# 🎧 Gemini STT (Speech-to-Text) 코드 라인별(Line-by-Line) 완벽 해설

이 문서는 Google AI Studio의 전용 오디오 전사 모델인 **`gemini-3.5-transcribe`**를 사용하여 로컬 음성 파일(`.wav`)을 실시간 텍스트로 변환(STT)하는 [`gemini_stt.py`](gemini_stt.py)의 모든 코드를 줄 단위로 상세히 설명합니다.

---

## 📌 전체 동작 흐름 요약

1. **클라이언트 초기화**: 환경변수의 `GEMINI_API_KEY`로 Google GenAI 클라이언트를 생성합니다.
2. **오디오 바이너리 로드**: 지정된 경로의 `.wav` 음성 파일을 바이너리(`rb`) 모드로 읽어 메모리에 올립니다.
3. **멀티모달 Content 구성**: `types.Part.from_bytes()`를 사용하여 원시 오디오 바이트 데이터와 MIME 타입을 `parts`에 주입합니다.
4. **전사 고급 옵션 설정**: 단어 단위 타임스탬프(`word_timestamp`) 및 화자 분리(`diarization`) 옵션을 활성화합니다.
5. **실시간 스트리밍 출력**: `generate_content_stream`을 통해 모델이 음성을 인식하는 즉시 터미널에 한 글자씩 실시간으로 전사 결과를 출력합니다.

---

## 🔍 Line-by-Line 상세 코드 해설

### 1행 ~ 6행: 라이브러리 임포트 및 SDK 로드

```python
1: import os
2: import sys
3: # pyrefly: ignore [missing-import]
4: from google import genai
5: # pyrefly: ignore [missing-import]
6: from google.genai import types
```

* **1행 (`import os`)**: 시스템 환경변수에서 `GEMINI_API_KEY`를 가져오기 위한 파이썬 표준 라이브러리입니다.
* **2행 (`import sys`)**: 터미널 명령행 인자(`sys.argv`)를 통해 사용자가 원하는 오디오 파일명을 직접 입력받기 위해 사용합니다.
* **4행 (`from google import genai`)**: Google GenAI 공식 최신 SDK의 메인 클라이언트 클래스를 가져옵니다.
* **6행 (`from google.genai import types`)**: 콘텐츠 객체(`Content`), 파트(`Part`), 전사 설정(`AudioTranscriptionConfig`) 등 구조화된 데이터 타입을 정의하기 위해 가져옵니다.

---

### 8행 ~ 11행: 메인 함수 선언 및 클라이언트 인증

```python
8: def generate():
9:     client = genai.Client(
10:         api_key=os.environ.get("GEMINI_API_KEY"),
11:     )
```

* **8행**: 음성 인식 및 전사를 수행하는 메인 함수 `generate()`를 정의합니다.
* **9~11행**: `os.environ.get("GEMINI_API_KEY")`로 API 키를 안전하게 읽어와 Google GenAI 클라이언트 인스턴스(`client`)를 초기화합니다.

---

### 13행 ~ 18행: 오디오 파일 경로 지정 및 바이너리 읽기

```python
13:     # 전사할 오디오 파일 (기본값: gemini_4_announcement.wav)
14:     audio_file = sys.argv[1] if len(sys.argv) > 1 else "gemini_4_announcement.wav"
15: 
16:     with open(audio_file, "rb") as f:
17:         audio_bytes = f.read()
```

* **14행**: 
  * 사용자가 터미널에서 `python3 gemini_stt.py "내파일.wav"` 형태로 파일명을 넘기면 `sys.argv[1]`을 타겟 파일로 지정합니다.
  * 별도의 인자를 주지 않고 실행하면 기본값으로 앞서 TTS로 생성했던 **`gemini_4_announcement.wav`**를 사용합니다.
* **16행 (`with open(audio_file, "rb") as f:`)**: 오디오 파일은 텍스트가 아닌 바이너리 음원 데이터이므로 반드시 읽기 바이너리(`"rb"`) 모드로 엽니다. `with` 문을 사용하여 작업 완료 후 파일이 자동으로 안전하게 닫히도록 보장합니다.
* **17행 (`audio_bytes = f.read()`)**: 파일 전체의 원시 바이너리 바이트 데이터를 읽어 메모리의 `audio_bytes` 변수에 담습니다.

---

### 20행 ~ 33행: 모델 지정 및 멀티모달 Content 구성

```python
20:     model = "gemini-3.5-transcribe"
21:     contents = [
22:         types.Content(
23:             role="user",
24:             parts=[
25:                 # 오디오 파일을 바이너리로 전달
26:                 types.Part.from_bytes(
27:                     data=audio_bytes,
28:                     mime_type="audio/wav",
29:                 ),
30:                 types.Part.from_text(text=""),
31:             ],
32:         ),
33:     ]
```

* **20행 (`model = "gemini-3.5-transcribe"`)**: 오디오 음성 인식 및 전사에 특화된 구글의 전용 STT 모델을 타겟으로 지정합니다.
* **21~23행**: 사용자 요청 역할을 나타내는 `role="user"`의 `types.Content` 객체를 리스트로 감쌉니다.
* **26~29행 (`types.Part.from_bytes(...)`)**: **[오디오 주입 핵심]**
  * 메모리에 읽어둔 `audio_bytes`와 함께 오디오 규격을 알리는 `mime_type="audio/wav"`를 지정하여 모델에 직접 바이트 스트림을 넘깁니다.
  * 복잡한 클라우드 업로드 과정 없이 로컬 파일을 즉시 전송할 수 있는 가장 간결한 방식입니다.
* **30행 (`types.Part.from_text(text="")`)**: 추가적인 텍스트 지시어(프롬프트) 자리입니다. 특정 번역 요구나 요약이 필요한 경우 여기에 텍스트를 추가할 수 있습니다.

---

### 34행 ~ 39행: 고급 오디오 전사 설정 (`AudioTranscriptionConfig`)

```python
34:     generate_content_config = types.GenerateContentConfig(
35:         audio_transcription_config=types.AudioTranscriptionConfig(
36:             word_timestamp=True,
37:             diarization=True,
38:         ),
39:     )
```

* **34~35행**: 전사 모델 전용 고급 옵션을 전달하기 위해 `audio_transcription_config`를 생성합니다.
* **36행 (`word_timestamp=True`)**:
  * 음성 인식 결과에 각 단어별 시작/종료 시점의 정밀한 **타임스탬프(시간 정보)**를 모델이 함께 산출하도록 활성화합니다. (자막 제작 시 유용)
* **37행 (`diarization=True`)**:
  * 여러 명의 화자가 대화하는 경우 "화자 1", "화자 2"와 같이 **발화자를 자동으로 구분(화자 분리)**하도록 요청합니다.

---

### 41행 ~ 47행: 실시간 스트리밍 출력 루프

```python
41:     for chunk in client.models.generate_content_stream(
42:         model=model,
43:         contents=contents,
44:         config=generate_content_config,
45:     ):
46:         if text := chunk.text:
47:             print(text, end="")
```

* **41~45행 (`client.models.generate_content_stream`)**:
  * 전체 음성 파일의 처리가 끝날 때까지 멍하니 기다리지 않고, 모델이 음성을 듣고 분석하는 즉시 텍스트 조각을 전달받는 **스트리밍 제너레이터**입니다.
* **46~47행 (`if text := chunk.text: print(text, end="")`)**:
  * 파이썬의 바다코끼리 연산자(`:=`)를 사용하여 수신된 청크에 텍스트가 있을 때만 `text` 변수에 할당하고, 줄바꿈 없이(`end=""`) 터미널에 한 글자씩 실시간으로 출력합니다.

---

### 50행 ~ 51행: 실행 진입점

```python
50: if __name__ == "__main__":
51:     generate()
```

* **50~51행**: 터미널에서 `python3 gemini_stt.py` 명령으로 파일을 직접 실행했을 때 `generate()` 함수를 호출하여 전사를 시작합니다.

---

## 🚀 실행 방법

```bash
# 1. 기본 오디오 파일 전사 (gemini_4_announcement.wav)
python3 gemini_stt.py

# 2. 다른 오디오 파일 지정 전사
python3 gemini_stt.py "회의녹음.wav"
```

실행하면 오디오 속 음성이 즉시 터미널 화면에 실시간으로 타이핑되듯 전사됩니다!
