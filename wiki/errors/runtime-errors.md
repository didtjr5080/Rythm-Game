런타임 오류

목적

발생 가능한 런타임 이슈와 원인을 정리한다.

확인된 사실

EXTRACTED: 오디오 파일이 없거나 디코딩이 실패하면 재생 오류가 보고된다.
EXTRACTED: settings.json이 손상되면 기본 설정으로 조용히 폴백한다.
INFERRED: 노트 JSON 손상은 게임 시작 시 로드 오류를 유발할 수 있다.
INFERRED: 누락된 음악 파일은 StartScreen 로그에 보고된다.
INFERRED: PyQt6 의존성이 누락되면 시작 오류가 발생할 수 있다.

관련 파일

[app/audio/audio_player.py](app/audio/audio_player.py)
[app/settings.py](app/settings.py)
[app/game/rhythm_game_engine.py](app/game/rhythm_game_engine.py)
[app/ui/start_screen.py](app/ui/start_screen.py)

흐름

앱 실행 -> 설정 로드 -> 노트 로드 -> 오디오 로드 -> 보고 또는 폴백

비고

코드는 주변 장치가 없을 때 크래시보다 폴백 동작을 우선한다.

TODO

UI 컴포넌트에 사용자용 오류 다이얼로그가 있는지 확인한다.
