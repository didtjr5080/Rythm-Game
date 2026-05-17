function AnalysisPanel({ analysis, noteCount, compact = false }) {
  const duration = analysis?.duration ? `${analysis.duration.toFixed(2)}s` : "-";
  const bpm = analysis?.bpm ? analysis.bpm.toFixed(1) : "-";
  const beats = analysis?.beats?.length ?? 0;
  const onsets = analysis?.onsets?.length ?? 0;

  return (
    <div>
      {!compact && <h2>Analysis</h2>}
      <div className="analysis-list">
        <div>
          <strong>BPM:</strong> {bpm}
        </div>
        <div>
          <strong>Duration:</strong> {duration}
        </div>
        <div>
          <strong>Beats:</strong> {beats}
        </div>
        <div>
          <strong>Onsets:</strong> {onsets}
        </div>
        <div>
          <strong>Notes:</strong> {noteCount}
        </div>
      </div>
    </div>
  );
}

export default AnalysisPanel;
