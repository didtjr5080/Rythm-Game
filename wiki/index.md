- [EXTRACTED: Reduced note frequency, including existing charts](../docs/note-density.md)

- [EXTRACTED: Webcam game selection and note speed 50-200](../docs/camera-selection-speed.md)

- [EXTRACTED: 상위 모드의 핀치+암밴드 첨부 이미지 적용](../docs/game-selection-images.md) — 원본 PNG와 비율 보존, 기본 두 모드 이미지 유지.

- [EXTRACTED: 사람별 보정 저장·삭제·상위 모드 해금](../docs/player-profiles.md) · [Mermaid](../diagrams/player-profiles.md) — 저장값 바로 시작, 같은 프로필의 기본 두 모드 정상 완주 필요, 120개 검사.

- [EXTRACTED: 핀치 + 신전 동시 확인 상위 모드](../docs/pinch-extension-mode.md) · [Mermaid](../diagrams/pinch-extension-mode.md) — 세 번째 선택, 기본 두 모드 보존.

- [EXTRACTED: 근전도 3.0초 기록의 최저값 이상이면 신전](../docs/emg-minimum-baseline.md) · [Mermaid](../diagrams/emg-rest-baseline.md) — 평균·+0.01 제거, 원래 정밀도로 비교, 측정값 결과 기록.

- [EXTRACTED: 두 모드 연속 MISS10 종료·근전도 긴 노트 전용](../docs/game-rule-update.md) · [Mermaid](../diagrams/game-rule-update.md) — PERFECT/GOOD 시 연속 횟수 초기화.

- [EXTRACTED: 음악 원본·재생 시간축·전체 곡 종료 보강](../docs/music-timeline.md) · [Mermaid](../diagrams/music-timeline.md) — 89개 검사, 양 모드 전체 곡·오류·취소와 실제 MP3 PCM 검증.

- [EXTRACTED: 메뉴 MediaPipe 손 커서 복원 / 게임 진입 전 카메라·추론 종료](../docs/menu-hand-cursor.md) · [Mermaid](../diagrams/menu-hand-cursor.md)

- [EXTRACTED: 게임 선택 이미지 카드·설명 제거](../docs/game-selection-images.md) · [Mermaid](../diagrams/game-selection-images.md)

- [EXTRACTED: 핀치의 armband 연동 전부 제거 / Leap 전용 및 근전도 모드 분리](../docs/pinch-leap-only.md) · [Mermaid](../diagrams/pinch-leap-only.md)

- [EXTRACTED: Leap 70% + EMG 30% 참고 점수 합산](../docs/weighted-pinch.md) · [Mermaid](../diagrams/weighted-pinch.md)

- [EXTRACTED: 재부팅 후 COM4 복구 / USB 초기화·재연결 및 장치 구분 이력](../docs/armband-reconnect.md) · [Mermaid](../diagrams/armband-reconnect.md)

- [EXTRACTED: Armband 단독 핀치 테스트](../docs/armband-only-test.md) · [Mermaid](../diagrams/armband-only-test.md)

- [EXTRACTED: Leap + armband 다섯 자세 보정 및 핀치 일치 판정](../docs/pinch-armband-intent.md) · [Mermaid](../diagrams/pinch-armband-intent.md)

- [EXTRACTED: 매 게임 시작 전 핀치 보정](../docs/pre-game-calibration.md) · [Mermaid](../diagrams/pre-game-calibration.md)

- [EXTRACTED: OYMotion USB 8채널 12bit 500Hz / 전체 채널 근활성도](../docs/oymotion-emg.md) · [Mermaid](../diagrams/oymotion-emg.md)

- [전시 안정화 구현과 현장 TODO](../docs/exhibition-stability.md) — v2026.11.17.2: 버튼 합성 분리와 설정 상태 영역 고정, Windows 125% 검사.
Rythm-Game 위키

- [EXTRACTED: Leap 핀치 모드 — 연속 MISS 10회 즉시 종료](../docs/leap-miss-limit.md) · [Mermaid](../diagrams/leap-miss-limit.md)

- [EXTRACTED: 최신 EMG — 수동 보정 제거 / 시작 전 3초 안정 기준 +0.01 입력](../docs/emg-rest-baseline.md) · [Mermaid](../diagrams/emg-rest-baseline.md)

- [EXTRACTED: EMG 보정·게임 값 일치 / 약한 수축과 입력 허용 범위 확대](../docs/emg-assisted-input.md) · [Mermaid](../diagrams/emg-assisted-input.md)

- [EXTRACTED: 최신 게임 선택 — 근전도 리듬·긴 노트 / 핀치 리듬, 두 모드 채보 동시 생성](../docs/game-modes.md) · [Mermaid](../diagrams/game-modes.md)

- [EXTRACTED: 최신 판정 — EMG 없이 기준선에서 핀치 유지로 득점](../docs/pinch-hold-scoring.md) · [Mermaid](../diagrams/pinch-hold-scoring.md)

- [EXTRACTED: Leap Motion 개인별 핀치 보정·저장·선택](../docs/leap-personal-calibration.md) · [Mermaid](../diagrams/leap-personal-calibration.md)

- [EXTRACTED: 손을 펼치지 않는 연속 핀치 즉시 전환](../docs/leap-personal-calibration.md#손을-펼치지-않는-연속-핀치-전환)

- [EXTRACTED: 최신 Leap Motion 전용 손 입력 / 웹캠 제외](../docs/leap-only.md) · [Mermaid](../diagrams/leap-only.md)

- [EXTRACTED: 새 채보의 MIDDLE 다음 RING 생성 금지](../docs/leap-only.md#middle-다음-ring-생성-금지)

- [EXTRACTED: 노래 없는 샘플 게임 재점검·엔진 최종 레인 제약](../docs/leap-only.md#노래-없이-시작하는-샘플-게임-재점검)

- v2026.11.09.4: [손 커서](../docs/hand-cursor.md)를 결과 화면·저장된 결과 목록에도 확장했습니다. 게임 중에는 비활성화하며 기존 카메라 세션을 재사용합니다.

- [설정 전환 크래시 수정](../docs/camera-transition-crash.md) — EXTRACTED/INFERRED: 네이티브 오류 기록, 카메라 공유·수명 직렬화, 손 클릭 전환 검사.

- [앱 내부 손 커서](../docs/hand-cursor.md) — EXTRACTED: 메인·설정·결과·결과 목록의 원형 포인터, 접기 클릭, 두 번 접기 스크롤 모드.

- [프레임 지연 최적화](../docs/performance.md) — EXTRACTED: 영상 작업 스레드, 최신 결과, 채보 구간 검색, 검증 범위.

- v2026.11.08.5: 필터 신호·임계값 12 기본 설정 및 사용자 테스트 완료. [입력 설정](../docs/five-lane-input.md)

- [5레인과 EMG 입력 수정](../docs/five-lane-input.md) — EXTRACTED: 손가락 개수 매핑, 실제 입력 차단, 수축당 한 번 판정.

이 위키는 기존 EMG Motion Rhythm 프로젝트를 문서화합니다.

이 위키의 목적은 구현된 게임을 변경하지 않고 현재 프로젝트 구조, 입력 흐름, 게임 루프, 오디오/노트 흐름, 시각화 리소스를 설명하는 것입니다.

아키텍처

시스템 개요
데이터 흐름

입력

입력 개요
모의 입력

EMG

시리얼 EMG 리더
EMG 임계값

손 추적

MediaPipe 손 추적
카메라 폴백

게임

리듬 게임 규칙
판정 시스템
설정 시스템

오디오

오디오 노트 생성
저장된 음악 흐름

데이터

로컬 데이터 레이아웃

오류

런타임 오류
EMG 입력 오류
카메라 및 MediaPipe 오류

결정 사항

아키텍처 결정 사항

모순점

모순점 및 애매한 내용

다이어그램

시스템 개요 다이어그램
데이터 흐름 다이어그램
입력 흐름 다이어그램
게임 루프 다이어그램
파일 구조 다이어그램
Graphify 리포트

Windows 실행 파일 배포

- [EXTRACTED: 다른 PC·한글 경로의 MediaPipe 진단과 수정](../docs/mediapipe-portability.md)

- [EXTRACTED: 여러 곡을 한눈에 보는 저장 음악 목록](audio/saved-music-flow.md)

- EXTRACTED: 노트 속도 360을 포함한 배포 버전과 기존 설정 우선순위는 [Windows 배포 안내](../docs/windows-release.md)를 참고합니다.

- [EXTRACTED: 노트 속도 기본값과 저장 설정](game/settings-system.md)

- [EXTRACTED: EMG 장치 검색·선택·재연결 및 펌웨어 안내](../docs/emg-device-setup.md)

- [EXTRACTED: Windows EXE 다운로드·빌드·검사 안내](../docs/windows-release.md)
- EXTRACTED: 같은 안내의 아이콘 항목에서 사용자 제공 PNG의 ICO 변환과 EXE·창 아이콘 적용 경로를 확인할 수 있습니다.

- [EXTRACTED: EMG 필터링·설정 화면 자동 임계값 보정](../docs/emg-auto-calibration.md) — [Mermaid 흐름](../diagrams/emg-auto-calibration.md)

- EXTRACTED: 자동 EMG 보정 포함 Windows 빌드 2026.11.17.3 생성·EXE 자체 검사 통과. [배포 안내](../docs/windows-release.md)

- [EXTRACTED: SZH-GJD001 센서 전용 500Hz·60–100Hz 필터와 RMS, COM3 백업·업로드·실수신](../docs/szh-gjd001-filter.md) — Windows 2026.11.17.4, [Mermaid](../diagrams/emg-auto-calibration.md)

- [EXTRACTED: 높은 안정 신호에서 자동 보정 실패 수정 — ON/OFF 분리 저장](../docs/emg-calibration-hysteresis.md) — Windows 2026.11.17.5, 검사 24개 및 EXE 자체 검사 통과.

- [EXTRACTED: 대역통과 필터 우회 비교 빌드](../docs/emg-no-bandpass-comparison.md) — 별도 No-Bandpass EXE 2026.11.17.6, COM3에서 BP RMS/NO BP RMS 동시 수신 확인. [Mermaid](../diagrams/emg-auto-calibration.md)

- [EXTRACTED: 고정 차이 5 제거, 안정 흔들림·3회 반복 수축 기반 보정](../docs/emg-adaptive-calibration.md) — 소수점 ON/OFF 게임 전달, Windows 2026.11.17.7, 검사 31개 및 EXE 자체 검사 통과.

- [EXTRACTED: 측정값 직접 보정 — 차이·잡음·분리 거부 조건 제거, 증가/감소형 적용](../docs/emg-direct-calibration.md) — Windows 2026.11.17.8, 검사 33개·EXE 자체 검사 통과.

- [EXTRACTED: 게임의 100% 초과 표시 수정 — 실제 EMG 활동값·ON/OFF 표시와 저장값 유지 검증](../docs/emg-game-display.md) — Windows 2026.11.17.9, 검사 34개·EXE 자체 검사 통과.

- [EXTRACTED: 최신 Windows 버전과 구버전 정리·데이터 백업](../docs/version-cleanup.md) — 2026.11.17.10, dist_windows_current로 통일. [두 손가락 드래그 스크롤](../docs/hand-cursor.md), [Mermaid](../diagrams/hand-cursor.md).

- [EXTRACTED: 두 손가락 손목 기울기 스크롤](../docs/hand-cursor.md) — 중립 유지 → 손목 뒤로 젖힘: 위 / 안쪽 굽힘: 아래 / 중립: 정지. v2026.11.17.11, 현재 실행 경로 유지·런타임 51개 백업/이관. [Mermaid](../diagrams/hand-cursor.md).

- [EXTRACTED: ?? ??? ?? 5? ?? PPT ? 3? ?? + 2? ?? ??](../docs/presentation/README.md) ? [?? ?? ??](../diagrams/presentation-flow.md)

- [EXTRACTED: Leap Motion 4?? ?? ??](../docs/leap-four-lane.md) ? [Mermaid](../diagrams/leap-four-lane.md)

- [EXTRACTED: Leap 4?? ? EXE??? SDK??? ?? 12? ??](../docs/leap-four-lane.md#2026-11-18-?-exe-??)
- [EXTRACTED: 공유 armband 연결·선택 음악 경로 검증 / 미확인 동기화와 실패 검사](../docs/music-session-review.md) · [Mermaid](../diagrams/music-session-review.md)


- [EXTRACTED: ?? ?? ??? ?? ??](../docs/NEXT_TASKS.md) ? [?? ?? ??](../docs/music-session-review.md) ? [Mermaid](../diagrams/music-session-review.md)

- [Next tasks and acceptance criteria](../docs/NEXT_TASKS.md) | [Local verification](../docs/music-session-review.md) | [Mermaid](../diagrams/music-session-review.md)
