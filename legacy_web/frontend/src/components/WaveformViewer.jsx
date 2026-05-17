import { useEffect, useRef } from "react";
import WaveSurfer from "wavesurfer.js";

function WaveformViewer({ audioUrl, beats, notes, duration }) {
  const containerRef = useRef(null);
  const waveRef = useRef(null);

  useEffect(() => {
    if (!audioUrl || !containerRef.current) {
      return;
    }

    waveRef.current = WaveSurfer.create({
      container: containerRef.current,
      waveColor: "rgba(148, 163, 184, 0.4)",
      progressColor: "#38bdf8",
      cursorColor: "#38bdf8",
      height: 160,
      barWidth: 2
    });

    waveRef.current.load(audioUrl);

    return () => {
      if (waveRef.current) {
        waveRef.current.destroy();
        waveRef.current = null;
      }
    };
  }, [audioUrl]);

  const renderMarkers = (items, className) => {
    if (!duration || !items.length) {
      return null;
    }
    return items.map((time, index) => (
      <span
        key={`${className}-${index}`}
        className={`waveform-line ${className}`}
        style={{ left: `${(time / duration) * 100}%` }}
      />
    ));
  };

  return (
    <div className="waveform-shell">
      <div ref={containerRef} />
      <div className="waveform-overlay">
        {renderMarkers(beats.slice(0, 80), "")}
        {renderMarkers(notes.map((note) => note.time).slice(0, 80), "note")}
      </div>
    </div>
  );
}

export default WaveformViewer;
