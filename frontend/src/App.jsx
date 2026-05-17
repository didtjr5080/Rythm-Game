import { useEffect, useMemo, useState } from "react";
import {
  analyzeFile,
  generateNotes,
  getAudioUrl,
  getCsvDownloadUrl,
  getJsonDownloadUrl,
  listSavedItems,
  loadAnalysis,
  loadChart,
  uploadFile
} from "./api.js";
import UploadPanel from "./components/UploadPanel.jsx";
import AnalysisPanel from "./components/AnalysisPanel.jsx";
import WaveformViewer from "./components/WaveformViewer.jsx";
import NoteTimeline from "./components/NoteTimeline.jsx";
import ExportPanel from "./components/ExportPanel.jsx";
import GamePlayer from "./components/GamePlayer.jsx";

const DEFAULT_DIFFICULTY = "normal";

function App() {
  const [mode, setMode] = useState("editor");
  const [selectedFile, setSelectedFile] = useState(null);
  const [audioUrl, setAudioUrl] = useState("");
  const [fileId, setFileId] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [chart, setChart] = useState(null);
  const [result, setResult] = useState(null);
  const [difficulty, setDifficulty] = useState(DEFAULT_DIFFICULTY);
  const [lanes, setLanes] = useState(4);
  const [playMode, setPlayMode] = useState("lanes");
  const [isUploading, setIsUploading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isLoadingSaved, setIsLoadingSaved] = useState(false);
  const [savedItems, setSavedItems] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!selectedFile) {
      setAudioUrl("");
      return;
    }
    const url = URL.createObjectURL(selectedFile);
    setAudioUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [selectedFile]);

  const noteCount = chart?.notes?.length || 0;
  const backendAudioUrl = fileId ? getAudioUrl(fileId) : "";
  const previewAudioUrl = audioUrl || backendAudioUrl;

  const refreshSavedItems = async () => {
    try {
      const result = await listSavedItems();
      setSavedItems(result.items || []);
    } catch (err) {
      setError(err.message);
    }
  };

  useEffect(() => {
    refreshSavedItems();
  }, []);

  const downloadLinks = useMemo(() => {
    if (!fileId) {
      return { json: "", csv: "" };
    }
    return {
      json: getJsonDownloadUrl(fileId),
      csv: getCsvDownloadUrl(fileId)
    };
  }, [fileId]);

  const handleFileChange = (file) => {
    setSelectedFile(file);
    setFileId("");
    setAnalysis(null);
    setChart(null);
    setResult(null);
    setMode("editor");
    setError("");
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError("Please select an audio file first.");
      return;
    }
    setIsUploading(true);
    setError("");
    try {
      const result = await uploadFile(selectedFile);
      setFileId(result.file_id);
      refreshSavedItems();
    } catch (err) {
      setError(err.message);
    } finally {
      setIsUploading(false);
    }
  };

  const handleAnalyze = async () => {
    if (!fileId) {
      setError("Please upload the audio before analyzing.");
      return;
    }
    setIsAnalyzing(true);
    setError("");
    try {
      const result = await analyzeFile(fileId);
      setAnalysis(result);
      refreshSavedItems();
    } catch (err) {
      setError(err.message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleGenerate = async () => {
    if (!analysis) {
      setError("Please run analysis before generating notes.");
      return;
    }
    setIsGenerating(true);
    setError("");
    try {
      const result = await generateNotes(fileId, difficulty, Number(lanes), playMode);
      setChart(result);
      refreshSavedItems();
    } catch (err) {
      setError(err.message);
    } finally {
      setIsGenerating(false);
    }
  };

  const handlePlay = () => {
    if (!chart || !fileId) {
      setError("Please generate notes before starting the game.");
      return;
    }
    setError("");
    setResult(null);
    setMode("game");
  };

  const handleLoadSaved = async (targetFileId) => {
    if (!targetFileId) {
      return;
    }
    setIsLoadingSaved(true);
    setError("");
    try {
      const [loadedAnalysis, loadedChart] = await Promise.all([
        loadAnalysis(targetFileId).catch(() => null),
        loadChart(targetFileId).catch(() => null)
      ]);
      setSelectedFile(null);
      setAudioUrl("");
      setFileId(targetFileId);
      setAnalysis(loadedAnalysis);
      setChart(loadedChart);
      setResult(null);
      setMode("editor");
      if (loadedChart?.difficulty) {
        setDifficulty(loadedChart.difficulty);
      }
      if (loadedChart?.lanes) {
        setLanes(loadedChart.lanes);
      }
      if (loadedChart?.play_mode) {
        setPlayMode(loadedChart.play_mode);
      }
      if (!loadedAnalysis && !loadedChart) {
        setError("No saved analysis or chart found for this item.");
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoadingSaved(false);
    }
  };

  if (mode === "game") {
    return (
      <GamePlayer
        fileId={fileId}
        audioUrl={backendAudioUrl}
        chart={chart}
        onBack={() => setMode("editor")}
        onFinish={(gameResult) => {
          setResult(gameResult);
          setMode("result");
        }}
      />
    );
  }

  if (mode === "result") {
    return (
      <div className="result-screen">
        <div className="result-card">
          <h2>Result</h2>
          <div className="analysis-list">
            <div>
              <strong>Score:</strong> {result?.score ?? 0}
            </div>
            <div>
              <strong>Accuracy:</strong> {result?.accuracy?.toFixed(2) ?? "0.00"}%
            </div>
            <div>
              <strong>Max Combo:</strong> {result?.maxCombo ?? 0}
            </div>
            <div>
              <strong>Perfect:</strong> {result?.perfect ?? 0}
            </div>
            <div>
              <strong>Great:</strong> {result?.great ?? 0}
            </div>
            <div>
              <strong>Good:</strong> {result?.good ?? 0}
            </div>
            <div>
              <strong>Miss:</strong> {result?.miss ?? 0}
            </div>
          </div>
          <div className="button-row">
            <button className="primary" onClick={() => setMode("game")}>
              Play Again
            </button>
            <button className="ghost" onClick={() => setMode("editor")}>
              Back to Editor
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="hero">
        <div>
          <p className="eyebrow">Rhythm Note Generator</p>
          <h1>Audio to playable rhythm charts in minutes.</h1>
          <p className="subtitle">
            Upload a song, extract beats and onsets, then preview lanes and export
            JSON/CSV for your rhythm game prototype.
          </p>
        </div>
      </header>

      <main className="layout">
        <section className="card left">
          <UploadPanel
            onFileChange={handleFileChange}
            onUpload={handleUpload}
            selectedFile={selectedFile}
            uploading={isUploading}
            fileId={fileId}
          />

          <div className="saved-panel">
            <div className="panel-heading">
              <h2>Saved Analyses</h2>
              <button className="ghost small" onClick={refreshSavedItems} disabled={isLoadingSaved}>
                Refresh
              </button>
            </div>
            {savedItems.length === 0 ? (
              <p className="muted">No saved analyses yet.</p>
            ) : (
              <div className="saved-list">
                {savedItems.map((item) => (
                  <button
                    key={item.file_id}
                    className="saved-item"
                    onClick={() => handleLoadSaved(item.file_id)}
                    disabled={isLoadingSaved || (!item.has_analysis && !item.has_chart)}
                  >
                    <strong>{item.title || item.file_id}</strong>
                    <span>
                      {item.has_chart ? `${item.play_mode || "lanes"} / ${item.difficulty || "-"} / ${item.notes || 0} notes` : "analysis only"}
                    </span>
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="control-group">
            <label>
              Play Mode
              <select value={playMode} onChange={(event) => setPlayMode(event.target.value)}>
                <option value="lanes">Lane Keys</option>
                <option value="beat">Beat Only</option>
              </select>
            </label>

            <label>
              Difficulty
              <select value={difficulty} onChange={(event) => setDifficulty(event.target.value)}>
                <option value="easy">Easy</option>
                <option value="normal">Normal</option>
                <option value="hard">Hard</option>
                <option value="expert">Expert</option>
              </select>
            </label>

            <label>
              Lanes
              <select
                value={lanes}
                onChange={(event) => setLanes(event.target.value)}
                disabled={playMode === "beat"}
              >
                <option value={4}>4</option>
                <option value={5}>5</option>
                <option value={6}>6</option>
              </select>
            </label>
          </div>

          <div className="button-row">
            <button className="primary" onClick={handleAnalyze} disabled={isAnalyzing}>
              {isAnalyzing ? "Analyzing..." : "Run Analysis"}
            </button>
            <button className="ghost" onClick={handleGenerate} disabled={isGenerating}>
              {isGenerating ? "Generating..." : "Generate Notes"}
            </button>
            <button className="primary" onClick={handlePlay} disabled={!chart}>
              Play Game
            </button>
          </div>

          {error && <div className="error">{error}</div>}

          <AnalysisPanel analysis={analysis} noteCount={noteCount} />
        </section>

        <section className="center">
          <div className="card">
            <div className="audio-row">
              <div>
                <h2>Waveform Preview</h2>
                <p className="muted">Beats and notes are marked as guides.</p>
              </div>
              {previewAudioUrl ? <audio controls src={previewAudioUrl} /> : <span className="muted">No audio</span>}
            </div>
            <WaveformViewer
              audioUrl={previewAudioUrl}
              beats={analysis?.beats || []}
              notes={chart?.notes || []}
              duration={analysis?.duration || 0}
            />
          </div>

          <div className="card">
            <h2>Note Timeline</h2>
            <NoteTimeline
              notes={chart?.notes || []}
              lanes={chart?.lanes || lanes}
              duration={analysis?.duration || 0}
              playMode={chart?.play_mode || playMode}
            />
          </div>
        </section>

        <section className="card right">
          <AnalysisPanel analysis={analysis} noteCount={noteCount} compact />
          <ExportPanel
            jsonUrl={downloadLinks.json}
            csvUrl={downloadLinks.csv}
            disabled={!chart}
          />
        </section>
      </main>
    </div>
  );
}

export default App;
