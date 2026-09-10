import os
import re
from typing import Any, Dict, Tuple


def sanitize_filename(name: str) -> str:
    """파일명으로 사용할 수 없는 특수문자를 제거합니다."""
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()


def get_video_info(url: str) -> Dict[str, Any]:
    """유튜브 URL로부터 영상 제목, 썸네일, 길이 등 메타데이터를 추출합니다."""
    try:
        import yt_dlp
    except ImportError:
        raise ImportError(
            "yt-dlp 모듈이 설치되어 있지 않습니다. 'pip install yt-dlp'를 실행해 주세요."
        )

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": False,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if not info:
            raise ValueError("영상 정보를 불러올 수 없습니다. 올바른 URL인지 확인해 주세요.")

        duration_sec = info.get("duration", 0)
        minutes, seconds = divmod(duration_sec, 60)
        duration_str = f"{minutes:02d}:{seconds:02d}"

        return {
            "id": info.get("id"),
            "title": info.get("title", "제목 없음"),
            "uploader": info.get("uploader", "알 수 없는 채널"),
            "thumbnail": info.get("thumbnail", ""),
            "duration": duration_sec,
            "duration_str": duration_str,
            "webpage_url": info.get("webpage_url", url),
        }


def download_audio(url: str, output_dir: str = "downloads") -> Tuple[str, Dict[str, Any]]:
    """유튜브 영상에서 최고 음질의 오디오 스트림을 다운로드합니다.
    
    Returns:
        (생성된 오디오 파일 경로, 영상 메타데이터 딕셔너리)
    """
    try:
        import yt_dlp
    except ImportError:
        raise ImportError(
            "yt-dlp 모듈이 설치되어 있지 않습니다. 'pip install yt-dlp'를 실행해 주세요."
        )

    os.makedirs(output_dir, exist_ok=True)

    # 1. 메타데이터 조회
    info = get_video_info(url)
    video_id = info["id"]
    safe_title = sanitize_filename(info["title"])[:50]
    out_template = os.path.join(output_dir, f"{safe_title}_{video_id}.%(ext)s")

    # 2. 다운로드 옵션 설정 (ffmpeg 없이도 안전한 m4a 직접 다운로드)
    ydl_opts = {
        "format": "bestaudio[ext=m4a]/bestaudio/best",
        "outtmpl": out_template,
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # 3. 다운로드된 파일 탐색
    for fname in os.listdir(output_dir):
        if video_id in fname:
            full_path = os.path.abspath(os.path.join(output_dir, fname))
            return full_path, info

    raise FileNotFoundError("오디오 다운로드에 실패했거나 파일을 찾을 수 없습니다.")
