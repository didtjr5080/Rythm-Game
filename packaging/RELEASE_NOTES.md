## Fix: crash entering Settings with hand cursor

- Main and Settings reuse the same camera/tracking session instead of closing and reopening the camera at every transition.
- Serializes native camera open and release across workers; repeated page cleanup is idempotent.
- Defers hand-triggered page swaps until mouse event delivery returns, and guards pointer cancellation during hover/resize.
- Records runtime Python/native faults under _internal/app/data/logs for follow-up diagnosis; personal logs are not bundled.
- Regression checks include 20 main/settings round trips and blocked previous-camera teardown. Actual physical-camera confirmation is still needed on the affected PC.

## App-local hand cursor

- Main and Settings screens support a MediaPipe-driven circular pointer. The OS cursor and other applications are untouched.
- Open hand moves; one fold clicks after a 450ms double-fold wait. Two quick folds cancel the click and toggle scroll mode.
- In scroll mode, move the hand up/down; two quick folds or ESC exit. The ring turns purple and displays SCROLL.
- Settings starts its shared camera preview automatically. App-owned combo popups support hand selection.
- Tracking loss, expired results, focus loss, modal dialogs, resizing and page changes cancel pending actions. No gesture clicks in gameplay/calibration/results or from approximate OpenCV tracking.
- Reuses the existing background video worker and retains the performance optimizations, five lanes and filtered EMG threshold 12.

## Performance update

- Camera capture and MediaPipe inference run in a background worker in gameplay, lobby, calibration, and camera settings.
- Latest-result delivery prevents an application frame backlog; stale hand results expire after 250ms.
- Tracking uses a maximum 640px image while the selected camera display resolution is preserved.
- Reuses unchanged camera conversions and searches only visible notes in long charts.
- Preserves five lanes, filtered EMG threshold 12, judgment timing and full-song playback.
- Regression checks cover slow inference, worker cleanup, stale-result rejection, and high-resolution rendering. Physical-camera FPS still requires verification on the exhibition PC.

## Tested EMG calibration defaults

- New installations use filtered activity (envelope) with threshold 12, matching the completed hardware test.
- RAW ADC values are diagnostic; game judgments use the selected signal.
- Existing saved settings take priority. Select Filtered activity and threshold 12 when updating an existing installation.
- Includes five finger-count lanes, one hit per contraction, disconnected-input blocking, and Korean-path MediaPipe support.
- Electrode placement and individual signal levels may require calibration in Settings.

## Five lanes and EMG input fixes

- Any 1-5 extended fingers select lanes 1-5. A fist selects none; horizontal position no longer selects a lane.
- Real serial mode disables input when disconnected, never silently substitutes SPACE.
- Rest-to-arm, noise confirmation, fresh-sample checks and one hit per contraction prevent repeated activation.
- Existing 3-lane charts migrate to lanes 1/3/5; new charts retain 5-lane metadata.
- Includes Korean-path MediaPipe model loading and bundled C++ runtime fixes.

## EMG Motion Rhythm — Windows x64

MediaPipe 호환성 업데이트: 한글 경로에서 모델을 불러오지 못하는 문제를 보완했습니다. 필요한 C++ 런타임을 함께 포함하고, 설정의 카메라 테스트에서 MediaPipe 활성 상태와 실제 오류를 확인할 수 있습니다. 초기화 실패가 대체 인식 뒤에 숨지 않도록 표시합니다.

음악 목록 업데이트: 음악 선택 공간을 확대해 한 화면에 여러 곡을 표시합니다. 20곡 테스트에서 1280×720은 7곡, 1440×900은 14곡, 1920×1080은 20곡을 표시했습니다. 긴 제목은 툴팁으로 확인할 수 있으며, 기존 선택·불러오기·더블클릭 동작은 유지합니다.

노트 속도 업데이트: 기본 이동 속도를 **450 → 360**으로 낮췄습니다. 음악 재생 속도와 판정 시각은 유지합니다. 기존 설정 파일을 유지한 경우 저장된 속도가 우선하므로 설정에서 노트 속도를 360으로 지정하세요.

EMG 장치 연결 업데이트:

- 설정에서 USB 시리얼 장치 자동 검색·수동 선택·연결 테스트
- USB 식별자를 이용한 COM 번호 변경 추적과 연결 끊김 후 재연결
- A0 원시 값·처리된 활동 값 선택 및 Nano·ESP8266 펌웨어 제공
- COM5 ESP8266 실장치 펌웨어 업로드와 실제 프레임 수신 확인

센서 신호선은 적합한 아날로그 입력에 연결하고 보드의 ADC 허용 전압을 확인하세요. 실제 수축/이완 시험으로 임계값을 조정하세요.

ZIP 전체를 압축 해제한 뒤 `EMG-Motion-Rhythm.exe`를 실행하세요. Python 설치가 필요하지 않으며, `_internal` 폴더를 함께 유지해야 합니다.

- Glassmorphism Sonic Lab UI, 원근 5레인과 크리스탈 노트·히트 파동
- 실제 웹캠 선택·연결 테스트, 관절 오버레이와 손가락별 인식 상태
- 1920×1080·1440×900 화면 지원과 비율 유지
- 곡 전체 재생 완료 후 결과 화면 전환
- 임계값 저장, 센서가 없는 환경의 키보드·모의 EMG 입력

사용자 음원·개인 설정·플레이 기록은 포함하지 않습니다. SHA256 파일로 ZIP 무결성을 확인할 수 있습니다.

검증: EXE 자체 검사로 MediaPipe 모델 추론, Qt 고해상도 렌더링, 오디오 디코딩·분석·노트 생성과 화면 모듈 로딩을 확인합니다. 실제 카메라·시리얼·스피커 동작은 PC와 드라이버에 따라 별도 확인이 필요합니다.

설정에서 카메라 번호를 고른 뒤 **Connect / Test Camera**로 연결을 확인하고 저장하세요. 처음 추가한 곡은 **노트 생성** 후 시작하세요.
