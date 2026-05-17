function UploadPanel({ onFileChange, onUpload, selectedFile, uploading, fileId }) {
  const fileName = selectedFile ? selectedFile.name : "No file selected";

  const handleChange = (event) => {
    const file = event.target.files?.[0] || null;
    onFileChange(file);
  };

  return (
    <div className="upload-panel">
      <h2>Upload Audio</h2>
      <input type="file" accept=".mp3,.wav,.ogg" onChange={handleChange} />
      <span className="file-name">{fileName}</span>
      <button className="primary" onClick={onUpload} disabled={uploading}>
        {uploading ? "Uploading..." : "Upload"}
      </button>
      {fileId && <span className="file-name">File ID: {fileId}</span>}
    </div>
  );
}

export default UploadPanel;
