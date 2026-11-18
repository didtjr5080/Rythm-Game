# EMG Motion Rhythm — 5분 발표 자료

- [PPTX 열기](EMG-Motion-Rhythm-5min.pptx)
- [발표 대본](speaker-script.md)
- [발표 흐름 Mermaid](../../diagrams/presentation-flow.md)

EXTRACTED: 제공 ZIP의 실제 PowerPoint 템플릿 중 1·3·9·11·18·4·8번 슬라이드를 골라 원본의 도형·색상·글꼴 지정·배치를 유지하고 내용을 교체했습니다. 원본은 `design-template.pptx`에 보관했습니다. 첨부 문서의 예시 문구는 디자인 참고 자료로만 취급했습니다.

EXTRACTED: 본문 6장에 15·30·40·40·45·10초, 마지막 시연 페이지에 120초를 배정했습니다. 대본은 PowerPoint 발표자 노트와 별도 Markdown으로 제공합니다. INFERRED: 실제 발화 속도에 따라 시간이 달라지므로 리허설로 조정해야 합니다.

EXTRACTED: 손가락 1~5개와 레인 매핑, EMG 입력, 수축당 최대 한 노트, PERFECT/GOOD/MISS는 `README.md`, `app/input/input_fusion.py`, `app/game/rhythm_game_engine.py`, `app/game/judge.py`에서 확인했습니다. 자동 보정은 `app/ui/settings_screen.py`, 음악·노트 저장은 `app/audio/note_generator_adapter.py`와 README, JSON/CSV 기록은 `app/analytics/session_logger.py`에서 확인했습니다. 임상 효과·정량 성능·환자 DB·클라우드 연동은 발표 내용에 추가하지 않았습니다.

## 영상 넣기

EXTRACTED: 영상이 제공되지 않아 마지막 장에는 편집 가능한 안내 상자만 있습니다. 상자를 삭제한 뒤 PowerPoint의 **삽입 → 비디오 → 이 장치**에서 영상을 선택하고, 위치·크기를 맞춘 뒤 재생 시작 방식을 설정하세요. 약 2분, 16:9 영상을 권장합니다. 준비 20초 → 플레이 80초 → 결과 20초가 시연 구성 제안입니다(INFERRED).

## 확인과 제한

EXTRACTED: ZIP 무결성, XML 파싱, 내부 관계의 대상 파일 존재, 발표 슬라이드 7개와 노트 7개를 검사했습니다. PowerPoint 실제 렌더링과 영상 재생은 이 환경에서 확인하지 못했습니다. 첨부 템플릿의 글꼴 지정은 유지했으므로 다른 PC에서 대체 글꼴이 사용되면 줄바꿈을 확인하세요. `content-layout-preview.png`는 본문 구성 참고용이며 최종 템플릿 렌더링이 아닙니다.

## 수동 Graphify

저장소 루트에서 `pip install graphifyy` 후 `graphify .`를 실행합니다. 옵션은 `graphify --help`, 인증·백엔드 설정은 [기존 안내](../graphify.md)를 참고하세요. 이번 작업에서는 Graphify를 실행하지 않았습니다. 기존 보고서는 2026-05-24 생성본이므로 현재 소스 확인을 우선했습니다.

## 남은 TODO

- 시연영상 삽입 후 전체 발표 5분 리허설.
- 발표할 PC에서 글꼴·줄바꿈·영상 음량 및 재생 확인.
- 필요하면 표지에 발표자·팀명 추가.
