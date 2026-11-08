import json
from pathlib import Path


DEFAULT_SETTINGS = {
    "language": "en",
    "window_mode": "windowed",
    "resolution": "1280x720",
    "show_game_hud": True,
    "show_judgement_text": True,
    "show_camera_debug": True,
    "camera_flip": True,
    "camera_enabled": True,
    "camera_index": 0,
    "camera_resolution": "1280x720",
    "music_volume": 0.85,
    "note_speed": 450,
    "judgement_line_y_ratio": 0.82,
    "emg_threshold": 400,
    "emg_input_mode": "serial",
    "emg_port": "auto",
    "emg_device_id": "",
    "emg_baudrate": 115200,
    "emg_signal": "envelope",
}

CAMERA_RESOLUTIONS = ("640x480", "1280x720", "1920x1080")

AVAILABLE_RESOLUTIONS = (
    "800x600",
    "960x540",
    "1024x576",
    "1024x768",
    "1152x648",
    "1152x864",
    "1280x720",
    "1280x768",
    "1280x800",
    "1280x960",
    "1280x1024",
    "1366x768",
    "1360x768",
    "1440x810",
    "1440x900",
    "1440x1080",
    "1600x900",
    "1600x1000",
    "1600x1200",
    "1680x945",
    "1680x1050",
    "1920x1080",
    "1920x1200",
    "1920x1440",
    "2048x1152",
    "2048x1536",
    "2560x1440",
    "2560x1600",
    "3840x2160",
)


def settings_path() -> Path:
    return Path(__file__).resolve().parent / "data" / "settings.json"


def load_settings() -> dict:
    path = settings_path()
    if not path.exists():
        return dict(DEFAULT_SETTINGS)
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except Exception:
        return dict(DEFAULT_SETTINGS)
    settings = dict(DEFAULT_SETTINGS)
    settings.update({key: data[key] for key in DEFAULT_SETTINGS if key in data})
    for key, choices, default in (("emg_input_mode", ("serial", "mock"), "serial"),
                                  ("emg_signal", ("envelope", "raw"), "envelope"),
                                  ("emg_baudrate", (9600, 57600, 115200), 115200)):
        if settings[key] not in choices: settings[key] = default
    for key, default in (("emg_port", "auto"), ("emg_device_id", "")):
        if not isinstance(settings[key], str) or len(settings[key])>256: settings[key] = default
    settings["camera_enabled"] = bool(settings["camera_enabled"])
    try:
        settings["camera_index"] = max(0, min(9, int(settings["camera_index"])))
    except (ValueError, TypeError):
        settings["camera_index"] = 0
    if settings["camera_resolution"] not in CAMERA_RESOLUTIONS:
        settings["camera_resolution"] = "1280x720"
    settings["language"] = settings["language"] if settings["language"] in {"en", "ko"} else "en"
    settings["window_mode"] = settings["window_mode"] if settings["window_mode"] in {"windowed", "borderless", "fullscreen"} else "windowed"
    settings["resolution"] = settings["resolution"] if settings["resolution"] in AVAILABLE_RESOLUTIONS else "1280x720"
    settings["music_volume"] = max(0.0, min(1.0, float(settings["music_volume"])))
    settings["note_speed"] = max(200, min(900, int(settings["note_speed"])))
    settings["judgement_line_y_ratio"] = max(0.55, min(0.92, float(settings["judgement_line_y_ratio"])))
    settings["emg_threshold"] = max(0, min(1000, int(settings["emg_threshold"])))
    settings["show_game_hud"] = bool(settings["show_game_hud"])
    settings["show_judgement_text"] = bool(settings["show_judgement_text"])
    settings["show_camera_debug"] = bool(settings["show_camera_debug"])
    settings["camera_flip"] = bool(settings["camera_flip"])
    return settings


def save_settings(settings: dict) -> dict:
    merged = dict(DEFAULT_SETTINGS)
    merged.update({key: settings[key] for key in DEFAULT_SETTINGS if key in settings})
    for key, choices, default in (("emg_input_mode", ("serial", "mock"), "serial"),
                                  ("emg_signal", ("envelope", "raw"), "envelope"),
                                  ("emg_baudrate", (9600, 57600, 115200), 115200)):
        if merged[key] not in choices: merged[key] = default
    for key, default in (("emg_port", "auto"), ("emg_device_id", "")):
        if not isinstance(merged[key], str) or len(merged[key])>256: merged[key] = default
    merged["camera_enabled"] = bool(merged["camera_enabled"])
    try:
        merged["camera_index"] = max(0, min(9, int(merged["camera_index"])))
    except (ValueError, TypeError):
        merged["camera_index"] = 0
    if merged["camera_resolution"] not in CAMERA_RESOLUTIONS:
        merged["camera_resolution"] = "1280x720"
    merged["language"] = merged["language"] if merged["language"] in {"en", "ko"} else "en"
    merged["window_mode"] = merged["window_mode"] if merged["window_mode"] in {"windowed", "borderless", "fullscreen"} else "windowed"
    merged["resolution"] = merged["resolution"] if merged["resolution"] in AVAILABLE_RESOLUTIONS else "1280x720"
    merged["music_volume"] = max(0.0, min(1.0, float(merged["music_volume"])))
    merged["note_speed"] = max(200, min(900, int(merged["note_speed"])))
    merged["judgement_line_y_ratio"] = max(0.55, min(0.92, float(merged["judgement_line_y_ratio"])))
    merged["emg_threshold"] = max(0, min(1000, int(merged["emg_threshold"])))
    merged["show_game_hud"] = bool(merged["show_game_hud"])
    merged["show_judgement_text"] = bool(merged["show_judgement_text"])
    merged["show_camera_debug"] = bool(merged["show_camera_debug"])
    merged["camera_flip"] = bool(merged["camera_flip"])
    path = settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(merged, handle, indent=2)
    return merged
