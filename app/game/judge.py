def judge_note(note, input_state, current_time_ms, config):
    if note.judged:
        return None

    timing_error = abs(note.hit_time_ms - current_time_ms)
    if current_time_ms < note.hit_time_ms - config.JUDGE_WINDOW_MS:
        return None

    if current_time_ms > note.hit_time_ms + config.JUDGE_WINDOW_MS:
        note.judged = True
        note.result = "MISS"
        return "MISS"

    if (
        input_state.hand_visible
        and input_state.lane == note.lane
        and input_state.emg_activated
        and timing_error <= config.JUDGE_WINDOW_MS
    ):
        note.judged = True
        note.result = "PERFECT" if timing_error <= config.PERFECT_WINDOW_MS else "GOOD"
        return note.result

    return None

