Rythm-Game 위키

- v2026.11.09.4: [손 커서](../docs/hand-cursor.md)를 결과 화면·저장된 결과 목록에도 확장했습니다. 게임 중에는 비활성화하며 기존 카메라 세션을 재사용합니다.

- [설정 전환 크래시 수정](../docs/camera-transition-crash.md) — EXTRACTED/INFERRED: 네이티브 오류 기록, 카메라 공유·수명 직렬화, 손 클릭 전환 검사.

- [앱 내부 손 커서](../docs/hand-cursor.md) — EXTRACTED: 메인·설정 화면 전용 원형 포인터, 접기 클릭, 두 번 접기 스크롤 모드.

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
