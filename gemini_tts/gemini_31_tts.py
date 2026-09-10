# To run this code you need to install the following dependencies:
# pip install google-genai

import mimetypes
import os
import re
import struct
# pyrefly: ignore [missing-import]
from google import genai
# pyrefly: ignore [missing-import]
from google.genai import types


def save_binary_file(file_name, data):
    f = open(file_name, "wb")
    f.write(data)
    f.close()
    print(f"File saved to to: {file_name}")


def generate():
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"),)

    model = "gemini-3.1-flash-tts-preview"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""## Scene:
A large tech conference keynote hall with thousands of excited attendees, subtle room acoustics and echoing stage microphone ambiance.

## Sample Context:
The presenter just unveiled the benchmark results of Gemini 4.0 to huge applause, and now pauses dramatically to announce the pricing.

## Transcript:
[반갑고 신나는 목소리로]
여러분, 깜짝 놀랄 만한 소식이 있습니다! 
[놀라움을 담아 빠르게]
구글의 최신 모델 Gemini 4.0이 드디어 공개되었는데요, 놀라지 마세요! 
[비밀을 말하듯 살짝 뜸을 들이다가]
이 엄청난 모델을, 정말 말도 안 되는 획기적인 가격으로 사용할 수 있게 되었습니다! 
[기분 좋은 밝은 목소리로]
고성능 AI 개발 비용 때문에 고민 많으셨던 분들, 이제 걱정 끝입니다. 지금 바로 확인해 보세요!"""),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        response_modalities=[
            "audio",
        ],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name="Kore"
                )
            )
        ),
    )

    audio_chunks = []
    mime_type = "audio/L16;rate=24000"

    print("음성 생성 중...")
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if chunk.parts is None:
            continue
        if chunk.parts[0].inline_data and chunk.parts[0].inline_data.data:
            inline_data = chunk.parts[0].inline_data
            mime_type = inline_data.mime_type
            audio_chunks.append(inline_data.data)
        elif chunk.text:
            print(chunk.text, end="")

    if audio_chunks:
        full_audio_pcm = b"".join(audio_chunks)
        wav_data = convert_to_wav(full_audio_pcm, mime_type)
        
        # gemini_tts/outputs 폴더 자동 감지 및 생성
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if os.path.basename(current_dir) == "gemini_tts":
            output_dir = os.path.join(current_dir, "outputs")
        else:
            output_dir = os.path.join(current_dir, "gemini_tts", "outputs")
        os.makedirs(output_dir, exist_ok=True)

        output_filename = os.path.join(output_dir, "gemini_4_announcement.wav")
        save_binary_file(output_filename, wav_data)
        print(f"\n성공적으로 파일이 생성되었습니다: {output_filename}")

def convert_to_wav(audio_data: bytes, mime_type: str) -> bytes:
    """Generates a WAV file header for the given audio data and parameters.

    Args:
        audio_data: The raw audio data as a bytes object.
        mime_type: Mime type of the audio data.

    Returns:
        A bytes object representing the WAV file header.
    """
    parameters = parse_audio_mime_type(mime_type)
    bits_per_sample = parameters["bits_per_sample"]
    sample_rate = parameters["rate"]
    num_channels = 1
    data_size = len(audio_data)
    bytes_per_sample = bits_per_sample // 8
    block_align = num_channels * bytes_per_sample
    byte_rate = sample_rate * block_align
    chunk_size = 36 + data_size  # 36 bytes for header fields before data chunk size

    # http://soundfile.sapp.org/doc/WaveFormat/

    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",          # ChunkID
        chunk_size,       # ChunkSize (total file size - 8 bytes)
        b"WAVE",          # Format
        b"fmt ",          # Subchunk1ID
        16,               # Subchunk1Size (16 for PCM)
        1,                # AudioFormat (1 for PCM)
        num_channels,     # NumChannels
        sample_rate,      # SampleRate
        byte_rate,        # ByteRate
        block_align,      # BlockAlign
        bits_per_sample,  # BitsPerSample
        b"data",          # Subchunk2ID
        data_size         # Subchunk2Size (size of audio data)
    )
    return header + audio_data

def parse_audio_mime_type(mime_type: str) -> dict[str, int | None]:
    """Parses bits per sample and rate from an audio MIME type string.

    Assumes bits per sample is encoded like "L16" and rate as "rate=xxxxx".

    Args:
        mime_type: The audio MIME type string (e.g., "audio/L16;rate=24000").

    Returns:
        A dictionary with "bits_per_sample" and "rate" keys. Values will be
        integers if found, otherwise None.
    """
    bits_per_sample = 16
    rate = 24000

    # Extract rate from parameters
    parts = mime_type.split(";")
    for param in parts: # Skip the main type part
        param = param.strip()
        if param.lower().startswith("rate="):
            try:
                rate_str = param.split("=", 1)[1]
                rate = int(rate_str)
            except (ValueError, IndexError):
                # Handle cases like "rate=" with no value or non-integer value
                pass # Keep rate as default
        elif param.startswith("audio/L"):
            try:
                bits_per_sample = int(param.split("L", 1)[1])
            except (ValueError, IndexError):
                pass # Keep bits_per_sample as default if conversion fails

    return {"bits_per_sample": bits_per_sample, "rate": rate}


if __name__ == "__main__":
    generate()
