# 전시 안정화 작업 기록

## v2026.11.17.2 후속 수정

EXTRACTED: v2026.11.17.1에서도 사용자 스크린샷의 Settings/Start Game 버튼에 사각형 조각이 남았다. 이전 단색 부모 배경 복원 검사는 스타일 버튼과 겹치는 형제 위젯의 Windows 합성을 충분히 검증하지 못했다. INFERRED: 전체 화면 크기 투명 자식 커서가 버튼 hover의 부분 갱신과 겹치는 경로가 원인 후보다.

EXTRACTED: CursorRing을 부모 화면에 소유된 별도 네이티브 투명 창으로 전환했다. 입력 통과·포커스 비활성·표시 시 활성화 금지를 적용하고, 그리기 영역을 투명 픽셀로 먼저 지운다. 앱의 활성 화면 제어와 추적 손실/화면 이탈 시 숨김은 기존 컨트롤러를 사용한다. OS 커서를 이동시키지 않는다.

EXTRACTED: 설정의 카메라 상태는 매 틱 1줄 상태→3줄 결과로 두 번 바뀌고 있었다. 프레임 유효 시 중간 1줄 변경을 제거하고 상태는 고정 3줄 높이·줄바꿈 없음·폭 크기 힌트 무시, 영상은 높이 200으로 고정했다. 같은 문구/색상은 다시 적용하지 않는다. 상세 추론 진단은 툴팁에 제공한다.

`WorkOrder/verify_button_overlay.py` 및 `--windows` 옵션을 실행했다. 오프스크린과 실제 Windows Qt 창(현재 125% DPR) 모두 PASS: 20회 이동 후 이전 커서 알파 제거, 입력 통과 플래그, 40회 상태 문구 변화에서 고정 레이아웃, 동일 상태 setText 0회. 손 커서·결과 화면·설정 전환·해상도 기존 검사도 통과했다. 실제 사용자 전시 PC에서 재확인은 여전히 필요하다.

EXTRACTED: 작업 지시서 `WorkOrder/Rythm_Game_Exhibition_Work_Order (1).md`를 기준으로 구현했다. 시작 HEAD는 `42bc7ec700136efd5c1ba240771262af249110fe`, 비교 ZIP은 v2026.11.09.4이며 SHA256은 `7ff8cd5eee8118ede615b6b968480738ef044373aeac05a3ee6b6df856603702`이다. 현장에서 문제가 발생한 파일과 이 ZIP이 동일한지는 미확인이다.

## 구현과 검증 근거

- EXTRACTED: 커서의 `WA_NoSystemBackground`를 제거해 Qt 배경 전파를 복구했다. 동일 위치/상태는 갱신하지 않고 표시할 때만 show/raise한다. 20회 이동·상태 변경·우측 SCROLL·숨김과 크기 변경 후 배경 픽셀 일치를 오프스크린에서 검사했다. INFERRED: 배경 전파 차단은 현장 잔상의 유력 원인이지만 실제 전시 EXE 증상과 동일하다는 확증은 없다.
- EXTRACTED: 표시 모드/해상도가 같으면 창 설정을 다시 적용하지 않는다. 저장 후 시작 화면을 먼저 교체하고 변경된 표시 설정만 적용한다. 모드 복귀는 showNormal 후 클라이언트 크기를 적용하며 가용 화면으로 제한한다. 시작 화면은 스크롤 컨테이너로 작은 화면에서도 버튼에 접근한다. 15회 실제 저장 경로에서 창 위치·크기와 오버레이 범위를 검사했다.
- EXTRACTED: 게임은 InputFusion의 사용하지 않는 RGB 변환을 생략하고 카메라 표시가 모두 꺼지면 픽스맵 변환도 생략한다. show_camera_debug가 실제 카메라 HUD를 제어한다. 영상 부재 시 게임의 가상 골격을 그리지 않는다. QImage는 실제 stride와 복사된 버퍼를 사용한다. 반전 설정 세대로 이전 영상/좌표/제스처를 폐기하고 손가락 안정화 이력을 초기화한다.
- EXTRACTED: 음원 분석·채보 생성은 제한된 작업 풀에서 수행한다. 페이지와 곡 선택을 확인한 뒤 완료 결과를 UI에 적용한다. 실패 시 상태에 이유와 재시도 안내를 표시한다. 채보 오류는 시작 화면에서 경고하고 재생성을 안내한다.
- EXTRACTED: 세션과 결과 저장은 게임 종료 후 작업 풀에서 수행한다. 결과 화면에서 저장 중/완료/오류와 재시도를 제공한다. 파일 이름에 UUID를 추가하고 개별 JSON/CSV/채보 파일을 임시 파일 후 원자 교체한다. JSON/CSV 두 파일 전체가 하나의 트랜잭션인 것은 아니다. 저장 실패 주입에서 기존 파일 보존·임시 파일 정리·재시도를 검사했다.
- EXTRACTED: GUI tick/paint 간격 및 실행 시간, 캡처 읽기, 추론, 캡처→첫 GUI read, 결과 간격을 최대 20,000개씩 보관한다. 결과 전환 시 `app/data/logs/performance-*.json`에 n/p50/p95/p99/max를 비동기로 기록한다. frozen 배포는 `_internal/app/data/logs/`이다. 첫 GUI read는 모니터에 실제 표시된 시각이 아니다. 창 적용값/실측 크기/가용 영역/DPR은 runtime 로그에 기록한다.

## 재현 명령

저장소 루트에서 `.venv311/Scripts/python.exe WorkOrder/verify_exhibition_graphics.py`와 `WorkOrder/verify_exhibition_jobs.py`를 실행한다. 기존 hand_cursor/result_hand_cursor/live_video/camera_transition/camera_resolution/fingers/five_lane_input/emg_serial/full_song 검사도 같은 Python으로 실행한다. 카메라 해상도 검사는 모의 가용 화면 2560×1600에서 1920×1080과 1440×900 렌더링을 확인한다.

## 현장 리허설과 미검증 항목

### 이번 실행 결과

| 검사 | 결과 |
|---|---|
| verify_exhibition_graphics.py | PASS: 커서 복원 20회, 저장 15회, 합성 영상 반전/맞춤/손실/표시 끔 |
| verify_exhibition_jobs.py | PASS: 선택 변경, 저장 충돌 방지, 원자 쓰기 실패, 결과 저장 재시도 |
| verify_hand_cursor.py / verify_result_hand_cursor.py | PASS: 접기와 스크롤, 목록, 결과 재시작, OS 커서 유지 |
| verify_camera_transition.py | PASS: 네이티브 해제 직렬화, 공유 세션, 20회 손 클릭 왕복 |
| verify_camera_resolution.py | PASS: 1920×1080 / 1440×900의 5개 화면과 모의 카메라 |
| verify_live_video.py | PASS: 만료·반전 무효화, 최신 슬롯, 장치 수명, 긴 채보 |
| verify_fingers.py / verify_five_lane_input.py | PASS: 32개 조합·회전·반전, 5레인·수축당 1회 |
| verify_emg_serial.py | PASS: 11개 직렬 입력 검사 |
| verify_full_song.py | PASS: 전체 음원·종료·시계·로딩 취소 |
| verify_ui.py | PASS: 네 화면·입력·PIP/AR, 모의 1280×720 paint 평균 10.43ms |
| verify_mediapipe_portability.py / verify_tracker_startup.py | PASS: Unicode 캐시와 실제 네이티브 모델의 빈 영상 추론 |

EXTRACTED: 모의 slow-camera 검사에서 수정판 GUI read p95 0.005ms, 같은 검사 내 동기 기준 81.09ms였다. 이 수치는 기존 워커 구조의 비차단성을 확인할 뿐 이번 변경으로 얻은 실제 카메라 개선량은 아니다. 기준판의 기존 모의 paint 기록은 약 9ms였으나 실행 조건을 통제한 재측정이 아니므로 10.43ms와 성능 증감 비교에 사용하지 않는다.

AMBIGUOUS: 현재 도구 환경에서는 물리 카메라·EMG·스피커·전시 모니터의 동시 사용과 실제 손 추적을 검증하지 못했다. Windows 100/125/150% DPI, 외부 출력, 실제 첫 표시 프레임, 콜드 시작/오디오 출력 지연, 60분·20회 완주, 메모리/핸들 추세는 현장에서 남겨야 한다. 오프스크린 픽셀 검사는 실제 Windows 합성기를 대체하지 않는다. 제시된 p95/p99 합격선을 달성했다고 주장하지 않는다.

추론 후보 분산과 배경 캐시는 실측 병목이 입증되지 않아 기존 알고리즘을 유지했다. 비교 기준판의 실제 장비 측정도 아직 없으므로 모의 워커 검사 수치를 실제 FPS로 해석하지 않는다. 기본 카메라 해상도는 기존 1280×720을 유지했다. 전시 초기에는 설정에서 화면 1280×720·카메라 640×480·AR 끔을 선택하고 정확도를 비교한다.

현장: 전체 ZIP을 쓰기 가능한 로컬 폴더에 해제하고 `_internal`을 유지한다. 운영자가 직접 보유한 곡 1~2개를 Add/Load → Generate Notes로 미리 준비한다. 개인 음원·설정·세션은 배포 ZIP에 넣지 않는다. 전시 곡/채보를 별도로 백업한다. 카메라 오류는 설정에서 재선택/테스트하고 숫자키 1~5를 사용한다. EMG 분리 시 실제 모드 입력은 차단되며 SPACE는 명시적인 모의 모드에서만 동작한다. 스피커/파일 오류는 Back 후 장치/파일을 수정해 재시작한다. 실패 시 runtime 로그와 Windows 오류 이벤트를 함께 보관하고 검증된 이전 ZIP으로 돌아간다.

[처리 흐름](../diagrams/exhibition-stability.md)은 GitHub Mermaid 미리보기로 확인한다. Graphify는 활성 환경에서 `graphify .`를 수동 실행한다.
