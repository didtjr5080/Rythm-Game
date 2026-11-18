def judge_note(note, input_state, current_time_ms, config, require_extension=False):
    if note.judged:
        return None

    timing_error = abs(note.hit_time_ms - current_time_ms)
    if current_time_ms < note.hit_time_ms:
        return None

    if current_time_ms > note.hit_time_ms + config.JUDGE_WINDOW_MS:
        note.judged = True
        note.result = "MISS"
        return "MISS"

    if (
        input_state.hand_visible
        and input_state.lane == note.lane
        and timing_error <= config.JUDGE_WINDOW_MS
        and (not require_extension or (input_state.emg_activated and input_state.emg_signal_fresh))
    ):
        note.judged = True
        note.result = "PERFECT" if timing_error <= config.PERFECT_WINDOW_MS else "GOOD"
        return note.result

    return None


def judge_emg_note(note, input_state, current_time_ms, config, triggered):
    if note.judged:
        return None
    result = None
    if note.holding:
        if (not input_state.emg_signal_fresh or current_time_ms - note.last_hold_time_ms > 250):
            result = 'MISS'
        else:
            note.last_hold_time_ms = current_time_ms
            if not input_state.emg_activated:
                if note.dropout_since_ms is None:
                    note.dropout_since_ms = current_time_ms
                if current_time_ms - note.dropout_since_ms > config.EMG_HOLD_DROPOUT_MS:
                    result = 'MISS'
            elif note.dropout_since_ms is not None and current_time_ms - note.dropout_since_ms > config.EMG_HOLD_DROPOUT_MS:
                result = 'MISS'
            else:
                note.dropout_since_ms = None
                if current_time_ms >= note.end_time_ms:
                    result = 'PERFECT' if note.start_error_ms <= config.EMG_PERFECT_WINDOW_MS else 'GOOD'
    elif current_time_ms > note.hit_time_ms + config.EMG_JUDGE_WINDOW_MS:
        result = 'MISS'
    elif input_state.emg_signal_fresh and triggered and abs(current_time_ms - note.hit_time_ms) <= config.EMG_JUDGE_WINDOW_MS:
        note.start_error_ms = abs(current_time_ms - note.hit_time_ms)
        if note.duration_ms:
            note.holding = True
            note.last_hold_time_ms = current_time_ms
        else:
            result = 'PERFECT' if note.start_error_ms <= config.EMG_PERFECT_WINDOW_MS else 'GOOD'
    if result:
        note.judged = True
        note.holding = False
        note.result = result
    return result

