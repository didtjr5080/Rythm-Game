from typing import List, Literal

from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    file_id: str
    filename: str
    stored_path: str


class AnalyzeRequest(BaseModel):
    file_id: str


class AnalyzeResponse(BaseModel):
    file_id: str
    duration: float
    sample_rate: int
    bpm: float
    beats: List[float]
    onsets: List[float]
    onset_strengths: List[float]
    energy_times: List[float]
    energy: List[float]


class GenerateNotesRequest(BaseModel):
    file_id: str
    difficulty: str = Field(default="normal")
    lanes: int = Field(default=4, ge=1)
    play_mode: Literal["lanes", "beat"] = Field(default="lanes")


class Note(BaseModel):
    time: float
    lane: int
    type: Literal["tap", "ex_tap", "hold", "slide"]
    length: float = 0.0


class ChartResponse(BaseModel):
    version: str
    file_id: str
    title: str
    play_mode: Literal["lanes", "beat"] = "lanes"
    bpm: float
    offset: float
    difficulty: str
    lanes: int
    duration: float
    notes: List[Note]
