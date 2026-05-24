오디오 노트 생성

목적

오디오 분석과 노트 생성이 처리되는 방식을 설명한다.

확인된 사실

EXTRACTED: 오디오 분석은 가능할 때 legacy backend 함수를 호출한다.
EXTRACTED: 노트 생성은 legacy backend의 note_generator를 우선 시도한다.
EXTRACTED: legacy 생성이 실패하면 샘플 노트로 폴백한다.
EXTRACTED: 노트는 과밀한 타격 간격을 줄이기 위해 단순화된다.
EXTRACTED: legacy_web 프론트엔드는 업로드, 분석, 노트 생성 엔드포인트를 호출한다.
EXTRACTED: legacy_web 백엔드는 차트 데이터를 구성하고 JSON/CSV를 내보낸다.

관련 파일

[app/audio/beat_analyzer.py](app/audio/beat_analyzer.py)
[app/audio/note_generator_adapter.py](app/audio/note_generator_adapter.py)
[README.md](README.md)
[legacy_web/frontend/src/api.js](legacy_web/frontend/src/api.js)
[legacy_web/backend/main.py](legacy_web/backend/main.py)

흐름

오디오 분석 -> 차트 생성 -> 레인 변환 -> 단순화 -> JSON 저장

비고

어댑터는 sys.path 조정으로 legacy_web/backend 모듈을 임포트한다.

TODO

전체 노트 생성을 위해 필요한 legacy backend 함수 범위를 확인한다.
