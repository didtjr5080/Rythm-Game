# OYMotion USB armband 입력

EXTRACTED: 기존에 구현된 `OYMotionReader`는 USB 동글의 Windows COM 포트와 공식 gForce SDK를 사용한다. SDK에 500Hz, 12bit, 채널 마스크 `0xFF`(8채널), 패킷 길이 128을 요청하고 성공 응답 후 raw EMG 알림을 켠다. 카메라 입력을 사용하지 않는다.

## 사용

EXTRACTED: Settings의 EMG 장치를 OYMotion으로 선택하고 실제 USB 동글 포트(현재 COM4) 또는 Auto를 선택한다. 다른 armband 프로그램은 포트를 함께 사용할 수 없다. 전원을 켠 armband가 검색되면 연결·설정 후 채널별 RMS와 전체 근활성도가 표시된다. 기존 직렬 장치는 Legacy 항목으로 분리되어 있다.

EXTRACTED: 근전도 게임은 시작 전 3초 동안 신선한 입력의 안정 평균을 측정한다. 수동 근전도 보정은 사용하지 않는다. 이후 소수 둘째 자리로 비교한 전체 근활성도가 안정 기준보다 **0.01 이상 높으면 활성**이다. 값은 아래의 AC RMS ADC 단위이며 원시 ADC의 DC 값이나 %MVC가 아니다. Leap 핀치 게임은 별도의 입력 경로를 사용한다.

## 전체 채널 계산

EXTRACTED: `app/input/oymotion_activity.py`는 수신 버퍼를 little-endian 16bit unsigned 값으로 해석하고 각 값이 0–4095인지 검증한다. 한 프레임은 8채널, 16바이트다. 최근 50프레임(설정 주파수 기준 100ms)의 채널별 평균을 뺀 뒤 각 채널의 제곱 평균을 계산한다.

```text
channel_variance[c] = mean((sample[c] - mean(sample[c])) ** 2)
activity = sqrt(mean(channel_variance[0:8]))
```

EXTRACTED: 모든 수신 프레임과 8채널이 같은 비중으로 계산에 기여한다. 10프레임마다 결과를 발행하므로 수집 설정은 500Hz, 근활성도 갱신은 약 50Hz다. 채널별 DC 제거로 안정 오프셋을 근활성도로 세지 않으며, 채널 부호가 서로 달라도 상쇄되지 않는다. 수신 중단 150ms 이후에는 신선한 신호로 인정하지 않는다.

## 검증과 범위

EXTRACTED: 2026-11-18 충전 후 COM4 실장치 검사에서 45초 관찰 중 연결 이후 약 20초 동안 **9,952프레임(채널별 9,952개, 총 79,616개 값)**을 수신했다. 마지막 약 1초 구간은 488프레임 증가했고 잘못된 패킷은 0개였다. 설정 요청 성공과 실수신은 확인했으나 하드웨어 타임스탬프로 정확한 샘플 주파수를 측정한 결과는 아니다. 원본 관찰 기록은 로컬 `build/oymotion-live-resume.json`이다.

EXTRACTED: 관련 소스 검사 56개가 통과했다. `docs/check_oymotion.py`는 12bit 경계, 잘못된 패킷, DC 제거, 8채널 기여, 연속 패킷 누적, SDK 설정 및 실패 응답 처리를 검증한다.

EXTRACTED: 새 배포 폴더는 `dist_windows_oymotion_2026.11.18/EMG-Motion-Rhythm-No-Bandpass`다. 기존 핀치 보정·설정을 복사하고 새 폴더 설정만 OYMotion, serial, COM4로 지정했다. 배포된 두 SDK DLL 로딩·콜백 구조 크기(80바이트)·원본 해시 일치를 포트를 열지 않고 확인했다(`sdk-check.json`). 기존 배포 폴더는 유지했다.

EXTRACTED: 새 EXE의 `--self-test` 자체 검사 15항목이 통과했다(`ok=true`). 이 자체 검사는 모의 입력과 게임·오디오 경로를 검사하며 실장치 수신 검사는 위 COM4 기록으로 별도 구분한다. 배포 폴더와 `release/self-test-oymotion-2026.11.18.json`에 보고서가 있다.

AMBIGUOUS: 사용자가 힘을 준 시점별 기록과 임상 사용 검증은 없다. 현재 0.01 기준은 사용자 요청을 그대로 반영하며 자연 잡음에 의한 활성 여부는 실제 착용 상태에서 확인해야 한다. 장시간 연결 및 전원 차단·재연결 반복도 추가 검증 대상이다.

## SDK와 문서

EXTRACTED: 포함된 Windows x64 DLL은 [공식 gForceSDKCSharp](https://github.com/oymotion/gForceSDKCSharp)의 커밋 `78e241145f17aa0f9b8b2627b8d32294dbccd6d4`에서 가져왔다. 출처·라이선스·해시는 `app/vendor/oymotion/NOTICE.txt`에 기록되어 있다. `EMG-Motion-Rhythm.spec`가 해당 DLL을 배포 폴더의 `_internal/oymotion`에 포함한다.

EXTRACTED: 관련 구현은 `app/input/oymotion_sdk.py`, `oymotion_reader.py`, `oymotion_activity.py`, `emg_factory.py`, `emg_session.py`, `app/ui/settings_screen.py`, `app/ui/game_widget.py`다. 이 문서 추가 시점에는 게임 동작을 더 변경하지 않았다.

[입력 흐름 Mermaid](../diagrams/oymotion-emg.md)를 Mermaid 지원 Markdown 미리보기에서 연다. Graphify 수동 실행은 저장소 루트에서 `pip install graphifyy`, `graphify --help`, `graphify .` 순서다. 기존 Graphify 출력은 이번에 갱신하지 않았다.
