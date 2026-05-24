리듬 게임 규칙

목적

레인, 노트, 타격에 대한 핵심 게임 규칙을 요약한다.

확인된 사실

EXTRACTED: 게임은 3개 레인(LEFT, CENTER, RIGHT)을 사용한다.
EXTRACTED: 노트는 판정선 타이밍 창에 도달했을 때 판정된다.
EXTRACTED: 타격은 EMG 활성화와 선택 레인이 노트 레인과 일치해야 한다.
EXTRACTED: 점수와 콤보는 게임 중 표시된다.

관련 파일

[app/config.py](app/config.py)
[app/game/judge.py](app/game/judge.py)
[app/ui/game_widget.py](app/ui/game_widget.py)

흐름

노트 생성 -> 판정선으로 이동 -> EMG + 레인 일치 -> 결과 -> 점수 업데이트

비고

판정선 위치는 설정에서 조정 가능하다.

TODO

난이도 모드에 따른 추가 규칙이 있는지 확인한다.
