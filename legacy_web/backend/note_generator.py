import random
import statistics


DIFFICULTY_CONFIG = {
    "easy": {
        "min_interval": 0.28,
        "subdivisions": (1, 2),
        "allow_trill": False,
        "allow_stairs": False,
        "allow_streams": False,
        "allow_jacks": False,
        "max_chord": 2,
        "ex_tap_threshold": 0.7,
        "sustain_min": 0.7,
    },
    "normal": {
        "min_interval": 0.2,
        "subdivisions": (1, 2),
        "allow_trill": True,
        "allow_stairs": True,
        "allow_streams": False,
        "allow_jacks": False,
        "max_chord": 2,
        "ex_tap_threshold": 0.65,
        "sustain_min": 0.6,
    },
    "hard": {
        "min_interval": 0.14,
        "subdivisions": (1, 2, 4),
        "allow_trill": True,
        "allow_stairs": True,
        "allow_streams": True,
        "allow_jacks": True,
        "max_chord": 3,
        "ex_tap_threshold": 0.6,
        "sustain_min": 0.5,
    },
    "expert": {
        "min_interval": 0.1,
        "subdivisions": (1, 2, 4),
        "allow_trill": True,
        "allow_stairs": True,
        "allow_streams": True,
        "allow_jacks": True,
        "max_chord": 4,
        "ex_tap_threshold": 0.55,
        "sustain_min": 0.45,
    },
}

PATTERNS = [
    [0, 1, 2, 3],
    [3, 2, 1, 0],
    [0, 2, 1, 3],
    [1, 2, 3, 2],
]

# Future expansion points:
# - Hold scoring ticks
# - Section detection
# - Downbeat detection
# - Manual note editing
# - Unity/Godot export
# - osu!mania format export


def _median_diff(values):
    if len(values) < 2:
        return 0.0
    diffs = [b - a for a, b in zip(values, values[1:])]
    return statistics.median(diffs) if diffs else 0.0


def _normalize_strengths(strengths):
    if not strengths:
        return []
    max_val = max(strengths) or 1.0
    return [min(s / max_val, 1.0) for s in strengths]


def _percentile(values, percentile):
    if not values:
        return 0.0
    ordered = sorted(values)
    index = int(len(ordered) * percentile)
    index = min(max(index, 0), len(ordered) - 1)
    return ordered[index]


def _find_sustain_segments(energy_times, energy, sustain_min, onset_times, onset_strengths):
    if not energy_times or not energy:
        return []
    threshold = _percentile(energy, 0.6)
    deltas = [b - a for a, b in zip(energy_times, energy_times[1:])]
    time_step = statistics.median(deltas) if deltas else 0.02
    segments = []
    start = None
    last_time = None
    for t, value in zip(energy_times, energy):
        if value >= threshold:
            if start is None:
                start = t
            last_time = t
        else:
            if start is not None and last_time is not None:
                if last_time - start >= sustain_min:
                    segments.append((start, last_time + time_step))
            start = None
            last_time = None
    if start is not None and last_time is not None and last_time - start >= sustain_min:
        segments.append((start, last_time + time_step))

    filtered = []
    for start, end in segments:
        onset_count = sum(1 for t in onset_times if start <= t <= end)
        if onset_count <= 2:
            filtered.append((start, end))
    return filtered


def _group_onsets_by_bar(beat_times, onset_events):
    bars = []
    if len(beat_times) < 2:
        return bars
    beats_per_bar = 4
    for i in range(0, len(beat_times) - 1, beats_per_bar):
        start = beat_times[i]
        end_index = min(i + beats_per_bar, len(beat_times) - 1)
        end = beat_times[end_index]
        bar_onsets = [event for event in onset_events if start <= event[0] < end]
        bars.append((start, end, bar_onsets, i))
    return bars


def _lane_candidates(lanes, count, avoid=None):
    pool = list(range(lanes))
    if avoid in pool and len(pool) > 1:
        pool.remove(avoid)
    random.shuffle(pool)
    return pool[:count]


def _is_in_segments(time_value, segments):
    return any(start <= time_value <= end for start, end in segments)


def generate_notes(analysis: dict, difficulty: str = "normal", lanes: int = 4) -> dict:
    if difficulty not in DIFFICULTY_CONFIG:
        raise ValueError("Invalid difficulty. Choose easy, normal, hard, or expert.")
    if lanes < 1:
        raise ValueError("Lanes must be at least 1.")

    config = DIFFICULTY_CONFIG[difficulty]
    beats = [float(t) for t in analysis.get("beats", [])]
    onsets = [float(t) for t in analysis.get("onsets", [])]
    onset_strengths = _normalize_strengths(analysis.get("onset_strengths", []))
    energy_times = analysis.get("energy_times", [])
    energy = analysis.get("energy", [])

    if not beats:
        return {
            "file_id": analysis.get("file_id"),
            "bpm": float(analysis.get("bpm", 0.0)),
            "difficulty": difficulty,
            "lanes": lanes,
            "notes": [],
        }

    onset_events = list(zip(onsets, onset_strengths + [0.0] * (len(onsets) - len(onset_strengths))))
    strength_values = [s for _, s in onset_events] or [0.0]
    strong_threshold = _percentile(strength_values, 0.75)
    peak_threshold = _percentile(strength_values, 0.9)

    sustain_segments = _find_sustain_segments(
        energy_times,
        energy,
        config["sustain_min"],
        onsets,
        strength_values,
    )

    beat_interval = 60.0 / analysis.get("bpm", 120.0) if analysis.get("bpm", 0.0) else _median_diff(beats)
    beat_interval = beat_interval or 0.5

    notes = []
    last_lane_end = {lane: -1.0 for lane in range(lanes)}
    last_global_time = -1.0
    last_lane = 0
    pattern_index = 0

    def can_place(time_value, lane, length=0.0, allow_same_time=False):
        nonlocal last_global_time
        lane_end = last_lane_end.get(lane, -1.0)
        if time_value < lane_end + config["min_interval"]:
            return False
        if time_value < last_global_time + config["min_interval"]:
            if not allow_same_time or abs(time_value - last_global_time) > 1e-3:
                return False
        if _is_in_segments(time_value, sustain_segments):
            return False
        return True

    def add_note(time_value, lane, note_type, length=0.0, allow_same_time=False):
        nonlocal last_global_time, last_lane
        if not can_place(time_value, lane, length, allow_same_time):
            return False
        notes.append(
            {
                "time": round(time_value, 3),
                "lane": lane,
                "type": note_type,
                "length": round(max(length, 0.0), 3),
            }
        )
        last_lane_end[lane] = time_value + max(length, 0.0)
        last_global_time = max(last_global_time, time_value)
        last_lane = lane
        return True

    def pick_note_type(time_value, strength):
        if strength >= config["ex_tap_threshold"]:
            return "ex_tap"
        return "tap"

    def place_chord(time_value, strength):
        chord_size = min(config["max_chord"], lanes)
        lanes_to_use = _lane_candidates(lanes, chord_size, avoid=last_lane)
        note_type = pick_note_type(time_value, strength)
        placed = False
        for lane in lanes_to_use:
            placed = add_note(time_value, lane, note_type, allow_same_time=True) or placed
        return placed

    def place_trill(start_time, interval, hits, lanes_pair, strength):
        lane_a, lane_b = lanes_pair
        note_type = pick_note_type(start_time, strength)
        for step in range(hits):
            lane = lane_a if step % 2 == 0 else lane_b
            add_note(start_time + step * interval, lane, note_type)

    def place_stairs(start_time, interval, direction, strength):
        pattern = list(range(lanes)) if direction > 0 else list(reversed(range(lanes)))
        note_type = pick_note_type(start_time, strength)
        for step, lane in enumerate(pattern):
            add_note(start_time + step * interval, lane, note_type)

    def place_stream(start_time, interval, hits, strength):
        pattern = PATTERNS[pattern_index % len(PATTERNS)]
        note_type = pick_note_type(start_time, strength)
        for step in range(hits):
            lane = pattern[step % len(pattern)] % lanes
            add_note(start_time + step * interval, lane, note_type)

    def place_jack(start_time, interval, hits, lane, strength):
        note_type = pick_note_type(start_time, strength)
        for step in range(hits):
            add_note(start_time + step * interval, lane, note_type)

    # Sustain notes first
    for start, end in sustain_segments:
        length = max(end - start, 0.0)
        if length <= 0:
            continue
        lane = _lane_candidates(lanes, 1, avoid=last_lane)[0]
        note_type = "hold" if random.random() < 0.6 else "slide"
        add_note(start, lane, note_type, length=length)

    bars = _group_onsets_by_bar(beats, onset_events)
    for bar_start, bar_end, bar_onsets, beat_index in bars:
        if bar_end <= bar_start:
            continue
        onset_count = len(bar_onsets)
        strength_mean = statistics.mean([s for _, s in bar_onsets]) if bar_onsets else 0.0
        intensity = "low"
        if onset_count >= 7 or strength_mean >= peak_threshold:
            intensity = "peak"
        elif onset_count >= 5 or strength_mean >= strong_threshold:
            intensity = "high"
        elif onset_count >= 3 or strength_mean >= strong_threshold * 0.8:
            intensity = "mid"

        downbeat_time = bar_start
        downbeat_strength = max([s for t, s in bar_onsets if abs(t - downbeat_time) <= 0.08] or [0.0])
        if downbeat_strength >= strong_threshold:
            place_chord(downbeat_time, downbeat_strength)

        beat_steps = [bar_start + beat_interval * i for i in range(4)]
        if difficulty == "easy":
            for t in beat_steps:
                strength = max([s for ot, s in bar_onsets if abs(ot - t) <= 0.06] or [0.0])
                add_note(t, _lane_candidates(lanes, 1, avoid=last_lane)[0], pick_note_type(t, strength))
            for t in beat_steps[::2]:
                strength = max([s for ot, s in bar_onsets if abs(ot - t) <= 0.06] or [0.0])
                add_note(t + beat_interval / 2, _lane_candidates(lanes, 1, avoid=last_lane)[0], pick_note_type(t, strength))
            continue

        if intensity in {"high", "peak"} and config["allow_streams"]:
            interval = beat_interval / 4
            hits = 16
            place_stream(bar_start, interval, hits, strength_mean)
            pattern_index += 1

            if config["allow_jacks"] and intensity == "peak":
                jack_lane = _lane_candidates(lanes, 1, avoid=last_lane)[0]
                place_jack(bar_start + interval * 8, interval, 4, jack_lane, strength_mean)
        elif intensity == "mid" and config["allow_stairs"]:
            interval = beat_interval / (2 if difficulty == "normal" else 4)
            direction = 1 if random.random() > 0.5 else -1
            place_stairs(bar_start, interval, direction, strength_mean)
        elif config["allow_trill"] and intensity in {"mid", "high"}:
            interval = beat_interval / (2 if difficulty == "normal" else 4)
            lanes_pair = _lane_candidates(lanes, 2, avoid=last_lane)
            place_trill(bar_start, interval, 6 if difficulty == "normal" else 8, lanes_pair, strength_mean)
        else:
            for t in beat_steps:
                strength = max([s for ot, s in bar_onsets if abs(ot - t) <= 0.06] or [0.0])
                add_note(t, _lane_candidates(lanes, 1, avoid=last_lane)[0], pick_note_type(t, strength))

    notes.sort(key=lambda item: item["time"])

    return {
        "file_id": analysis.get("file_id"),
        "bpm": float(analysis.get("bpm", 0.0)),
        "difficulty": difficulty,
        "lanes": lanes,
        "notes": notes,
    }


def generate_beat_notes(analysis: dict, difficulty: str = "normal") -> dict:
    if difficulty not in DIFFICULTY_CONFIG:
        raise ValueError("Invalid difficulty. Choose easy, normal, hard, or expert.")

    beats = [float(t) for t in analysis.get("beats", [])]
    onsets = [float(t) for t in analysis.get("onsets", [])]
    onset_strengths = _normalize_strengths(analysis.get("onset_strengths", []))
    bpm = float(analysis.get("bpm", 0.0))
    duration = float(analysis.get("duration", 0.0))
    if not beats and not onsets:
        return {
            "file_id": analysis.get("file_id"),
            "bpm": bpm,
            "difficulty": difficulty,
            "lanes": 1,
            "notes": [],
        }

    limit = duration if duration > 0 else (onsets[-1] if onsets else beats[-1])
    min_intervals = {
        "easy": 0.18,
        "normal": 0.11,
        "hard": 0.075,
        "expert": 0.055,
    }
    strength_percentiles = {
        "easy": 0.62,
        "normal": 0.34,
        "hard": 0.22,
        "expert": 0.12,
    }
    min_interval = min_intervals[difficulty]
    strength_threshold = _percentile(onset_strengths, strength_percentiles[difficulty])

    candidates = []
    if onsets:
        padded_strengths = onset_strengths + [0.0] * (len(onsets) - len(onset_strengths))
        for time_value, strength in zip(onsets, padded_strengths):
            if time_value < 0 or time_value > limit + 0.01:
                continue
            if strength >= strength_threshold:
                candidates.append((time_value, strength))

    # Beat tracker results are often nearly uniform, so they should not define the
    # whole chart. Use them only as pulse anchors when no detected onset is close.
    anchor_window = 0.07
    for beat_time in beats:
        if beat_time < 0 or beat_time > limit + 0.01:
            continue
        if any(abs(beat_time - onset_time) <= anchor_window for onset_time, _ in candidates):
            continue
        candidates.append((beat_time, strength_threshold * 0.95))

    candidates.sort(key=lambda item: item[0])
    notes = []
    for time_value, strength in candidates:
        if notes and time_value < notes[-1]["time"] + min_interval:
            if notes and strength > notes[-1].get("_strength", 0.0):
                notes[-1]["time"] = round(time_value, 3)
                notes[-1]["_strength"] = strength
            continue
        notes.append(
            {
                "time": round(time_value, 3),
                "lane": 0,
                "type": "tap",
                "length": 0.0,
                "_strength": strength,
            }
        )

    for note in notes:
        note.pop("_strength", None)

    return {
        "file_id": analysis.get("file_id"),
        "bpm": bpm,
        "difficulty": difficulty,
        "lanes": 1,
        "notes": notes,
    }
