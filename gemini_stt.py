import os
import sys
# pyrefly: ignore [missing-import]
from google import genai
# pyrefly: ignore [missing-import]
from google.genai import types


def transcribe_audio(audio_path: str):
    """지정된 오디오 파일을 Gemini 멀티모달 모델을 통해 텍스트로 변환합니다."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[오류] GEMINI_API_KEY 환경변수가 설정되어 있지 않습니다.")
        print("터미널에서 'export GEMINI_API_KEY=\"your_api_key\"'를 먼저 실행해 주세요.")
        return

    if not os.path.exists(audio_path):
        print(f"[오류] 오디오 파일 '{audio_path}'을(를) 찾을 수 없습니다.")
        print("먼저 gemini_31_tts.py를 실행하여 음성 파일을 생성하거나 올바른 파일 경로를 지정해 주세요.")
        return

    client = genai.Client(api_key=api_key)

    # 1. 오디오 파일 읽기
    with open(audio_path, "rb") as f:
        audio_bytes = f.read()

    print(f"[{audio_path}] 음성 분석 및 텍스트 변환(STT) 진행 중...")

    # 2. 멀티모달 모델 호출
    # 최신 멀티모달 모델인 gemini-3.6-flash를 사용합니다.
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=[
            types.Part.from_bytes(
                data=audio_bytes,
                mime_type="audio/wav",
            ),
            """
            이 오디오 파일을 주의 깊게 듣고 다음 항목을 정리해줘:

            1. [전사 (Transcript)]: 화자가 말한 모든 내용을 빠짐없이 정확하게 한국어로 받아써줘.
            2. [음성 톤 및 분위기]: 목소리의 억양, 감정(기쁨, 기대감, 차분함 등), 발화 속도 및 전달력에 대해 간단히 평가해줘.
            """,
        ],
    )

    print("\n" + "=" * 40)
    print("📝 음성 텍스트 변환 (STT) 결과")
    print("=" * 40)
    print(response.text)
    print("=" * 40)


if __name__ == "__main__":
    # 실행 시 파일명을 인자로 넘길 수도 있고, 기본값으로 gemini_4_announcement.wav를 사용합니다.
    target_file = sys.argv[1] if len(sys.argv) > 1 else "gemini_4_announcement.wav"
    transcribe_audio(target_file)
