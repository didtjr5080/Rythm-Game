저장된 음악 흐름

목적

사용자 추가 음악과 노트가 저장 및 로드되는 방식을 문서화한다.

확인된 사실

EXTRACTED: 추가된 음악은 타임스탬프가 포함된 이름으로 app/data/songs/에 복사된다.
EXTRACTED: 노트는 app/data/notes/에 _notes.json 접미사로 저장된다.
EXTRACTED: 선택한 곡에 저장된 노트가 있으면 자동으로 로드된다.

관련 파일

[app/ui/start_screen.py](app/ui/start_screen.py)
[app/audio/note_generator_adapter.py](app/audio/note_generator_adapter.py)
[README.md](README.md)

흐름

음악 추가 -> app/data/songs/ -> 노트 생성 -> app/data/notes/ -> 선택 로드 -> 게임 시작

비고

저장된 음악과 노트는 런타임 데이터이므로 git 추적에서 제외되어야 한다.

TODO

노트 파일 누락 시 사용자에게 어떻게 표시되는지 확인한다.
