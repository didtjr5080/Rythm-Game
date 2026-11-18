# USB 동글 초기화 실패와 재연결

EXTRACTED: 후속 재부팅 후 pyserial 목록에서 `COM4 / USB Serial Port(COM4)`가 다시 확인됐다. 사용자 보정 화면에도 armband 8채널 RMS와 동작별 수집 개수가 표시됐다. 아래 COM 미열거 기록은 복구 전 점검 이력이다. 이후 나타난 `Armband NONE: patterns overlap or vary too much`는 포트 초기화 오류가 아니라 자세 보정의 분리 검사 실패다. [보정 규칙](pinch-armband-intent.md)을 참고한다.

EXTRACTED: 추가 HID 목록 점검에서 `Bluetooth Low Energy GATT compliant HID device`의 부모 장치 이름은 `SPA-NMA1PM`이었다. 이전 gForcePro+ 주소와 다른 Bluetooth 장치이며 armband 수신 동글로 선택할 근거가 없다. 이 점검 시점에는 전체 Bluetooth 클래스 조회에서도 gForcePro+ 항목이 나오지 않았고 현재 COM 목록도 비어 있었다. HID의 일반 표시 이름만으로 장치를 식별하지 않는다.

AMBIGUOUS: 과거 사용자 보고로 허브 연결 경로를 의심했으나, 이후 본체 직접 연결에서도 실패했다. 따라서 허브만의 문제라는 이전 추론은 확정할 수 없다. 동글·PC USB 연결의 구체적인 원인은 미확정이며 추가 코드 변경이나 재빌드는 하지 않았다.

EXTRACTED: 후속 점검에서 관련 게임 프로세스 종료를 확인한 후에도 COM 포트가 없었다. `Start-Process -Verb RunAs`를 통해 관리자 권한으로 수행한 `pnputil /scan-devices`는 종료 코드 0으로 성공했지만, 이후에도 COM 포트는 없고 FTDI 동글은 Disconnected였다. 앞선 일반 실행의 권한 오류와 구분한다.

EXTRACTED: 현재 연결된 USB Composite Device의 장치 속성을 직접 조회한 결과, `DEVPKEY_Device_BusReportedDeviceDesc`는 `Leap Motion Controller`, 하드웨어 ID는 `USB\\VID_F182&PID_0003`였다. 이는 별도 FTDI 장치(`VID_0403/PID_6001`, 과거 COM4)와 다르다. USB Composite Device라는 일반 표시 이름만으로 armband 수신 동글이라고 판단할 수 없다. 이 점검에서는 연결된 USB 클래스 중 해당 이름의 장치는 하나였다.

AMBIGUOUS: 다른 PC가 없어 교차 연결 검사는 수행하지 못했다. 실제 armband 수신 동글의 연결 확인과 새 COM 열거가 우선이며, 드라이버 교체 필요성이나 동글 고장은 아직 확정하지 못했다.

EXTRACTED: 사용자 화면은 SDK `hub_init`의 code 1 실패다. 포함된 공식 SDK의 `Hub.cs`에서 1은 일반 오류(GF_ERROR)이며 다른 앱 점유만을 뜻하지 않는다.

EXTRACTED: 2026-11-18 점검 시 pyserial의 COM 포트 목록과 Windows의 연결된 Ports 목록이 모두 비어 있었다. 연결 해제된 장치 목록에는 FTDI `USB Serial Port(COM4)`가 있었고 해당 드라이버는 `oem155.inf`로 등록되어 있었다. 따라서 COM4는 과거 등록 정보이며 당시 실제 연결 상태는 Disconnected다. `Port_#0002.Hub_#0007`은 USB 위치 문자열이며 COM 번호가 아니다.

EXTRACTED: 후속 화면 점검에서도 FTDI 상위 장치 `USB Serial Converter`는 Disconnected, `DEVPKEY_Device_IsPresent=FALSE`였다. 기존 연결 경로의 Generic USB Hub는 Started였으며 연결된 문제 장치 목록은 비어 있었다. 따라서 허브 인식과 동글 인식은 구분해야 한다. 동글 자체가 현재 열거되지 않는 상태이며, 물리 고장·접촉·다른 연결 위치 등 세부 원인은 확정하지 못했다. 이 후속 점검에서는 코드나 EXE를 추가로 변경하지 않았다.

EXTRACTED: `pnputil /scan-devices`는 일반 실행과 실행 권한 확장 요청 후에도 Windows의 Access is denied로 실패했다. 장치 재검색 성공이나 실제 수신 복구를 확인하지 못했다. 드라이버 설치·제거·교체는 하지 않았다.

## 변경

EXTRACTED: `EMGSession.acquire`는 오류가 남은 reader를 동일 설정으로 다시 요청해도 닫고 새로 생성한다. 기존에는 설정이 같으면 실패 객체를 계속 재사용했다. 정상 연결은 계속 공유하며, 이전 lease는 교체된 reader에 접근할 수 없다. 오류 이후 Connect / Test EMG 또는 게임 보정을 다시 시작하면 새 연결을 시도한다. 주기적 무한 재시도는 추가하지 않았다.

EXTRACTED: `OYMotionSDK.open`은 요청 COM 포트 또는 Auto에서 사용 가능한 포트가 있는지 확인한 후 SDK를 초기화한다. 포트가 없으면 USB 동글 재연결·장치 목록 새로고침·현재 COM 선택 안내를 표시한다. 포트가 있어도 SDK 초기화가 실패하면 원래 오류 코드를 유지하고 동글·포트·다른 앱 점유를 확인하도록 안내한다. COM 존재 여부만으로 OYMotion 동글임을 확정하지 않는다.

EXTRACTED: 관련 소스 검사 74개 통과. `docs/check_emg_reconnect.py`는 같은 설정에서 실패한 연결 재생성·정상 연결 재사용·이전 lease 무효화, 포트 없음·잘못된 COM의 SDK 진입 차단, 포트가 있을 때 native code 1 유지 동작을 검사한다.

새 실행 폴더는 `dist_windows_armband_reconnect_2026.11.18/EMG-Motion-Rhythm-No-Bandpass`다. 새 폴더의 포트만 Auto로 설정하여 과거 COM4 번호에 고정되지 않도록 한다. 기존 배포 폴더는 유지한다.

EXTRACTED: 새 EXE 자체 검사 17항목 통과(`ok=true`). 보고서는 배포 폴더의 `self-test.json` 및 `release/self-test-armband-reconnect-2026.11.18.json`이다. 합성 입력 기반 검사이며 실장치 연결 복구를 뜻하지 않는다. 최종 점검에서도 현재 COM 포트 목록은 비어 있었다.

AMBIGUOUS: 동글이 연결된 장치로 열거되지 않는 물리적 원인은 확정하지 못했다. 현재 인식되는 USB 동글이 나타난 뒤 초기화와 8채널 실수신을 다시 검증해야 한다. 관리자 권한의 Windows 장치 관리자에서 하드웨어 변경 사항 검색을 수행할 수 있지만, 해당 조치의 성공도 이번 점검에서는 확인하지 못했다.

[재시도 흐름](../diagrams/armband-reconnect.md)은 Mermaid 지원 Markdown 미리보기에서 확인한다. Graphify 수동 실행: `pip install graphifyy` → `graphify --help` → `graphify .`. 기존 Graphify 출력은 갱신하지 않았다.
