def calculate_game_metrics(score_state, logs: list[dict], input_delays_ms: list[float] | None = None) -> dict:
    emg_values = [float(row.get("emg_value") or 0.0) for row in logs]
    activation_count = sum(1 for row in logs if row.get("emg_activated"))
    avg_emg = sum(emg_values) / len(emg_values) if emg_values else 0.0
    max_emg = max(emg_values) if emg_values else 0.0
    input_delays_ms = input_delays_ms or []
    avg_input_delay_ms = sum(input_delays_ms) / len(input_delays_ms) if input_delays_ms else 0.0

    emg_drop_rate = 0.0
    if emg_values:
        segment = max(1, int(len(emg_values) * 0.3))
        front_avg = sum(emg_values[:segment]) / segment
        back_avg = sum(emg_values[-segment:]) / segment
        emg_drop_rate = 0.0 if front_avg == 0 else max(0.0, (front_avg - back_avg) / front_avg)

    metrics = score_state.as_dict()
    metrics.update(
        {
            "avg_emg": avg_emg,
            "max_emg": max_emg,
            "activation_count": activation_count,
            "avg_input_delay_ms": avg_input_delay_ms,
            "emg_drop_rate": emg_drop_rate,
        }
    )
    return metrics

