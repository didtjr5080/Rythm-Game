데이터 흐름

목적

음악 파일에서 노트와 게임 결과까지의 경로를 설명한다.

확인된 사실

EXTRACTED: 추가된 음악은 app/data/songs/에 저장된다.
EXTRACTED: 생성된 노트는 app/data/notes/에 _notes.json 접미사로 저장된다.
EXTRACTED: 선택한 곡에 저장된 노트가 있으면 자동으로 로드된다.
EXTRACTED: 게임 업데이트에서 레인 선택과 EMG 활성화를 판정에 사용한다.

관련 파일

[app/ui/start_screen.py](app/ui/start_screen.py)
[app/audio/note_generator_adapter.py](app/audio/note_generator_adapter.py)
[app/game/rhythm_game_engine.py](app/game/rhythm_game_engine.py)
[app/game/judge.py](app/game/judge.py)

흐름

Music File
-> app/data/songs/
-> Generate Notes
-> app/data/notes/
-> Load Selected Song
-> Note Spawn
-> Hand Lane Selection
-> EMG Activation
-> Judgement
-> Score / Combo / Result
-> Session Log (app/data/sessions/)
-> Result Summary (app/data/results/)

비고

노트는 과밀한 타격 창을 줄이기 위해 게임 전에 정규화 및 단순화된다.

TODO

세션 로그와 결과 출력에 대한 추가 데이터 흐름이 있는지 확인한다.
