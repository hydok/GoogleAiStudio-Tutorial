# ⚡ YouTube Audio Transcriber (FastAPI & Modern Web UI)

고성능 비동기 파이썬 웹 프레임워크인 **FastAPI**와 현대적인 **HTML5/Tailwind CSS 프론트엔드**를 결합하여, 유튜브 영상 URL로부터 고음질 오디오를 다운로드하고 **Google Gemini 3.6 Flash 모델**을 통해 발화 전문 전사, AI 3줄 요약, 타임스탬프를 추출하며 히스토리를 관리하는 독립 웹 서비스입니다.

---

## ✨ 주요 기능 및 특징

1. **상단 모던 네비게이션 UI (Top Navigation Bar)**:
   * 깔끔하고 미니멀한 상단 헤더에 **`🎙️ 새 영상 변환`**과 **`📜 변환 기록 (History)`** 탭 배치
   * 별도의 화면 깜빡임 없이 매끄러운 단일 페이지 애플리케이션(SPA) 경험 제공
2. **RESTful API 백엔드 (FastAPI)**:
   * `POST /api/info`: 영상 메타데이터(제목, 채널, 썸네일, 길이) 파싱
   * `POST /api/transcribe`: `yt-dlp` 오디오 다운로드 + Gemini 3.6 Flash 전사/요약 + 자동 히스토리 누적
   * `GET /api/history`: 저장된 변환 내역 목록 반환 (검색 지원)
   * `DELETE /api/history/{id}`: 개별 기록 삭제 및 전체 초기화
   * `GET /downloads/{filename}`: 추출된 오디오 정적 스트리밍 제공
3. **무손실 오디오 추출 & 웹 플레이어**:
   * 영상에서 고음질 오디오(`.m4a`)를 다운로드하여 브라우저 내 오디오 플레이어에서 즉각 청취
4. **Gemini 3.6 Flash 3단계 리포트**:
   * **💡 1. 핵심 3줄 요약 & 키워드**
   * **⏱️ 2. 주요 구간별 타임스탬프 요약**
   * **📝 3. 전체 발화 전문 (Full Transcript)**
   * 마크다운 렌더링, 텍스트 클립보드 복사, `.txt` 파일 다운로드 지원
5. **히스토리 관리**:
   * 과거 작업했던 영상들의 오디오 다시 듣기, 전문 다시 보기, `.txt` 재다운로드

---

## 📂 파일 구조

```plaintext
youtube_transcriber_fastapi/
├── main.py              # FastAPI 서버 및 REST API 엔드포인트 라우터
├── downloader.py        # yt-dlp 기반 유튜브 오디오 다운로드 엔진
├── transcriber.py       # Google GenAI 기반 오디오 전사 및 요약 모듈
├── history_manager.py   # JSON 기반 변환 히스토리 관리자
├── history.json         # 변환 이력 데이터 파일 (자동 생성)
├── downloads/           # 다운로드된 오디오 저장소
├── templates/
│   └── index.html       # Tailwind CSS 기반 반응형 모던 웹 UI
├── requirements.txt     # 필수 패키지 목록
└── README.md            # 사용 설명서
```

---

## 🚀 설치 및 실행 방법

### 1. 패키지 설치

터미널에서 아래 명령어를 실행하여 필요한 의존성을 설치합니다:

```bash
cd youtube_transcriber_fastapi
pip install -r requirements.txt
```

### 2. Gemini API Key 설정

시스템 환경변수에 등록하거나, 웹페이지 우측 상단의 **톱니바퀴(⚙️)** 버튼을 눌러 브라우저에 직접 저장하실 수 있습니다:

```bash
export GEMINI_API_KEY="본인의_구글_API_키"
```

### 3. FastAPI 서버 구동

아래 명령어로 Uvicorn 개발 서버를 실행합니다:

```bash
uvicorn main:app --reload --port 8000
```

실행 후 브라우저에서 **`http://localhost:8000`**에 접속하시면 완성된 웹 서비스를 이용하실 수 있습니다!
