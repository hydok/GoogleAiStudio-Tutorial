# 🎙️ YouTube Audio Transcriber & History with Google Gemini

유튜브 영상 URL을 입력하면 자동으로 오디오를 추출/다운로드하고 **Google Gemini 3.6 Flash 모델**을 통해 **고품질 발화 전문(Full Transcript), AI 3줄 요약, 주요 구간 타임스탬프**를 생성하며, **과거 변환 기록(History)을 언제든 다시 열람하고 다운로드**할 수 있는 웹 애플리케이션입니다.

---

## ✨ 주요 기능

1. **간편한 링크 입력 & 영상 미리보기**:
   * 일반 유튜브 영상, 단축 링크(`youtu.be`), Shorts 링크 완벽 지원
   * 영상 썸네일, 제목, 채널명, 재생시간 실시간 카드 표시
2. **무손실 고음질 오디오 추출**:
   * `yt-dlp` 엔진을 탑재하여 최적의 오디오 스트림(`m4a`/`mp3`) 무손실 다운로드
3. **Gemini 3.6 Flash 기반 멀티모달 STT & 분석**:
   * 한국어 및 다국어 음성을 정확하고 매끄러운 문장으로 전사
   * 긴 오디오(20MB 초과)는 Google Files API를 통해 끊김 없이 안정적으로 처리
   * **[1. 핵심 3줄 요약 & 키워드]**, **[2. 주요 구간별 타임스탬프 요약]**, **[3. 전체 발화 전문]**의 3단계 구조화 리포트 생성
4. **📜 변환 히스토리(History) 관리 페이지**:
   * 지금까지 변환했던 모든 영상의 기록을 로컬 JSON(`history.json`)에 영구 저장
   * 영상 제목/채널명 검색 필터링 지원
   * 이전 영상의 오디오 다시 듣기 및 트랜스크립트 텍스트(.txt) 재다운로드
   * 개별 기록 삭제 및 전체 초기화 지원
5. **인터랙티브 웹 UX (Streamlit)**:
   * 좌측 사이드바 메뉴를 통해 **[🎙️ 새 영상 변환]**과 **[📜 변환 기록(History)]**을 자유롭게 이동

---

## 📂 파일 구조

```plaintext
youtube_transcriber/
├── app.py              # Streamlit 기반 메인 웹 애플리케이션 UI (네비게이션 탑재)
├── downloader.py       # yt-dlp 기반 유튜브 오디오 다운로드 모듈
├── transcriber.py      # Google GenAI 기반 오디오 전사 및 요약 모듈
├── history_manager.py  # ✨ [신규] 변환 이력(History) 로컬 저장 및 검색/관리 모듈
├── history.json        # ✨ [자동 생성] 변환 이력 데이터베이스 파일
├── downloads/          # 다운로드된 오디오 저장소
├── requirements.txt    # 필수 라이브러리 목록
└── README.md           # 사용 설명서
```

---

## 🚀 설치 및 실행 방법

### 1. 가상환경 활성화 및 필수 패키지 설치

터미널에서 아래 명령어를 실행하여 필요한 라이브러리를 설치합니다:

```bash
cd youtube_transcriber
pip install -r requirements.txt
```

### 2. Gemini API 키 설정

시스템 환경변수에 API 키를 설정하거나, 웹 화면 좌측 사이드바에 직접 입력하실 수 있습니다:

```bash
export GEMINI_API_KEY="본인의_구글_API_키"
```

### 3. 웹 애플리케이션 실행

아래 명령어로 Streamlit 웹 서버를 시작합니다:

```bash
streamlit run app.py
```

명령어를 실행하면 브라우저에 `http://localhost:8501` 웹페이지가 자동으로 열립니다!
