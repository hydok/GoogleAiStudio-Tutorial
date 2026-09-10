import os
# pyrefly: ignore [missing-import]
from google import genai
# pyrefly: ignore [missing-import]
from google.genai import types


def get_mime_type(file_path: str) -> str:
    """오디오 파일 확장자에 맞는 MIME 타입을 반환합니다."""
    ext = os.path.splitext(file_path)[1].lower()
    mime_map = {
        ".m4a": "audio/mp4",
        ".mp3": "audio/mp3",
        ".wav": "audio/wav",
        ".aac": "audio/aac",
        ".ogg": "audio/ogg",
        ".flac": "audio/flac",
        ".webm": "audio/webm",
    }
    return mime_map.get(ext, "audio/mp4")


def transcribe_youtube_audio(
    audio_path: str,
    api_key: str | None = None,
    language_hint: str = "한국어",
) -> str:
    """다운로드된 오디오 파일을 Gemini 모델로 전달하여 전문 전사 및 요약을 생성합니다."""
    key = api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise ValueError(
            "GEMINI_API_KEY가 설정되어 있지 않습니다. API 키를 입력하거나 환경변수를 설정해 주세요."
        )

    client = genai.Client(api_key=key)
    file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
    mime_type = get_mime_type(audio_path)

    system_instruction = f"""
    당신은 세계 최고 수준의 오디오 전사 및 전문 요약 AI 어시스턴트입니다.
    제공된 오디오를 꼼꼼하게 청취하고, 주로 {language_hint}로 작성해 주세요.

    반드시 아래의 3가지 마크다운 섹션 형식으로 출력해야 합니다:

    # 🎬 영상 트랜스크립트 & 분석 리포트

    ## 💡 1. 핵심 3줄 요약
    - (영상의 가장 중요한 핵심 포인트 1)
    - (핵심 포인트 2)
    - (핵심 포인트 3)

    ### 🔑 주요 핵심 키워드
    - 키워드1, 키워드2, 키워드3, 키워드4, 키워드5

    ---

    ## ⏱️ 2. 주요 구간별 타임스탬프 요약
    - **[00:00]** 구간 주요 내용 요약
    - **[01:30]** 구간 주요 내용 요약
    (영상의 흐름에 따라 4~8개 내외의 주요 구간 타임스탬프 작성)

    ---

    ## 📝 3. 전체 발화 전문 (Full Transcript)
    (오디오 속 발화자의 모든 대화를 한 글자도 빠짐없이 명확한 문단으로 전사)
    """

    user_prompt = "위 오디오의 내용을 청취하고 지침에 따라 3줄 요약, 타임스탬프, 그리고 전체 발화 전문을 작성해 주세요."

    if file_size_mb < 20.0:
        with open(audio_path, "rb") as f:
            audio_bytes = f.read()

        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_bytes(data=audio_bytes, mime_type=mime_type),
                    types.Part.from_text(text=user_prompt),
                ],
            )
        ]
    else:
        print(f"대용량 오디오({file_size_mb:.1f} MB) 감지: 구글 Files API로 업로드 중...")
        uploaded_file = client.files.upload(file=audio_path)
        contents = [
            uploaded_file,
            user_prompt,
        ]

    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.2,
    )

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=contents,
        config=config,
    )

    return response.text
