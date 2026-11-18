"""One-lane sustained holds only, derived from the same song."""
import math
from app import config


def generate_emg_notes(pinch_notes, analysis=None):
    analysis = analysis or {}
    bpm = float(analysis.get('bpm') or 120)
    if not math.isfinite(bpm) or not 20 <= bpm <= 300:
        bpm = 120.
    beat_ms = 60000 / bpm
    duration = float(analysis.get('duration') or 0) * 1000
    if not math.isfinite(duration) or duration < 0:
        raise ValueError('Invalid song duration.')
    if not duration:
        duration = max(15000, max((int(n.get('hit_time_ms', float(n.get('time', 0)) * 1000))
                                   for n in pinch_notes), default=0) + 4000)
    beats = sorted(set(round(float(t) * 1000) for t in analysis.get('beats', [])
                       if math.isfinite(float(t)) and 2000 <= float(t) * 1000 < duration - 200))
    if not beats:
        beats = [round(i * beat_ms) for i in range(math.ceil(duration / beat_ms))
                 if 2000 <= i * beat_ms < duration - 200]
    notes = []
    next_time = 0
    for stamp in beats:
        if stamp < next_time:
            continue
        available = math.floor((duration - 200 - stamp) / beat_ms) * beat_ms
        hold_beats = max(math.ceil(1000 / beat_ms), min(4, math.floor(4000 / beat_ms)))
        planned = round(beat_ms * hold_beats)
        hold_ms = round(min(planned, available))
        if hold_ms < 1000:
            continue  # Never substitute a short tap near the end of the song.
        notes.append({'note_id': len(notes), 'lane': 0, 'hit_time_ms': stamp,
                      'duration_ms': hold_ms})
        next_time = stamp + hold_ms + max(config.MIN_NOTE_INTERVAL_MS, round(beat_ms * 2))
    return notes
