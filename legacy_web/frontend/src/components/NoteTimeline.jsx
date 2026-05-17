function NoteTimeline({ notes, lanes, duration, playMode = "lanes" }) {
  if (!duration) {
    return <p className="muted">Run analysis to see timeline.</p>;
  }

  const timelineWidth = Math.max(duration * 120, 600);
  const pixelsPerSecond = timelineWidth / duration;

  const visibleLanes = playMode === "beat" ? 1 : lanes;
  const laneRows = Array.from({ length: visibleLanes }, (_, lane) => {
    const laneNotes = notes.filter((note) => note.lane === lane);
    return (
      <div key={`lane-${lane}`} className="timeline-lane">
        {laneNotes.map((note, index) => {
          const length = note.length || 0;
          const width = Math.max(10, length * pixelsPerSecond);
          return (
          <span
            key={`note-${lane}-${index}`}
            className={`timeline-note ${note.type || "tap"}`}
            style={{
              left: `${(note.time / duration) * timelineWidth}px`,
              width: `${width}px`
            }}
            title={`Lane ${note.lane} @ ${note.time}s`}
          />
          );
        })}
      </div>
    );
  });

  return (
    <div className="timeline">
      <div className="timeline-track" style={{ width: `${timelineWidth}px` }}>
        {laneRows}
      </div>
    </div>
  );
}

export default NoteTimeline;
