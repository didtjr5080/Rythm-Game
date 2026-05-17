const API_BASE = "http://localhost:8000";

async function handleResponse(response) {
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    const message = data.detail || "Request failed.";
    throw new Error(message);
  }
  return response.json();
}

export async function uploadFile(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE}/api/upload`, {
    method: "POST",
    body: formData
  });

  return handleResponse(response);
}

export async function analyzeFile(fileId) {
  const response = await fetch(`${API_BASE}/api/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ file_id: fileId })
  });

  return handleResponse(response);
}

export async function generateNotes(fileId, difficulty, lanes, playMode = "lanes") {
  const response = await fetch(`${API_BASE}/api/generate-notes`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ file_id: fileId, difficulty, lanes, play_mode: playMode })
  });

  return handleResponse(response);
}

export async function listSavedItems() {
  const response = await fetch(`${API_BASE}/api/library`);
  return handleResponse(response);
}

export async function loadAnalysis(fileId) {
  const response = await fetch(`${API_BASE}/api/analysis/${fileId}`);
  return handleResponse(response);
}

export async function loadChart(fileId) {
  const response = await fetch(`${API_BASE}/api/chart/${fileId}`);
  return handleResponse(response);
}

export function getJsonDownloadUrl(fileId) {
  return `${API_BASE}/api/export/json/${fileId}`;
}

export function getCsvDownloadUrl(fileId) {
  return `${API_BASE}/api/export/csv/${fileId}`;
}

export function getAudioUrl(fileId) {
  return `${API_BASE}/api/audio/${fileId}`;
}
