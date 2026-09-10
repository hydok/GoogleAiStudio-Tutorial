import os
import sys
# pyrefly: ignore [missing-import]
from google import genai
# pyrefly: ignore [missing-import]
from google.genai import types


def generate():
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    # 전사할 오디오 파일 (기본값: gemini_4_announcement.wav)
    audio_file = sys.argv[1] if len(sys.argv) > 1 else "gemini_4_announcement.wav"

    with open(audio_file, "rb") as f:
        audio_bytes = f.read()

    model = "gemini-3.5-transcribe"
    contents = [
        types.Content(
            role="user",
            parts=[
                # 오디오 파일을 바이너리로 전달
                types.Part.from_bytes(
                    data=audio_bytes,
                    mime_type="audio/wav",
                ),
                types.Part.from_text(text=""),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        audio_transcription_config=types.AudioTranscriptionConfig(
            word_timestamp=True,
            diarization=True,
        ),
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if text := chunk.text:
            print(text, end="")


if __name__ == "__main__":
    generate()
