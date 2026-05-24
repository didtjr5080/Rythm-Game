시스템 개요

목적

PyQt6 리듬 게임의 상위 구조와 주요 서브시스템 연결을 설명한다.

확인된 사실

EXTRACTED: 애플리케이션은 app/main.py의 PyQt6 엔트리 포인트로 실행된다.
EXTRACTED: MainWindow는 Start, Settings, Calibration, Game, Result 화면을 전환한다.
EXTRACTED: 카메라가 활성화되면 MediaPipe 기반 손 추적으로 레인을 선택한다.
EXTRACTED: EMG 입력은 SerialEMGReader를 사용하며 시리얼 입력이 없으면 모의 입력으로 폴백한다.
EXTRACTED: 키보드 레인 폴백은 A/S/D 또는 Left/Down/Right를 사용하며, SPACE로 모의 EMG를 사용한다.
EXTRACTED: 음악과 노트는 app/data/songs/ 및 app/data/notes/에 저장된다.
EXTRACTED: 설정은 app/data/settings.json에 저장된다.
EXTRACTED: 게임 세션은 app/data/sessions/에 JSON과 CSV로 기록된다.
EXTRACTED: 결과 요약은 app/data/results/에 JSON 파일로 저장된다.
EXTRACTED: legacy_web/는 보존되어 있으며 오디오/노트 어댑터가 legacy backend 모듈을 참조한다.

관련 파일

[app/main.py](app/main.py)
[app/ui/main_window.py](app/ui/main_window.py)
[app/ui/game_widget.py](app/ui/game_widget.py)
[app/input/input_fusion.py](app/input/input_fusion.py)
[app/input/emg_reader.py](app/input/emg_reader.py)
[app/input/mock_emg_reader.py](app/input/mock_emg_reader.py)
[app/input/mediapipe_tracker.py](app/input/mediapipe_tracker.py)
[app/audio/note_generator_adapter.py](app/audio/note_generator_adapter.py)
[app/audio/beat_analyzer.py](app/audio/beat_analyzer.py)
[app/analytics/session_logger.py](app/analytics/session_logger.py)
[app/analytics/game_metrics.py](app/analytics/game_metrics.py)
[app/ui/result_screen.py](app/ui/result_screen.py)
[app/settings.py](app/settings.py)
[README.md](README.md)

흐름

앱 실행 -> StartScreen -> 노래 선택 또는 추가 -> 노트 생성 또는 로드 -> GameWidget
GameWidget -> InputFusion (카메라 + EMG) -> RhythmGameEngine -> Judge -> Score -> ResultScreen

비고

카메라나 시리얼 입력이 없어도 폴백 입력으로 게임이 계속 진행된다.

TODO

CalibrationScreen의 선택적 보정 흐름 세부 사항을 확인한다.
