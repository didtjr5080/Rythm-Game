function ExportPanel({ jsonUrl, csvUrl, disabled }) {
  return (
    <div className="export-panel">
      <h2>Export</h2>
      <a href={disabled ? "#" : jsonUrl} onClick={(event) => disabled && event.preventDefault()}>
        <button className="primary" disabled={disabled}>
          Download JSON
        </button>
      </a>
      <a href={disabled ? "#" : csvUrl} onClick={(event) => disabled && event.preventDefault()}>
        <button className="ghost" disabled={disabled}>
          Download CSV
        </button>
      </a>
    </div>
  );
}

export default ExportPanel;
