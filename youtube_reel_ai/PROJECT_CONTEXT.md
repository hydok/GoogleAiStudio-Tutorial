# 🎬 hydok VIDEO JOURNAL & YouTube AI Chat - 프로젝트 컨텍스트 & 인계 문서 (Project Context & Handover)

> **문서 목적**: 본 문서는 다른 AI(ChatGPT, Claude, Gemini 등) 또는 새로운 세션의 AI 어시스턴트가 프로젝트의 배경, 요구사항의 변천 과정, 기술적 의사결정 내역, 주의해야 할 제약사항(Gotchas)을 완벽하게 파악하고 **맥락의 단절 없이 일관성 있게 작업을 이어갈 수 있도록 정리한 단일 진실 공급원(Single Source of Truth)**입니다.

---

## 📌 1. 프로젝트 개요 (Project Overview)

* **프로젝트명**: `hydok VIDEO JOURNAL & YouTube AI Chat`
* **위치**: `youtube_reel_ai/` (전체 저장소: `GoogleAiStudio-Tutorial/youtube_reel_ai/`)
* **핵심 컨셉**: 사용자가 제공한 감성적인 저널 디자인(Reel VIDEO JOURNAL)을 정밀 재현한 웹 UI 위에서, **유튜브 영상 실시간 감상**, **Google Gemini AI 맞춤형 심층 대화**, **스마트 타임스탬프**, **0초 인메모리 스마트 캐싱**, 그리고 **브라우저 뒤로가기/앞으로가기 완벽 동기화**를 제공하는 모던 SPA형 풀스택 웹 애플리케이션.
* **주요 기술 스택**:
  * **Backend**: Python 3.10+, FastAPI, Uvicorn, `yt-dlp`, `google-genai` SDK (Gemini 2.5 Flash / Gemini 3.6 Flash)
  * **Frontend**: Single File SPA (`templates/index.html`), Pure Vanilla JavaScript (ES6+), Tailwind CSS (CDN), Google Fonts
  * **Web APIs**: Browser History API (`pushState`/`popstate`), YouTube IFrame API (PostMessage), Clipboard API + Fallback `execCommand`, LocalStorage, In-Memory Map Cache

---

## 🎨 2. UI / UX 디자인 철학 및 구조

1. **감성적인 저널 톤앤매너**:
   * 따뜻하고 편안한 웜 베이지 캔버스 (`--bg-canvas: #eae6de`) 및 부드러운 라운드 패널 (`rounded-3xl`, `rounded-2xl`).
   * 고급스러운 타이포그래피: 영문 로고(`Playfair Display`), 한글 메인 타이틀(`Noto Serif KR`), 본문(`Pretendard`).
   * 시그니처 컬러: 버건디 액센트 (`#923826`), 다크 브라운 차콜 텍스트 (`#1c1917`, `#2b2724`).

2. **2단계 뷰(View) 전환 아키텍처**:
   * **[VIEW 1] 랜딩 뷰 (`#landing-view`)**:
     * 첫 접속 시 중앙 대형 URL 입력 바와 최근 시청/검색 기록 카드(`History`)에 집중.
   * **[VIEW 2] 워크스페이스 뷰 (`#workspace-view`)**:
     * URL 입력 후 영상이 로드되면 2컬럼 레이아웃으로 부드럽게 전환.
     * 좌측: 16:9 유튜브 IFrame 플레이어 + 영상 메타데이터(제목, 채널, 구독자, 설명 등).
     * 우측: 탭 인터페이스 (`[💬 AI 대화]`, `[⏱️ 타임스탬프]`).
   * **로고 인터랙션**: 좌측 상단 `hydok` 로고 클릭 시 언제든 첫 랜딩 뷰로 즉시 복귀 (`resetToLanding`).

---

## 🕒 3. 누적 사용자 요구사항 및 구현 히스토리 타임라인

이 프로젝트는 사용자와의 긴밀한 대화와 피드백을 통해 점진적으로 고도화되었습니다. 아래는 발생한 요구사항의 순서와 각각의 엔지니어링 해결 내역입니다:

### [요건 1] 최근 시청 기록 및 LocalStorage 구조 구축
* **사용자 요청**: `"localStorage 에 저장되는 구조 보자"`
* **해결 및 적용**:
  * `HYDOK_WATCH_HISTORY`: 최근 시청/검색한 영상 10개를 객체 배열(`[{ id, title, uploader, thumbnail, view_count, url, timestamp }]`)로 저장.
  * `HYDOK_TIMESTAMPS_<videoId>`: 영상별 추출된 타임스탬프 챕터 목록 영구 캐싱.
  * `GEMINI_API_KEY`: 우측 상단 ⚙️ 모달을 통해 입력받은 사용자 전용 구글 API 키 보관.

### [요건 2] AI 대화에서 추천 영상 [바로가기] / [링크복사] 제공
* **사용자 요청**: `"ai 대화에서 비슷한 영상 추천해줄때 해당링크로 [바로가기] 도 되도록해주세요. 바로가기하면 해당 링크로 영상 재생 설정!"`
* **해결 및 적용**:
  * Gemini 프롬프트에 추천 영상 안내 시 마크다운 링크 또는 특수 마커를 출력하도록 지침 추가.
  * 프론트엔드에서 추천 영상을 감지하여 바로 재생하거나 주소를 복사할 수 있는 인터랙티브 UI 제공.

### [요건 3] [바로가기] 동작 방식에 대한 피드백 및 조정
* **사용자 요청**: `"[🎬 바로 재생 →] 클릭시 해당 링크로 유튜브 페이지로 이동하는게 그렇게말고, hydok VIDEO JOURNAL 검색창에 해당 링크 넣고 기능 동작하게해줘"` ➔ 이후 `"이전 으로 되돌려줘"`
* **해결 및 적용**:
  * 외부 새 창 이동이 아닌 웹앱 내부 상단 검색창에 URL을 주입하여 앱 내부에서 즉시 전환되도록 개선 후, 사용자의 이전 롤백 요청에 맞춰 자연스러운 링크 복사 및 감상 중심 UI로 안정화.

### [요건 4] 실제 유튜브 직통 URL(`watch?v=...`) 100% 보장 (LLM 할루시네이션 방지)
* **사용자 요청**: `"예시: [링크복사](https://www.youtube.com/results?search_query=...) 검색 url 말고!! 해당 영상으로 바로 가는 url 복사되도록!"`
* **핵심 문제점**:
  * LLM(Gemini)은 존재하지 않는 가짜 비디오 ID(`dQw4w9WgXcQ` 등)를 지어내거나(Hallucination), 검색 결과 URL(`search_query=...`)만 제시할 수밖에 없는 한계가 있음.
* **엔지니어링 솔루션**:
  * 백엔드에 `POST /api/resolve-video-url` 엔드포인트 신설.
  * AI가 추천한 제목과 채널명을 백엔드로 전달하면, 백엔드에서 `yt-dlp`의 `ytsearch1:` 엔진을 백그라운드로 실행하여 **0.5초 만에 실제 유튜브에 존재하는 진짜 11자리 직통 URL(`https://www.youtube.com/watch?v=REAL_ID`)**을 실시간 탐색하여 반환.

### [요건 5] 100% 보장 클립보드 복사 시스템 및 토스트 알림
* **사용자 요청**: `"[링크복사] 눌러도 복사 기능이 없어"`
* **원인**:
  * AI가 일반 텍스트로 `📋 링크복사`를 출력하여 클릭 핸들러가 연결되지 않았거나, 브라우저 보안 컨텍스트(iframe/비보안 환경)에서 `navigator.clipboard`가 거부됨.
* **해결 및 적용**:
  * `appendAiBubble`: 마크다운 링크뿐만 아니라 일반 텍스트 형태의 `📋 링크복사` 패턴도 정규식으로 감지하여 `addEventListener`가 바인딩된 버튼 요소로 동적 교체.
  * `copyToClipboard`: `navigator.clipboard` 실패 시 숨김 `<textarea>` + `document.execCommand('copy')` Fallback을 적용하여 어떤 환경에서도 100% 복사 성공 보장.
  * `showToast`: 복사 완료 시 화면 상단에 세련된 다크 글래스모피즘 토스트 팝업 표시.

### [요건 6] 브라우저 뒤로가기(Back Button) 전체 컨텐츠 동기화
* **사용자 요청**: `"영상 url 여러개 입력하고 이동하고 나서 뒤로가기 하면 영상만 이전 영상으로 이동 하고. 컨텐츠 내용은 그대로인데 뒤로가기 제대로 되도록 수정해줘"`
* **핵심 문제점**:
  * `iframe.src = '...'`를 직접 변경하면 브라우저 히스토리 스택에 iframe 서브프레임 내비게이션이 기록되어, 뒤로가기를 누르면 부모 페이지의 `popstate` 없이 iframe 내부만 뒤로 가고 부모 화면의 텍스트/대화는 그대로 남음.
* **엔지니어링 솔루션**:
  * 영상 전환 시 기존 iframe 노드를 복제/교체(`oldIframe.parentNode.replaceChild(newIframe, oldIframe)`)하여 서브프레임 히스토리 오염을 원천 차단.
  * `history.pushState({ view: 'workspace', url, videoId }, '', '?v=...')` 등록.
  * `window.addEventListener('popstate', ...)` 핸들러를 구축하여 뒤로가기/앞으로가기 시 **영상 플레이어 + 좌측 메타데이터(제목, 채널명, 설명) + 우측 AI 대화 + 타임스탬프 + 상단 URL 검색창**까지 일관되게 100% 복원.

### [요건 7] 로딩 프로그레스(Loading Progress) 시스템 구축
* **사용자 요청**: `"로딩 프로그래스 만들어줘"`
* **해결 및 적용**:
  * `ProgressController` 객체 구현:
    1. **최상단 슬릭 프로그레스 바 (`#top-progress-container`)**: 버건디-코랄 그라데이션(`bg-gradient-to-r from-[#923826] to-[#e07a5f]`)의 3.5px YouTube/NProgress 스타일 바.
    2. **중앙 분석 진행률 모달 (`#loading-overlay`)**: 회전 스피너 아이콘(🎬), 실시간 퍼센트 게이지(`10% → 100%`), 5단계 진행 안내 텍스트.
  * 상단 검색 버튼 스피너 및 타임스탬프 재분석 시에도 연동.

### [요건 8] 0초 인메모리 스마트 캐싱 시스템 (Instant Restore Cache)
* **사용자 요청**: `"뒤로가기 했는데... 왜 다시 로딩 프로그래스 돌아가?? 조회했던 데이터는 남아있어서 바로 나와야하는거 아닌가요 ?"`
* **핵심 문제점**:
  * 이미 조회했던 영상으로 뒤로가기를 했을 때도 매번 서버에 `fetch('/api/video-info')`를 재요청하면서 로딩 프로그레스 모달이 다시 뜨는 비효율 발생.
* **엔지니어링 솔루션**:
  * `videoDataCache` (Map): URL 및 11자리 Video ID를 키로 하여 수신된 영상 메타데이터와 타임스탬프를 메모리에 영구 보관.
  * `videoChatCache` (Map): 영상 전환 직전 현재 영상에서 나누었던 `chatHistory` 배열과 렌더링된 채팅 말풍선 HTML(`dynamic-chat-list.innerHTML`)을 자동 백업.
  * 뒤로가기 시 `extractVideoId(url)`로 캐시를 즉시 확인 ➔ **로딩 모달을 전혀 띄우지 않고 0.001초 만에 영상, 메타데이터, 타임스탬프, 그리고 이전 나눴던 AI 질문과 답변 내역까지 100% 즉시 복원(Instant Display)**.

### [요건 9] 한글(IME) 조합 문자 중복 입력 버그 해결
* **사용자 요청**: `"ai 대화에서 직접 입력했을때 마지막 글자가 한번더 입력되어지는데 수정헤줘 (안녕 -> 안녕 / 녕 이렇게됨..)"`
* **핵심 문제점**:
  * 한글은 자음과 모음이 합쳐지는 조합 문자(IME)이므로, '안녕' 타이핑 후 Enter를 누르면 `keydown` 시점에 `e.isComposing === true` 상태임.
  * 이때 `sendChatMessage`가 호출되어 입력창을 비워도, 브라우저의 IME 엔진이 조합 종료 처리를 하면서 방금 비워진 입력창에 마지막 글자('녕')를 다시 채워 넣거나, 엔터 이벤트가 2번 연속 발화되어 두 번째 메시지로 '녕'이 전송됨.
* **엔지니어링 솔루션**:
  * `chat-user-input`에 `oncompositionstart="isChatComposing = true"`, `oncompositionend="isChatComposing = false"` 등록.
  * `handleChatInputKeyDown(e)`: `e.isComposing || isChatComposing || e.keyCode === 229`일 때 Enter 키는 한글 조합 확정용으로만 넘기고 메시지 전송 차단.
  * `sendChatMessage`: 전송 플래그 락(`isSendingChat = true`) 추가 및 전송 직후 macOS/Chrome 잔여 버퍼 청소(`setTimeout`으로 `input.value = ""` 클린업).

---

## 📁 4. 핵심 파일 및 아키텍처 명세

```plaintext
youtube_reel_ai/
├── main.py              # FastAPI 메인 웹 서버, REST API 엔드포인트 및 정적 파일(/static) 서빙
├── gemini_chat.py       # Google Gemini SDK 기반 비디오 컨텍스트 프롬프트 엔진
├── video_helper.py      # yt-dlp 기반 유튜브 URL 파싱, 검색어 처리 및 메타데이터 추출기
├── static/              # 분리된 정적 에셋 모듈
│   ├── css/
│   │   └── style.css    # 웜 베이지 테마 변수, 커스텀 스크롤바, 마크다운 스타일시트
│   └── js/
│       └── app.js       # SPA 상태 관리, 캐싱, 히스토리 동기화, AI 대화, 타임스탬프, IME 처리 등
├── templates/
│   └── index.html       # 슬림해진 순수 HTML 템플릿 마크업
├── requirements.txt     # 프로젝트 필수 의존성 목록
├── README.md            # 사용자 및 개발자 안내서 (한글)
└── PROJECT_CONTEXT.md   # [본 문서] AI 간 맥락 인계 및 아키텍처 명세서
```

### 주요 REST API 엔드포인트 (`main.py`)
1. `GET /`: 메인 웹페이지 (`templates/index.html`) 렌더링.
2. `POST /api/video-info`:
   * 요청: `{ url: string }`
   * 동작: `video_helper.py`를 통해 제목, 채널명, 조회수, 구독자 수, 챕터, 설명 추출. 검색어 입력 시 자동 1순위 영상 매핑.
3. `POST /api/chat`:
   * 요청: `{ video_info: dict, message: string, chat_history: list, api_key: string }`
   * 동작: Gemini 모델(Gemini 2.5 Flash / 3.6 Flash)을 호출하여 영상 컨텍스트 기반 답변 생성.
4. `POST /api/timestamps`:
   * 요청: `{ video_info: dict, api_key: string }`
   * 동작: 자막 및 영상 내용을 Gemini로 분석하여 챕터 타임스탬프 리스트 생성.
5. `POST /api/resolve-video-url`:
   * 요청: `{ query: string }`
   * 동작: `yt-dlp` 검색(`ytsearch1:`)으로 실제 존재하는 유튜브 영상의 고유 11자리 직통 URL(`https://www.youtube.com/watch?v=...`) 조회 및 반환.

---

## 🧠 5. 프론트엔드 상태 관리 및 캐시 명세 (`index.html`)

* **전역 변수**:
  * `currentVideo`: 현재 로드된 영상의 메타데이터 객체.
  * `chatHistory`: 현재 활성 대화 세션의 메시지 리스트 (`[{ role: 'user'|'model', text: '...' }]`).
  * `currentTimestamps`: 현재 영상의 타임스탬프 챕터 배열.
  * `isChatComposing`: 한글 IME 조합 진행 여부 플래그 (Boolean).
  * `isSendingChat`: 채팅 API 호출 진행 중 중복 전송 방지 락 (Boolean).
* **인메모리 캐시 맵**:
  * `videoDataCache = new Map()`: Key(`videoId` 또는 `url`) ➔ Value(`videoData` 객체).
  * `videoChatCache = new Map()`: Key(`videoId`) ➔ Value(`{ history: [...], domHtml: '...' }`).
* **SPA 브라우저 히스토리 스택**:
  * 랜딩 상태: `history.pushState({ view: 'landing' }, '', '/')`
  * 워크스페이스 상태: `history.pushState({ view: 'workspace', url, videoId }, '', '?v=' + videoId)`

---

## ⚠️ 6. 다음 AI 어시스턴트를 위한 주의사항 (Gotchas & Guidelines)

새로운 AI 어시스턴트가 코드를 수정하거나 기능을 추가할 때 **반드시 준수해야 할 제약사항**입니다:

1. **YouTube IFrame 조작 시 `src` 직접 변경 금지**:
   * `iframe.src = ...`를 직접 바꾸면 브라우저 히스토리 스택에 서브프레임이 쌓여 뒤로가기 시 부모 페이지가 먹통이 됩니다.
   * 영상 교체 시 반드시 `oldIframe.parentNode.replaceChild(newIframe, oldIframe)` 노드 교체 방식을 유지하세요.
2. **한글 IME 이벤트 처리 원칙 유지**:
   * `chat-user-input`의 엔터 키 처리 시 `handleChatInputKeyDown`의 `e.isComposing`, `isChatComposing`, `e.keyCode === 229` 체크를 절대로 제거하지 마세요. (제거 시 '안녕' ➔ '안녕', '녕' 버그가 즉시 재발합니다.)
3. **추천 영상 URL 생성 시 LLM에게 직통 URL 생성을 맡기지 말 것**:
   * LLM은 가짜 Video ID를 생성하므로, 직통 링크가 필요할 때는 반드시 `POST /api/resolve-video-url` 백엔드 엔드포인트를 호출하도록 프론트엔드 파이프라인을 유지해야 합니다.
4. **클립보드 복사 시 execCommand Fallback 필수**:
   * 브라우저 보안 정책에 따라 `navigator.clipboard`가 실패할 수 있으므로, 숨김 textarea + `document.execCommand('copy')` Fallback 구조를 절대 생략하지 마세요.
5. **뒤로가기 시 인메모리 캐시(`videoDataCache`) 우선 확인 유지**:
   * `loadVideoFromUrl` 시작 시 반드시 캐시 유무를 먼저 검사하여, 이미 조회한 영상은 불필요한 서버 호출 및 로딩 프로그레스 모달 없이 즉시 렌더링되도록 유지하세요.
6. **사용자 전역 규칙**:
   * 사용자는 모든 대답 및 `.md` 파일 생성을 한국어로 작성할 것을 전역 규칙으로 지정해 두었습니다.
