# 🎙️ Gemini 3.1 TTS (Text-to-Speech) 코드 라인별(Line-by-Line) 완벽 해설

이 문서는 Google AI Studio의 최신 음성 생성 모델인 **`gemini-3.1-flash-tts-preview`**를 사용하여 텍스트와 감정/상황 지시어를 기반으로 고품질 WAV 음성 파일을 생성하는 [`gemini_31_tts.py`](gemini_31_tts.py)의 모든 코드를 줄 단위로 상세히 설명합니다.

---

## 📌 전체 동작 흐름 요약

1. **라이브러리 로드 & 클라이언트 생성**: Google GenAI SDK를 초기화하고 API 키를 인증합니다.
2. **상황 및 대본(Prompt) 정의**: Scene(무대/공간 배경), Context(직전 상황), Transcript(감정 연기 지문이 포함된 대본)를 구조화합니다.
3. **음성 생성 설정 (SpeechConfig)**: 출력 형식을 `audio`로 지정하고, 음성 모델의 화자(`Kore`) 및 음조를 설정합니다.
4. **스트리밍 수신 & PCM 누적**: 모델로부터 실시간으로 쏟아져 나오는 오디오 PCM 스트림 청크들을 메모리 버퍼에 모읍니다.
5. **WAV 헤더 결합 & 파일 저장**: 순수 PCM 바이너리 데이터 앞에 RIFF WAV 헤더를 직접 바이너리로 조립하여 재생 가능한 완성형 `.wav` 파일로 저장합니다.

---

## 🔍 Line-by-Line 상세 코드 해설

### 1행 ~ 12행: 라이브러리 임포트 및 SDK 로드

```python
1: # To run this code you need to install the following dependencies:
2: # pip install google-genai
3: 
4: import mimetypes
5: import os
6: import re
7: import struct
8: # pyrefly: ignore [missing-import]
9: from google import genai
10: # pyrefly: ignore [missing-import]
11: from google.genai import types
12: 
```

* **1~2행**: 실행에 필요한 필수 라이브러리(`google-genai`) 설치 안내 주석입니다.
* **4행 (`import mimetypes`)**: 파일 형식이나 MIME 타입을 다룰 때 사용하는 파이썬 내장 모듈입니다.
* **5행 (`import os`)**: 환경변수(`GEMINI_API_KEY`)를 읽어오기 위한 파이썬 표준 라이브러리입니다.
* **6행 (`import re`)**: 정규 표현식을 지원하는 모듈입니다.
* **7행 (`import struct`)**: **[핵심 모듈]** 파이썬 데이터(정수, 바이트열 등)를 C 언어 구조체 스타일의 순수 바이너리 바이트(Binary Bytes)로 패킹(Pack)할 때 사용됩니다. WAV 파일 헤더를 수동 제작하는 데 필수적입니다.
* **9~11행 (`from google import genai`, `from google.genai import types`)**: 최신 구글 GenAI 공식 SDK 클라이언트 및 설정/입출력에 사용되는 타입 클래스(`GenerateContentConfig`, `Content`, `Part` 등)를 가져옵니다.

---

### 14행 ~ 19행: 바이너리 파일 저장 함수 (`save_binary_file`)

```python
14: def save_binary_file(file_name, data):
15:     f = open(file_name, "wb")
16:     f.write(data)
17:     f.close()
18:     print(f"File saved to to: {file_name}")
```

* **14행**: 완성된 바이너리 바이트 데이터를 디스크의 파일로 저장하는 헬퍼 함수 정의입니다.
* **15행**: 파일을 바이너리 쓰기 모드(`"wb"`)로 엽니다. 일반 텍스트가 아닌 오디오 음원 바이트이므로 반드시 `"wb"` 모드여야 합니다.
* **16행**: 메모리에 완성된 WAV 바이트 데이터를 디스크에 기록합니다.
* **17행**: 파일 핸들을 정상적으로 닫아 리소스를 해제합니다.
* **18행**: 저장이 완료된 파일 경로를 콘솔에 출력합니다.

---

### 21행 ~ 24행: 메인 생성 함수 및 모델 지정

```python
21: def generate():
22:     client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"),)
23: 
24:     model = "gemini-3.1-flash-tts-preview"
```

* **21행**: TTS 음성 생성 파이프라인 전체를 구동하는 메인 함수입니다.
* **22행**: 시스템 환경변수에 등록된 `GEMINI_API_KEY`를 읽어 Google GenAI 클라이언트 인스턴스를 생성합니다.
* **24행**: 구글의 최신 전용 음성 생성 프리뷰 모델인 **`gemini-3.1-flash-tts-preview`**를 타겟 모델로 지정합니다.

---

### 25행 ~ 46행: 고품질 음성 유도를 위한 3단계 프롬프트 구조

```python
25:     contents = [
26:         types.Content(
27:             role="user",
28:             parts=[
29:                 types.Part.from_text(text="""## Scene:
30: A large tech conference keynote hall with thousands of excited attendees, subtle room acoustics and echoing stage microphone ambiance.
31: 
32: ## Sample Context:
33: The presenter just unveiled the benchmark results of Gemini 4.0 to huge applause, and now pauses dramatically to announce the pricing.
34: 
35: ## Transcript:
36: [반갑고 신나는 목소리로]
37: 여러분, 깜짝 놀랄 만한 소식이 있습니다! 
38: [놀라움을 담아 빠르게]
39: 구글의 최신 모델 Gemini 4.0이 드디어 공개되었는데요, 놀라지 마세요! 
40: [비밀을 말하듯 살짝 뜸을 들이다가]
41: 이 엄청난 모델을, 정말 말도 안 되는 획기적인 가격으로 사용할 수 있게 되었습니다! 
42: [기분 좋은 밝은 목소리로]
43: 고성능 AI 개발 비용 때문에 고민 많으셨던 분들, 이제 걱정 끝입니다. 지금 바로 확인해 보세요!"""),
44:             ],
45:         ),
46:     ]
```

* **25~28행**: 모델에 전달할 `Content` 객체를 구성하고 역할(role)을 `"user"`로 지정합니다.
* **29~30행 (`## Scene:`)**: **[음향 공간감 설정]** 수천 명의 청중이 모인 거대한 테크 컨퍼런스 기조연설 홀의 미세한 룸 어쿠스틱과 무대 마이크 울림 환경을 묘사하여 모델이 적절한 음향 톤을 잡도록 유도합니다.
* **32~33행 (`## Sample Context:`)**: **[발화 직전 맥락]** 직전까지 기립 박수가 터져 나왔고, 이제 가격 발표를 위해 극적으로 잠시 뜸을 들이는 순간임을 설명합니다.
* **35~43행 (`## Transcript:`)**: **[대본 및 감정 지문]**
  * `[반갑고 신나는 목소리로]`, `[놀라움을 담아 빠르게]`, `[비밀을 말하듯 살짝 뜸을 들이다가]` 등 대괄호 안의 한국어 지문을 통해 성우처럼 생동감 넘치는 억양과 호흡, 속도 변화를 음성에 직접 불어넣습니다.

---

### 47행 ~ 60행: 음성 생성 상세 설정 (`GenerateContentConfig`)

```python
47:     generate_content_config = types.GenerateContentConfig(
48:         temperature=1,
49:         response_modalities=[
50:             "audio",
51:         ],
52:         speech_config=types.SpeechConfig(
53:             voice_config=types.VoiceConfig(
54:                 prebuilt_voice_config=types.PrebuiltVoiceConfig(
55:                     voice_name="Kore"
56:                 )
57:             )
58:         ),
59:     )
```

* **47~48행**: `temperature=1`을 설정하여 음성의 감정 표현과 억양의 다채로움을 풍부하게 만듭니다.
* **49~51행 (`response_modalities=["audio"]`)**: 모델에게 텍스트가 아닌 **"오디오(음성 바이너리)"**를 결과물 모달리티로 출력하도록 지시합니다.
* **52~58행 (`speech_config`)**:
  * 구글 Gemini TTS의 사전 빌드된 고품질 보이스인 **`Kore`**를 화자로 지정합니다.

---

### 61행 ~ 78행: 스트리밍 수신 및 PCM 오디오 청크 누적

```python
61:     audio_chunks = []
62:     mime_type = "audio/L16;rate=24000"
63: 
64:     print("음성 생성 중...")
65:     for chunk in client.models.generate_content_stream(
66:         model=model,
67:         contents=contents,
68:         config=generate_content_config,
69:     ):
70:         if chunk.parts is None:
71:             continue
72:         if chunk.parts[0].inline_data and chunk.parts[0].inline_data.data:
73:             inline_data = chunk.parts[0].inline_data
74:             mime_type = inline_data.mime_type
75:             audio_chunks.append(inline_data.data)
76:         elif chunk.text:
77:             print(chunk.text, end="")
```

* **61행 (`audio_chunks = []`)**: **[스트리밍 최적화 핵심]** 모델이 스트리밍으로 전달하는 오디오 조각들을 모아둘 빈 리스트를 생성합니다.
* **62행 (`mime_type`)**: 모델이 반환하는 오디오 포맷의 기본값(`audio/L16;rate=24000` = 16비트 리니어 PCM, 24,000Hz 샘플레이트)을 선언합니다.
* **65~69행 (`generate_content_stream`)**: 모델의 출력을 스트리밍 방식으로 실시간 수신하는 제너레이터 루프입니다.
* **70~71행**: 전달된 청크에 내용(`parts`)이 없는 경우 안전하게 스킵합니다.
* **72~75행**:
  * 스트리밍 조각에 바이너리 오디오 데이터(`inline_data.data`)가 포함되어 있으면, 이를 즉시 개별 파일로 저장하지 않고 **`audio_chunks` 리스트에 차곡차곡 누적(`append`)**합니다. (이전 수십 개의 쪼개진 파일이 생성되던 문제를 방지)
  * 응답 헤더에 담긴 최신 `mime_type`을 갱신합니다.
* **76~77행**: 혹시 모델이 텍스트 로그를 출력하는 경우 실시간으로 터미널에 출력합니다.

---

### 79행 ~ 85행: 버퍼 결합 및 단일 WAV 파일 저장

```python
79:     if audio_chunks:
80:         full_audio_pcm = b"".join(audio_chunks)
81:         wav_data = convert_to_wav(full_audio_pcm, mime_type)
82:         output_filename = "gemini_4_announcement.wav"
83:         save_binary_file(output_filename, wav_data)
84:         print(f"\n성공적으로 파일이 생성되었습니다: {output_filename}")
```

* **79행**: 수신된 오디오 청크가 1개 이상 존재하는지 확인합니다.
* **80행 (`b"".join(audio_chunks)`)**: 쪼개져서 전송된 수십 개의 순수 PCM 바이너리 조각들을 하나로 매끄럽게 이어 붙입니다.
* **81행 (`convert_to_wav`)**: 순수 PCM 데이터는 헤더가 없으면 일반 미디어 플레이어에서 재생할 수 없으므로, 표준 44바이트 RIFF WAV 헤더를 생성하여 부착합니다.
* **82~84행**: 최종 결합된 음원을 `gemini_4_announcement.wav` 파일로 저장하고 완료 메시지를 출력합니다.

---

### 86행 ~ 125행: 표준 WAV 헤더 조립 함수 (`convert_to_wav`)

```python
86: def convert_to_wav(audio_data: bytes, mime_type: str) -> bytes:
...
96:     parameters = parse_audio_mime_type(mime_type)
97:     bits_per_sample = parameters["bits_per_sample"]
98:     sample_rate = parameters["rate"]
99:     num_channels = 1
100:     data_size = len(audio_data)
101:     bytes_per_sample = bits_per_sample // 8
102:     block_align = num_channels * bytes_per_sample
103:     byte_rate = sample_rate * block_align
104:     chunk_size = 36 + data_size
...
108:     header = struct.pack(
109:         "<4sI4s4sIHHIIHH4sI",
110:         b"RIFF",          # ChunkID
111:         chunk_size,       # ChunkSize (전체 파일 크기 - 8)
112:         b"WAVE",          # Format
113:         b"fmt ",          # Subchunk1ID
114:         16,               # Subchunk1Size (PCM은 항상 16)
115:         1,                # AudioFormat (PCM 형식 코드 = 1)
116:         num_channels,     # 채널 수 (모노 = 1)
117:         sample_rate,      # 샘플링 레이트 (24000Hz)
118:         byte_rate,        # 초당 바이트 수 (SampleRate * BlockAlign)
119:         block_align,      # 1개 샘플 블록 크기 (Channels * BytesPerSample)
120:         bits_per_sample,  # 비트 깊이 (16비트)
121:         b"data",          # Subchunk2ID
122:         data_size         # 순수 오디오 데이터 크기
123:     )
124:     return header + audio_data
```

* **96~104행**: MIME 타입으로부터 오디오 스펙(16비트, 24kHz, 모노 채널, 총 데이터 바이트 수)을 계산합니다.
* **108~123행 (`struct.pack`)**: 
  * 포맷 스트링 `"<4sI4s4sIHHIIHH4sI"`: 리틀 엔디안(`<`) 방식으로 문자열(`4s`), 4바이트 정수(`I`), 2바이트 정수(`H`)를 정확한 바이트 오프셋으로 직렬화합니다.
  * Windows, Mac, 스마트폰 등 전 세계 모든 OS의 오디오 엔진이 즉시 인식할 수 있는 정통 RIFF WAV 컨테이너 헤더를 완성합니다.
* **124행**: 완성된 44바이트 헤더와 실제 오디오 바이트(`audio_data`)를 합쳐 최종 WAV 바이트를 반환합니다.

---

### 126행 ~ 159행: MIME 문자열 파싱 함수 (`parse_audio_mime_type`)

```python
126: def parse_audio_mime_type(mime_type: str) -> dict[str, int | None]:
...
138:     bits_per_sample = 16
139:     rate = 24000
140: 
141:     parts = mime_type.split(";")
142:     for param in parts:
143:         param = param.strip()
144:         if param.lower().startswith("rate="):
...
152:         elif param.startswith("audio/L"):
...
158:     return {"bits_per_sample": bits_per_sample, "rate": rate}
```

* **126~158행**: 모델이 응답 헤더로 전달한 문자열(`"audio/L16;rate=24000"`)을 `;` 단위로 쪼개어:
  * `rate=24000`에서 샘플레이트 정수 `24000` 추출
  * `audio/L16`에서 비트 수 정수 `16` 추출
  * 파싱에 실패하더라도 기본값(16비트, 24kHz)으로 안전하게 방어 처리합니다.

---

### 161행 ~ 163행: 실행 진입점

```python
161: if __name__ == "__main__":
162:     generate()
```

* **161~162행**: 파이썬 인터프리터에서 이 스크립트가 직접 실행되었을 때 `generate()` 함수를 호출하여 전체 TTS 음성 생성을 시작합니다.

---

## 🚀 실행 방법

```bash
# 1. API 키 설정 (최초 1회)
export GEMINI_API_KEY="본인의_API_키"

# 2. 스크립트 실행
python3 gemini_31_tts.py
```
실행 완료 시 현재 폴더에 **`gemini_4_announcement.wav`** 파일이 생성됩니다.
