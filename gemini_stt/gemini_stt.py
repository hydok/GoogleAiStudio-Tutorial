import os
import sys
# pyrefly: ignore [missing-import]
from google import genai
# pyrefly: ignore [missing-import]
from google.genai import types


def get_tts_output_dir() -> str:
    """gemini_tts/outputs 폴더 경로를 자동으로 찾아 반환합니다."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        # gemini_stt 서브폴더 내부에서 실행 시
        os.path.abspath(os.path.join(current_dir, "..", "gemini_tts", "outputs")),
        # 프로젝트 루트에서 실행 시
        os.path.abspath(os.path.join(current_dir, "gemini_tts", "outputs")),
        # 현재 디렉토리 기준
        os.path.abspath("gemini_tts/outputs"),
    ]
    for path in candidates:
        if os.path.isdir(path):
            return path
    # 폴더가 없으면 기본 위치 생성 후 반환
    default_path = candidates[0]
    os.makedirs(default_path, exist_ok=True)
    return default_path


def select_audio_file() -> str | None:
    """gemini_tts/outputs 폴더를 조회하여 사용자가 STT할 오디오 파일을 선택하도록 합니다."""
    # 명령행 인자로 파일이 직접 전달된 경우 우선 사용
    if len(sys.argv) > 1:
        custom_path = sys.argv[1]
        if os.path.exists(custom_path):
            return custom_path
        print(f"[경고] 지정하신 파일을 찾을 수 없습니다: {custom_path}")

    tts_dir = get_tts_output_dir()
    supported_exts = (".wav", ".mp3", ".m4a", ".ogg", ".flac", ".aac")

    # 폴더 내 지원 오디오 파일 목록 탐색 (최신 생성순 정렬)
    audio_files = [
        f for f in os.listdir(tts_dir)
        if os.path.isfile(os.path.join(tts_dir, f)) and f.lower().endswith(supported_exts)
    ]
    audio_files.sort(
        key=lambda f: os.path.getmtime(os.path.join(tts_dir, f)),
        reverse=True
    )

    if not audio_files:
        print(f"\n[안내] '{tts_dir}' 폴더에 오디오 파일이 없습니다.")
        print("💡 먼저 gemini_tts/gemini_31_tts.py 를 실행하여 음성 파일을 생성해 주세요.\n")
        return None

    print("\n" + "=" * 65)
    print(f"📁 [gemini_tts/outputs] 폴더의 생성 오디오 파일 목록:")
    print("=" * 65)
    for idx, fname in enumerate(audio_files, 1):
        full_path = os.path.join(tts_dir, fname)
        size_kb = os.path.getsize(full_path) / 1024
        size_str = f"{size_kb / 1024:.1f} MB" if size_kb >= 1024 else f"{size_kb:.1f} KB"
        print(f" [{idx}] {fname:<30} ({size_str})")
    print("-" * 65)

    while True:
        try:
            choice = input(f"👉 전사(STT)를 진행할 파일 번호를 선택하세요 (기본값 1): ").strip()
            if not choice:
                selected_file = audio_files[0]
                break
            idx = int(choice)
            if 1 <= idx <= len(audio_files):
                selected_file = audio_files[idx - 1]
                break
            print(f"⚠️ 1부터 {len(audio_files)} 사이의 번호를 입력해 주세요.")
        except ValueError:
            print("⚠️ 숫자로 번호를 입력해 주세요.")
        except (KeyboardInterrupt, EOFError):
            print("\n작업을 취소했습니다.")
            return None

    chosen_path = os.path.join(tts_dir, selected_file)
    print(f"\n선택된 파일: {selected_file}")
    return chosen_path


def get_mime_type(file_path: str) -> str:
    """오디오 파일 확장자에 맞는 MIME 타입을 반환합니다."""
    ext = os.path.splitext(file_path)[1].lower()
    mime_map = {
        ".wav": "audio/wav",
        ".mp3": "audio/mp3",
        ".m4a": "audio/m4a",
        ".ogg": "audio/ogg",
        ".flac": "audio/flac",
        ".aac": "audio/aac",
    }
    return mime_map.get(ext, "audio/wav")


def generate():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[오류] GEMINI_API_KEY 환경변수가 설정되어 있지 않습니다.")
        print("터미널에서 'export GEMINI_API_KEY=\"your_api_key\"'를 먼저 실행해 주세요.")
        return

    # 1. 파일 선택
    audio_path = select_audio_file()
    if not audio_path:
        return

    # 2. 오디오 파일 바이너리 읽기
    with open(audio_path, "rb") as f:
        audio_bytes = f.read()

    mime_type = get_mime_type(audio_path)
    client = genai.Client(api_key=api_key)

    contents = [
        types.Content(
            role="user",
            parts=[
                # 선택한 오디오 파일을 바이너리로 전달
                types.Part.from_bytes(
                    data=audio_bytes,
                    mime_type=mime_type,
                ),
                types.Part.from_text(text="이 오디오의 내용을 한 글자도 빠짐없이 한국어로 정확하게 텍스트로 받아적어(전사) 주세요."),
            ],
        ),
    ]

    generate_content_config = types.GenerateContentConfig(
        audio_transcription_config=types.AudioTranscriptionConfig(
            word_timestamp=True,
            diarization=True,
        ),
    )

    models_to_try = ["gemini-3.5-transcribe", "gemini-3.6-flash"]

    for model_name in models_to_try:
        try:
            print(f"\n🚀 [{model_name}] 모델로 오디오 텍스트 변환(STT) 시작...\n")
            response_stream = client.models.generate_content_stream(
                model=model_name,
                contents=contents,
                config=generate_content_config,
            )

            has_output = False
            for chunk in response_stream:
                if text := chunk.text:
                    print(text, end="", flush=True)
                    has_output = True

            if has_output:
                print("\n\n" + "=" * 65)
                print("✅ 음성 전사(STT)가 성공적으로 완료되었습니다!")
                print("=" * 65 + "\n")
                return

        except Exception as e:
            if "404" in str(e) or "not found" in str(e).lower():
                continue
            print(f"\n[오류 발생]: {e}")
            return


if __name__ == "__main__":
    generate()
