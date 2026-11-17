# 최신 실행 버전과 구버전 정리

EXTRACTED: 후속 v2026.11.17.11은 같은 dist_windows_current 경로에서 [두 손가락 손목 기울기 스크롤](hand-cursor.md)로 교체했습니다. 교체 전 51개 런타임 파일을 `backups/wrist-scroll-upgrade-20261117/app-data`에 백업·SHA256 검증하고 새 버전으로 이관했습니다. 파일 목록은 해당 백업의 `runtime-manifest.json`에 있습니다. 현재 ZIP은 `release/EMG-Motion-Rhythm-windows-x64-2026.11.17.11.zip` 하나이며, 아래는 최초 v10 정리 당시의 기록입니다.

EXTRACTED: 사용자가 EMG 해결을 확인한 뒤 나머지 버전 정리와 두 손가락 스크롤 변경을 요청했습니다. 최신 실행 폴더는 `dist_windows_current/EMG-Motion-Rhythm-No-Bandpass`, 실행 파일은 `EMG-Motion-Rhythm-No-Bandpass.exe`로 통일합니다. 새 배포 ZIP은 `release/EMG-Motion-Rhythm-windows-x64-2026.11.17.10.zip`입니다.

## 데이터 보존과 정리 범위

EXTRACTED: 정리 스크립트는 새 EXE 존재, 자체 검사 ok=true, 새 ZIP SHA256을 확인한 뒤 진행합니다. 실행 중인 EMG 앱이 있으면 정리를 시작하지 않습니다. 삭제 경로는 작업 공간 내부인지 확인하고 다음 구버전 폴더 이름만 대상으로 지정합니다.

```text
dist_windows
dist_windows_szh_v4
dist_windows_szh_v5
dist_windows_no_bandpass
dist_windows_adaptive_calibration
dist_windows_direct_calibration
dist_windows_emg_display
```

EXTRACTED: 각 구버전 `_internal/app/data`의 설정·음원·노트·결과·세션·로그를 `backups/version-cleanup-20261117`에 버전별로 복사하고 SHA256을 검증합니다. 최신 실행 폴더에도 데이터를 합칩니다. 같은 상대 경로가 겹치면 수정 시간이 가장 최근인 파일이 활성 폴더에 남으며, 다른 사본도 버전별 백업에서 복구할 수 있습니다. 검증된 백업을 만든 뒤 구버전 EXE 폴더와 ZIP·해시를 삭제합니다.

EXTRACTED: 구버전 자체 검사·실수신 요약 JSON은 백업의 `release-reports`에 보존합니다. 오래된 Windows 빌드 캐시만 정리하며 `build/firmware`의 원본 플래시 백업과 `release/firmware-*`는 건드리지 않습니다. 소스·문서·가상환경도 유지합니다. 백업은 git 추적 대상에서 제외합니다.

EXTRACTED: 최종 백업 목록과 해시는 `runtime-manifest.json`, 삭제 목록과 최신 경로는 `cleanup-summary.json`에 기록합니다. 다른 문서에 적힌 과거 실행 경로는 생성 당시의 기록이며, 정리 후 실행 경로로 사용하지 않습니다.

## 손 스크롤

EXTRACTED: 최신 앱은 [두 손가락 드래그 스크롤](hand-cursor.md)을 사용합니다. 정확히 두 손가락을 펴고 위/아래로 움직이며, 멈추면 스크롤도 멈춥니다. 자세를 풀면 종료합니다. EMG 처리와 보정 코드는 변경하지 않습니다.

EXTRACTED: 최신 EXE 자체 검사 11개 항목을 통과했습니다. 주먹 클릭·두 손가락 위아래 스크롤·정지·자세 해제·포커스/모달/ESC·결과 목록 회귀 검사가 통과했고 EMG 검사 34개도 통과했습니다. EMG 핵심 소스 7개 파일의 작업 전후 SHA256이 같은지 확인했습니다.

EXTRACTED: 실제 정리 결과는 구버전 실행 폴더 7개, 이전 Windows 캐시 5개, 이전 ZIP/해시 14개, 이전 검사/실수신 보고서 9개로 총 35개 항목 삭제입니다. 런타임 파일 66개 사본을 버전별로 백업하고 해시를 검증했으며, 최신 폴더에는 상대 경로가 고유한 파일 51개를 합쳤습니다. 백업 파일과 최신 폴더의 최종 선택 파일을 모두 다시 해시 검증했습니다. 현재 dist_windows_current와 최신 ZIP 한 개만 남아 있음을 확인했습니다. 최신 ZIP은 사용자 설정·음원·기록을 포함하지 않습니다.

EXTRACTED: 정리 직후 보존된 현재 EMG 설정은 unfiltered, ON=32.462, OFF=19.606이었습니다. 이는 구버전 중 가장 최근에 저장된 설정 파일을 복사한 결과이며 새로 계산한 값이 아닙니다.

TODO: 물리 카메라에서 두 손가락 인식과 드래그 감도를 확인합니다. Windows EXE는 `dist_windows_current/EMG-Motion-Rhythm-No-Bandpass/EMG-Motion-Rhythm-No-Bandpass.exe`를 사용합니다.

[손 커서 Mermaid](../diagrams/hand-cursor.md)는 Mermaid 지원 미리보기로 열고, Graphify는 저장소 루트에서 `graphify .`로 수동 실행합니다.
