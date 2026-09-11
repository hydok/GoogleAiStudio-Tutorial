# 🎬 hydok VIDEO JOURNAL & YouTube AI Chat

> **hydok VIDEO JOURNAL**은 따뜻하고 우아한 저널 감성의 UI 위에서 **유튜브 영상 실시간 감상**, **Google Gemini AI 심층 대화**, **스마트 타임스탬프**, 그리고 **0초 인메모리 캐싱 & 히스토리 동기화**를 결합한 최고 수준의 멀티미디어 비디오 저널 웹 애플리케이션입니다.

---

## 🌟 최신 주요 기능 및 특징 (Key Features)

### 1. 🎨 감성적인 저널 디자인 & 2단계 인터페이스
* **프리미엄 저널 톤앤매너**:
  * 차분하고 따뜻한 웜 베이지(`--bg-canvas: #eae6de`) 톤과 정갈한 라운드 카드 레이아웃
  * 우아한 타이포그래피: 영문 로고(`Playfair Display`), 감성 명조 타이틀(`Noto Serif KR`), 본문(`Pretendard`)
* **집중형 2단계 뷰(View) 전환**:
  * **[VIEW 1] 랜딩 뷰**: 첫 진입 시 영상 URL 입력에 온전히 몰입할 수 있는 미니멀 UI 및 최근 시청 기록 카드 제공
  * **[VIEW 2] 워크스페이스 뷰**: 영상 로드 시 2컬럼 레이아웃(좌측 비디오 플레이어 + 우측 AI 대화/타임스탬프)으로 자연스럽게 전환
  * 좌측 상단 로고(`hydok`)를 클릭하면 언제든 첫 화면으로 즉시 복귀

### 2. 🎬 스마트 영상 플레이어 & 실시간 메타데이터
* **`yt-dlp` 백엔드 엔진 연동**:
  * 11자리 영상 고유 ID, 일반 유튜브 URL, 단축 URL(`youtu.be`), 모바일 링크뿐만 아니라 **검색어 및 `search_query` URL**까지 완벽 지원
  * 영상 제목, 채널명, 프로필 이니셜, 조회수, 업로드 일자, 구독자 수, 좋아요 수, 영상 설명문 실시간 추출 및 표시
* **반응형 16:9 임베드 플레이어**: 깔끔한 유튜브 IFrame으로 잡음 없이 영상에 몰입

### 3. 💬 Google Gemini AI 실시간 대화 & 추천 질문
* **영상 맞춤형 AI 컨텍스트 분석**:
  * 시청 중인 영상의 제목, 채널, 자막, 영상 설명을 기반으로 깊이 있는 문답 지원
* **원클릭 추천 질문 칩 (Prompt Chips)**:
  * `📌 3줄 요약`: 영상의 핵심 줄거리를 3문장으로 간결하게 요약
  * `🎯 인터뷰 부분만`: 주요 인터뷰 및 핵심 발언 구간 안내
  * `🎬 비슷한 영상`: 감상 중인 영상과 분위기·주제가 어울리는 영상 3편 추천
* **세련된 말풍선 UI & 마크다운 렌더링**: 볼드, 리스트, 인용구 등 마크다운 스타일 완벽 적용
* **한글(IME) 조합 문자 중복 입력 방지**: `isComposing` 상태 및 `compositionstart/end` 감지를 통해 '안녕' 입력 후 엔터 시 마지막 글자('녕')가 중복 전송되는 버그를 원천 차단

### 4. 📋 100% 보장 실제 유튜브 직통 URL(`watch?v=...`) 복사 시스템
* **LLM 할루시네이션 가짜 링크 원천 차단**:
  * AI가 추천 영상을 알려줄 때 `POST /api/resolve-video-url` 백엔드 엔드포인트를 통해 실시간 `yt-dlp` 탐색(`ytsearch1:`)을 수행하여 **실제 존재하는 영상의 11자리 직통 URL(`https://www.youtube.com/watch?v=REAL_ID`)**을 0.5초 만에 정확히 조회
* **안전한 복사 파이프라인**:
  * 최신 `navigator.clipboard` 실패 시 숨김 텍스트에어리어 기반 `document.execCommand('copy')` Fallback을 적용하여 어떤 환경에서도 100% 클립보드 복사 보장
  * 복사 성공 시 화면 상단에 세련된 **플로팅 알림 토스트(`hydok-toast`)** 표시

### 5. ⏱️ 스마트 타임스탬프 & 즉시 이동 (Seek & Play)
* **3단계 타임스탬프 수집 우선순위**:
  1. 유튜브 원본 메타데이터에 등록된 챕터
  2. 브라우저 로컬스토리지(`localStorage`)에 저장된 캐시
  3. Gemini AI 실시간 자막 분석 및 챕터 자동 생성
* **원클릭 재생 연동**:
  * 챕터 목록 클릭 시 YouTube IFrame PostMessage API를 통해 해당 초(`seekTo`)로 즉시 이동 후 자동 재생(`playVideo`)

### 6. 🚀 실시간 로딩 프로그레스 (Progress Controller)
* **YouTube / NProgress 스타일 최상단 슬릭 프로그레스 바**:
  * 영상 로드 및 분석 시 화면 최상단에 버건디-코랄 그라데이션(`bg-gradient-to-r from-[#923826] to-[#e07a5f]`)의 매끄러운 프로그레스 바가 차오름
* **중앙 글래스모피즘 진행률 인디케이터 모달**:
  * 회전 링 애니메이션과 함께 실시간 퍼센트 게이지(`10% → 100%`) 및 단계별 친절한 안내 문구 표시
* **상단 미니 검색창 및 AI 타임스탬프 분석 시에도 상태 피드백 실시간 연동**

### 7. 🔙 브라우저 뒤로가기 / 앞으로가기 SPA 완벽 동기화
* **IFrame 히스토리 오염 방지**:
  * 영상 전환 시 IFrame 노드를 클린 교체(`replaceChild`)하여 브라우저 히스토리 스택이 IFrame 서브프레임 이동으로 오염되는 현상 원천 차단
* **웹앱 전체 상태 동기화 (`pushState` & `popstate`)**:
  * 브라우저 뒤로가기/앞으로가기 시 **영상 플레이어뿐만 아니라 좌측 메타데이터(제목, 채널, 설명) + 우측 AI 대화창 + 타임스탬프 + 상단 URL 입력창까지 모든 컨텐츠가 동기화되어 온전히 복원**

### 8. ⚡ 0초 인메모리 스마트 캐싱 시스템 (Instant Restore Cache)
* **`videoDataCache` & `videoChatCache`**:
  * 한 번 조회한 영상의 메타데이터와 타임스탬프는 메모리에 자동 캐싱
  * 해당 영상에서 AI와 나누었던 **질문과 답변 말풍선 내역까지 영상별로 자동 백업**
* **뒤로가기 시 0초 즉각 렌더링**:
  * 이미 조회했던 영상으로 뒤로가기/앞으로가기를 할 경우, **로딩 프로그레스 모달 없이 0.001초 만에 영상과 이전 대화 기록까지 완벽 복원**

### 9. ⚙️ 편리한 Gemini API Key 관리
* 시스템 환경변수(`GEMINI_API_KEY`) 지원
* 화면 우측 상단의 **⚙️ 톱니바퀴 버튼**을 통해 브라우저 로컬스토리지에 개인 API 키를 직접 저장/관리 가능

---

## 📂 프로젝트 구조

```plaintext
youtube_reel_ai/
├── main.py              # FastAPI 서버, REST API 엔드포인트 및 정적 파일(/static) 마운트
├── gemini_chat.py       # Google Gemini 3.6 Flash / 2.5 Flash 기반 비디오 컨텍스트 대화 엔진
├── video_helper.py      # yt-dlp 기반 유튜브 URL 파싱, 검색어 처리 및 실시간 메타데이터 추출기
├── static/              # 정적 에셋 (CSS / JS 분리 모듈)
│   ├── css/
│   │   └── style.css    # 웜 베이지 테마 변수, 커스텀 스크롤바, 마크다운 스타일시트
│   └── js/
│       └── app.js       # SPA 상태 관리, 캐싱, 히스토리 동기화, AI 대화, 타임스탬프, IME 처리 등
├── templates/
│   └── index.html       # 감성 저널 UI 1:1 정밀 재현 반응형 프론트엔드 (순수 HTML 템플릿 마크업)
├── requirements.txt     # FastAPI, Uvicorn, yt-dlp, Google GenAI 등 의존성 목록
├── PROJECT_CONTEXT.md   # AI 간 맥락 인계 및 아키텍처 명세서
└── README.md            # 상세 사용 및 기능 설명서
```

---

## 🛠️ 주요 기술 스택

* **Backend**: Python 3.10+, FastAPI, Uvicorn, yt-dlp, Google GenAI SDK (Gemini 2.5 Flash / 3.6 Flash)
* **Frontend**: HTML5, Vanilla JavaScript (ES6+), Tailwind CSS (CDN), Google Fonts (Playfair Display, Noto Serif KR, Pretendard)
* **Browser APIs**: History API (`pushState`, `popstate`), YouTube IFrame Player API, Clipboard API, LocalStorage, In-Memory Map Cache

---

## 🚀 설치 및 실행 방법

### 1. 필수 패키지 설치

터미널에서 아래 명령어를 실행하여 필수 의존성을 설치합니다:

```bash
cd youtube_reel_ai
pip install -r requirements.txt
```

### 2. Gemini API 키 설정

환경변수로 설정하거나, 웹페이지 접속 후 우측 상단의 **⚙️ 톱니바퀴 아이콘**을 클릭하여 직접 입력할 수 있습니다:

```bash
export GEMINI_API_KEY="your_gemini_api_key_here"
```

### 3. FastAPI 서버 실행

개발 모드로 서버를 실행합니다:

```bash
uvicorn main:app --reload --port 8000
```

### 4. 브라우저 접속

웹 브라우저에서 아래 주소로 접속합니다:
👉 **`http://localhost:8000`**

---

## 💡 사용 팁 (User Guide)

1. **시작하기**: 랜딩 페이지 입력창에 원하는 유튜브 동영상 URL을 붙여넣고 `시작하기 →`를 클릭합니다.
2. **AI 대화 나누기**: 영상이 재생되면 우측 채팅창의 추천 칩(`3줄 요약`, `비슷한 영상` 등)을 누르거나 직접 궁금한 내용을 질문해 보세요.
3. **비슷한 영상 직통 링크 복사**: AI가 추천해 준 영상 목록 아래의 `[📋 링크복사]` 버튼을 누르면 즉시 해당 영상의 실제 유튜브 링크가 클립보드에 복사됩니다.
4. **타임스탬프 이동**: 우측 `타임스탬프` 탭을 선택하고 원하는 챕터를 클릭하면 영상의 해당 구간으로 즉시 이동하여 재생됩니다.
5. **뒤로가기/앞으로가기**: 여러 영상을 탐색한 후 브라우저의 뒤로가기(←) 버튼을 눌러보세요. 0초 만에 이전 영상과 나눴던 대화 내용까지 즉시 복원됩니다!
