import json
import logging
import mimetypes
import os
import shutil
import uuid

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from audio_analyzer import analyze_audio
from export_utils import save_analysis_json, save_chart_csv, save_chart_json
from note_generator import generate_beat_notes, generate_notes
from schemas import AnalyzeRequest, AnalyzeResponse, ChartResponse, GenerateNotesRequest, UploadResponse

BASE_DIR = os.path.dirname(__file__)
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

ALLOWED_EXTENSIONS = {".mp3", ".wav", ".ogg"}

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

FILE_INDEX = {}
# TODO: Persist file_id -> path mapping (e.g., SQLite) for server restarts.
ANALYSIS_CACHE = {}
CHART_CACHE = {}

app = FastAPI(title="Rhythm Note Generator API")
logger = logging.getLogger("rhythm_note_generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _analysis_path(file_id: str) -> str:
    return os.path.join(OUTPUT_DIR, f"{file_id}_analysis.json")


def _chart_json_path(file_id: str) -> str:
    return os.path.join(OUTPUT_DIR, f"{file_id}_chart.json")


def _chart_csv_path(file_id: str) -> str:
    return os.path.join(OUTPUT_DIR, f"{file_id}_chart.csv")


def _scan_uploads():
    FILE_INDEX.clear()
    for filename in os.listdir(UPLOAD_DIR):
        stored_path = os.path.join(UPLOAD_DIR, filename)
        if not os.path.isfile(stored_path):
            continue
        file_id, sep, original_name = filename.partition("_")
        if not sep or not file_id:
            continue
        _, ext = os.path.splitext(original_name)
        if ext.lower() not in ALLOWED_EXTENSIONS:
            continue
        FILE_INDEX[file_id] = {"filename": original_name, "stored_path": stored_path}


def _load_json_file(path: str):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _load_analysis(file_id: str):
    if file_id in ANALYSIS_CACHE:
        return ANALYSIS_CACHE[file_id]
    path = _analysis_path(file_id)
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="Analysis not found.")
    analysis = _load_json_file(path)
    ANALYSIS_CACHE[file_id] = analysis
    return analysis


def _load_chart(file_id: str):
    if file_id in CHART_CACHE:
        return CHART_CACHE[file_id]["chart"]
    path = _chart_json_path(file_id)
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="Chart not found.")
    chart = _load_json_file(path)
    CHART_CACHE[file_id] = {
        "chart": chart,
        "json_path": path,
        "csv_path": _chart_csv_path(file_id),
    }
    return chart


_scan_uploads()


@app.get("/")
def health_check():
    return {"status": "ok", "message": "Rhythm Note Generator API is running"}


@app.post("/api/upload", response_model=UploadResponse)
async def upload_audio(file: UploadFile = File(...)):
    if file is None:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    _, ext = os.path.splitext(file.filename)
    ext = ext.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type. Use mp3, wav, or ogg.")

    file_id = uuid.uuid4().hex
    safe_name = f"{file_id}_{os.path.basename(file.filename)}"
    stored_path = os.path.join(UPLOAD_DIR, safe_name)

    try:
        with open(stored_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to save uploaded file.") from exc

    FILE_INDEX[file_id] = {"filename": file.filename, "stored_path": stored_path}

    return UploadResponse(
        file_id=file_id,
        filename=file.filename,
        stored_path=f"uploads/{safe_name}",
    )


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze_audio_file(payload: AnalyzeRequest):
    file_id = payload.file_id
    if file_id not in FILE_INDEX:
        raise HTTPException(status_code=404, detail="File ID not found. Please upload first.")

    try:
        analysis = analyze_audio(FILE_INDEX[file_id]["stored_path"])
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Uploaded file not found on server.") from exc
    except Exception as exc:
        logger.exception("Audio analysis failed for file_id=%s", file_id)
        raise HTTPException(
            status_code=400,
            detail=f"Audio analysis failed: {exc}",
        ) from exc

    analysis["file_id"] = file_id
    ANALYSIS_CACHE[file_id] = analysis
    save_analysis_json(file_id, analysis)

    return analysis


@app.post("/api/generate-notes", response_model=ChartResponse)
def generate_notes_for_file(payload: GenerateNotesRequest):
    file_id = payload.file_id
    if file_id not in FILE_INDEX:
        raise HTTPException(status_code=404, detail="File ID not found. Please upload first.")
    try:
        analysis = _load_analysis(file_id)
    except HTTPException as exc:
        raise HTTPException(status_code=400, detail="Please analyze the file before generating notes.") from exc

    try:
        if payload.play_mode == "beat":
            chart_core = generate_beat_notes(analysis, payload.difficulty)
        else:
            chart_core = generate_notes(analysis, payload.difficulty, payload.lanes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    title = os.path.splitext(FILE_INDEX[file_id]["filename"])[0]
    chart = {
        "version": "0.1.0",
        "file_id": file_id,
        "title": title,
        "play_mode": payload.play_mode,
        "bpm": chart_core["bpm"],
        "offset": 0.0,
        "difficulty": chart_core["difficulty"],
        "lanes": chart_core["lanes"],
        "duration": analysis.get("duration", 0.0),
        "notes": chart_core["notes"],
    }

    try:
        json_path = save_chart_json(file_id, chart)
        csv_path = save_chart_csv(file_id, chart)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to export chart files.") from exc

    CHART_CACHE[file_id] = {"chart": chart, "json_path": json_path, "csv_path": csv_path}

    return chart


@app.get("/api/export/json/{file_id}")
def export_json(file_id: str):
    _load_chart(file_id)
    json_path = CHART_CACHE[file_id]["json_path"]
    if not os.path.isfile(json_path):
        raise HTTPException(status_code=404, detail="Exported JSON file not found.")

    return FileResponse(json_path, filename=os.path.basename(json_path), media_type="application/json")


@app.get("/api/export/csv/{file_id}")
def export_csv(file_id: str):
    _load_chart(file_id)
    csv_path = CHART_CACHE[file_id]["csv_path"]
    if not os.path.isfile(csv_path):
        raise HTTPException(status_code=404, detail="Exported CSV file not found.")

    return FileResponse(csv_path, filename=os.path.basename(csv_path), media_type="text/csv")


@app.get("/api/library")
def list_saved_items():
    _scan_uploads()
    items = []
    file_ids = set(FILE_INDEX.keys())
    for filename in os.listdir(OUTPUT_DIR):
        if filename.endswith("_analysis.json"):
            file_ids.add(filename[: -len("_analysis.json")])
        elif filename.endswith("_chart.json"):
            file_ids.add(filename[: -len("_chart.json")])

    for file_id in sorted(file_ids):
        file_info = FILE_INDEX.get(file_id, {})
        chart_path = _chart_json_path(file_id)
        analysis_path = _analysis_path(file_id)
        title = os.path.splitext(file_info.get("filename", file_id))[0]
        chart_summary = {}
        if os.path.isfile(chart_path):
            try:
                chart = _load_json_file(chart_path)
                title = chart.get("title") or title
                chart_summary = {
                    "play_mode": chart.get("play_mode", "lanes"),
                    "difficulty": chart.get("difficulty", ""),
                    "notes": len(chart.get("notes", [])),
                }
            except Exception:
                chart_summary = {}
        items.append(
            {
                "file_id": file_id,
                "filename": file_info.get("filename", ""),
                "title": title,
                "has_audio": file_id in FILE_INDEX,
                "has_analysis": os.path.isfile(analysis_path),
                "has_chart": os.path.isfile(chart_path),
                **chart_summary,
            }
        )
    return {"items": items}


@app.get("/api/analysis/{file_id}", response_model=AnalyzeResponse)
def get_analysis(file_id: str):
    return _load_analysis(file_id)


@app.get("/api/chart/{file_id}", response_model=ChartResponse)
def get_chart(file_id: str):
    return _load_chart(file_id)


@app.get("/api/audio/{file_id}")
def get_audio(file_id: str):
    if file_id not in FILE_INDEX:
        raise HTTPException(status_code=404, detail="File ID not found. Please upload first.")

    stored_path = FILE_INDEX[file_id]["stored_path"]
    if not os.path.isfile(stored_path):
        raise HTTPException(status_code=404, detail="Uploaded file not found on server.")

    media_type, _ = mimetypes.guess_type(stored_path)
    return FileResponse(
        stored_path,
        filename=os.path.basename(stored_path),
        media_type=media_type or "application/octet-stream",
    )
