아키텍처 결정 사항

목적

현재 구현에서 확인되는 주요 설계 선택을 기록한다.

확인된 사실

EXTRACTED: 게임은 PyQt6 데스크톱 애플리케이션으로 구현되었다.
EXTRACTED: legacy_web/는 보존되며 오디오/노트 생성 어댑터가 이를 참조한다.
EXTRACTED: 하드웨어 없이 테스트 가능한 모의 EMG 입력을 지원한다.
EXTRACTED: 손 추적이 불가능할 때 키보드 레인 폴백을 지원한다.
EXTRACTED: 음악과 노트는 app/data/에 로컬로 저장된다.
EXTRACTED: 이번 작업은 게임 변경 없이 문서화와 시각화만 추가한다.

관련 파일

[README.md](README.md)
[app/audio/note_generator_adapter.py](app/audio/note_generator_adapter.py)
[app/audio/beat_analyzer.py](app/audio/beat_analyzer.py)
[app/ui/game_widget.py](app/ui/game_widget.py)

흐름

설계 결정 문서화 -> 코드와 정렬 -> 기능 변경 방지

비고

이 결정 사항은 현재 구현을 기준으로 하며 아키텍처가 바뀌면 업데이트해야 한다.

TODO

프로젝트 논의에 보류 중인 리팩터 계획이 있는지 확인한다.
