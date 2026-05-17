# 리듬 노트 생성기

업로드한 오디오 파일을 분석해 4레인 리듬게임 노트를 자동으로 생성하는 풀스택 프로토타입입니다. 웹 UI에서 파형과 타임라인을 미리 보고 JSON/CSV로 내보낼 수 있습니다.

## 기능

- mp3, wav, ogg 업로드
- BPM 감지
- Beat/Onset 추출
- 난이도 기반 노트 생성
- 4+ 레인 리듬 노트 차트
- 파형 미리보기(비트/노트 마커)
- 노트 타임라인 미리보기
- JSON/CSV 내보내기
- 웹 리듬게임 플레이(4키 탭)
- 점수/콤보/정확도/판정 통계
- Tap/Accent/Long/Chain 노트 타입
- long/chain 홀드형 판정(keydown/keyup)
- 게임 플레이 비주얼(히트 플래시, 판정 배너, 콤보 펄스)
- PowerShell 스크립트로 백엔드+프론트엔드 동시 실행

## 폴더 구조

```
rhythm-note-generator/
├── backend/
│   ├── main.py
│   ├── audio_analyzer.py
│   ├── note_generator.py
│   ├── export_utils.py
│   ├── schemas.py
│   ├── requirements.txt
│   ├── uploads/
│   └── outputs/
├── frontend/
│   ├── package.json
│   ├── index.html
│   ├── vite.config.js
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── api.js
│       ├── styles.css
│       └── components/
│           ├── UploadPanel.jsx
│           ├── AnalysisPanel.jsx
│           ├── WaveformViewer.jsx
│           ├── NoteTimeline.jsx
│           └── ExportPanel.jsx
├── README.md
└── run_dev.md
```

## 설치

백엔드 의존성: backend/requirements.txt

프론트엔드 의존성: frontend/package.json

## 실행(요약)

Windows PowerShell 명령은 run_dev.md를 참고하세요.

백엔드/프론트엔드를 동시에 실행:

```powershell
./run_all.ps1
```

## API 목록

- GET /
- POST /api/upload
- POST /api/analyze
- POST /api/generate-notes
- GET /api/export/json/{file_id}
- GET /api/export/csv/{file_id}
- GET /api/audio/{file_id}

## 게임 플레이

노트 생성 후 "Play Game"을 클릭하면 4키 리듬게임 플레이 화면이 열립니다.

### 조작(4레인)

- Lane 0: D
- Lane 1: F
- Lane 2: J
- Lane 3: K

### 판정 기준

- Perfect: ±0.050s
- Great: ±0.100s
- Good: ±0.150s
- Miss: > ±0.180s (자동 미스)

노트 타입과 길이에 따라 판정 윈도우가 약간 보정됩니다.

### 점수

- Perfect: 1000
- Great: 700
- Good: 400
- Miss: 0

정확도 계산식:

$$\text{accuracy} = \frac{\text{score}}{\text{notes} \times 1000} \times 100$$

### 게임 흐름

1. 오디오 업로드
2. 분석(Analyze)
3. 노트 생성(Generate Notes)
4. 타임라인 미리보기
5. Play Game
6. Start
7. D/F/J/K로 플레이
8. 결과 확인

## 차트 JSON 포맷

```json
{
  "version": "0.1.0",
  "file_id": "abc123",
  "title": "sample",
  "bpm": 128.0,
  "offset": 0.0,
  "difficulty": "normal",
  "lanes": 4,
  "duration": 180.5,
  "notes": [
    {
      "time": 1.245,
      "lane": 2,
      "type": "tap",
      "length": 0.0
    }
  ]
}
```

노트 타입:

 - `tap`: 기본 단타
 - `accent`: 강조 단타
 - `long`: 길게 유지하는 노트(hold-like)
 - `chain`: 짧은 연결형 롱 노트

## 한계점

- 분석 정확도는 오디오 품질에 영향을 받습니다.
- 차트는 간단한 휴리스틱과 패턴으로 생성됩니다.
- 차트는 메모리에 저장되어 서버 재시작 시 사라집니다.
- long/chain은 홀드형이지만 틱 점수 등 완전한 홀드 채점은 아직 없습니다.
- 자동 채보는 초안 수준입니다.
- 수동 노트 편집은 지원하지 않습니다.
- 브라우저 오디오 지연으로 오프셋 보정이 필요할 수 있습니다.

## 향후 개선

- Hold note 지원
- 섹션/다운비트 감지
- 수동 노트 편집
- Unity/Godot 및 osu!mania 포맷 내보내기
