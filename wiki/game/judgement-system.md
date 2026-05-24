판정 시스템

목적

점수 계산에 사용되는 타이밍 창과 판정 결과를 문서화한다.

확인된 사실

EXTRACTED: 판정 결과는 PERFECT, GOOD, MISS이다.
EXTRACTED: PERFECT는 perfect 창 안에서, GOOD은 judge 창 안에서 발생한다.
EXTRACTED: 노트가 judge 창을 지나면 MISS로 기록된다.
EXTRACTED: PERFECT는 1000점, GOOD은 500점이며 MISS는 콤보를 초기화한다.

관련 파일

[app/game/judge.py](app/game/judge.py)
[app/game/score.py](app/game/score.py)
[app/config.py](app/config.py)

흐름

입력 확인 -> 타이밍 창 -> PERFECT/GOOD/MISS -> ScoreState 업데이트

비고

판정은 타이밍 정확도와 EMG 활성화 및 레인 일치에 의존한다.

TODO

ScoreState 외에 다른 스코어링 로직이 있는지 확인한다.
