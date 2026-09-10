import re
from typing import Any, Dict, List, Optional


def extract_video_id(url: str) -> Optional[str]:
    """다양한 형식의 유튜브 URL에서 11자리 video_id를 추출합니다."""
    if not url:
        return None
    
    # 1. 일반적인 11자리 ID 직접 입력 대응
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", url.strip()):
        return url.strip()

    patterns = [
        r"(?:v=|\/v\/|youtu\.be\/|\/embed\/|\/shorts\/|\/live\/)([A-Za-z0-9_-]{11})",
        r"[?&]v=([A-Za-z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def format_count(count: Optional[int]) -> str:
    """조회수/구독자 수를 한국식 포맷(만, 천)으로 변환합니다."""
    if not count:
        return "0"
    if count >= 100_000_000:
        return f"{count / 100_000_000:.1f}억"
    if count >= 10_000:
        return f"{count / 10_000:.1f}만"
    if count >= 1_000:
        return f"{count / 1_000:.1f}천"
    return str(count)


def parse_timestamps(info: Dict[str, Any]) -> List[Dict[str, Any]]:
    """유튜브 챕터(chapters) 또는 영상 설명란에서 타임스탬프 리스트를 추출합니다."""
    timestamps = []

    # 1. yt-dlp 챕터 정보 확인
    chapters = info.get("chapters")
    if chapters and isinstance(chapters, list):
        for ch in chapters:
            start_sec = int(ch.get("start_time", 0))
            title = (ch.get("title") or "").strip()
            if title:
                m, s = divmod(start_sec, 60)
                h, m = divmod(m, 60)
                time_str = f"{h:02d}:{m:02d}:{s:02d}" if h > 0 else f"{m:02d}:{s:02d}"
                timestamps.append({
                    "seconds": start_sec,
                    "time_str": time_str,
                    "title": title,
                })
        if timestamps:
            return timestamps

    # 2. 설명란(description)에서 00:00 패턴 정규식 파싱
    desc = info.get("description", "")
    if desc:
        pattern = re.compile(r'(?:(?:(\d{1,2}):)?(\d{1,2}):(\d{2}))\s*[-–—:]?\s*([^\n\r]+)')
        for line in desc.splitlines():
            match = pattern.search(line)
            if match:
                h = int(match.group(1)) if match.group(1) else 0
                m = int(match.group(2))
                s = int(match.group(3))
                total_sec = h * 3600 + m * 60 + s
                title = match.group(4).strip()
                title = re.sub(r'^[|\-•\s]+', '', title).strip()
                if title:
                    time_str = f"{h:02d}:{m:02d}:{s:02d}" if h > 0 else f"{m:02d}:{s:02d}"
                    timestamps.append({
                        "seconds": total_sec,
                        "time_str": time_str,
                        "title": title,
                    })

    return timestamps


def get_video_details(url_or_id: str) -> Dict[str, Any]:
    """유튜브 영상의 풍부한 메타데이터를 추출합니다."""
    try:
        import yt_dlp
    except ImportError:
        raise ImportError("yt-dlp 모듈이 필요합니다. 'pip install yt-dlp'를 실행해 주세요.")

    import urllib.parse

    video_id = extract_video_id(url_or_id)
    if video_id:
        target_url = f"https://www.youtube.com/watch?v={video_id}"
    else:
        # 검색 쿼리(search_query) URL이거나 텍스트 검색어인 경우
        parsed = urllib.parse.urlparse(url_or_id)
        qs = urllib.parse.parse_qs(parsed.query)
        if "search_query" in qs and qs["search_query"]:
            target_url = f"ytsearch1:{qs['search_query'][0]}"
        elif url_or_id.startswith("http://") or url_or_id.startswith("https://"):
            target_url = url_or_id
        else:
            target_url = f"ytsearch1:{url_or_id.strip()}"

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": False,
        "skip_download": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(target_url, download=False)
        if not info:
            raise ValueError("영상 정보를 불러올 수 없습니다.")

        # ytsearch 결과인 경우 첫 번째 실제 영상 추출
        if "entries" in info:
            entries = [e for e in (info.get("entries") or []) if e]
            if not entries:
                raise ValueError("검색어와 일치하는 실제 유튜브 영상을 찾을 수 없습니다.")
            info = entries[0]

        vid = info.get("id") or video_id or "default"
        duration_sec = info.get("duration", 0)
        minutes, seconds = divmod(duration_sec, 60)
        duration_str = f"{minutes:02d}:{seconds:02d}"

        view_count = info.get("view_count", 0)
        like_count = info.get("like_count", 0)
        subscriber_count = info.get("channel_follower_count")

        # 업로드 날짜 포맷팅 (YYYYMMDD -> YYYY년 M월 D일)
        upload_date_raw = info.get("upload_date", "")
        formatted_date = ""
        if len(upload_date_raw) == 8:
            y, m, d = upload_date_raw[:4], int(upload_date_raw[4:6]), int(upload_date_raw[6:8])
            formatted_date = f"{y}년 {m}월 {d}일"
        else:
            formatted_date = "최근 게시됨"

        # 채널 아바타 첫 글자
        uploader = info.get("uploader") or "영상 제작자"
        avatar_letter = uploader[0] if uploader else "R"

        timestamps = parse_timestamps(info)

        return {
            "id": vid,
            "title": info.get("title", "제목 없음"),
            "uploader": uploader,
            "avatar_letter": avatar_letter,
            "channel_url": info.get("channel_url", ""),
            "subscribers_str": f"구독자 {format_count(subscriber_count)}" if subscriber_count else "구독자 정보 없음",
            "thumbnail": info.get("thumbnail") or f"https://img.youtube.com/vi/{vid}/maxresdefault.jpg",
            "duration": duration_sec,
            "duration_str": duration_str,
            "duration_min_str": f"{max(1, round(duration_sec / 60))}분",
            "view_count_str": f"조회수 {format_count(view_count)}회",
            "like_count_str": format_count(like_count),
            "upload_date_str": formatted_date,
            "description": (info.get("description") or "영상 설명이 없습니다.").strip(),
            "category": info.get("categories", ["ESSAY"])[0] if info.get("categories") else "ESSAY",
            "webpage_url": info.get("webpage_url") or f"https://www.youtube.com/watch?v={vid}",
            "timestamps": timestamps,
        }

