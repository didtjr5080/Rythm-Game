로컬 데이터 레이아웃

목적

런타임에서 사용되는 로컬 데이터 디렉터리를 설명한다.

확인된 사실

EXTRACTED: app/data/songs/는 사용자가 추가한 오디오 파일을 저장한다.
EXTRACTED: app/data/notes/는 생성된 노트 JSON을 저장한다.
EXTRACTED: app/data/settings.json은 설정 값을 저장한다.
EXTRACTED: app/data/sessions/는 세션 로그를 JSON과 CSV로 저장한다.
EXTRACTED: app/data/results/는 플레이 결과 요약을 JSON으로 저장한다.
EXTRACTED: 결과 요약에는 세션 JSON/CSV 경로 참조가 포함될 수 있다.
EXTRACTED: 이러한 런타임 데이터 경로는 .gitignore로 git 추적에서 제외된다.

관련 파일

[app/ui/start_screen.py](app/ui/start_screen.py)
[app/analytics/session_logger.py](app/analytics/session_logger.py)
[app/ui/result_screen.py](app/ui/result_screen.py)
[app/settings.py](app/settings.py)
[.gitignore](.gitignore)

흐름

런타임 데이터 -> app/data/* -> 버전 관리 제외

비고

런타임 데이터는 소스와 분리해 실수로 커밋되는 것을 방지한다.

TODO

분석 모듈이 추가 데이터 하위 폴더를 생성하는지 확인한다.
