import json
import os
from datetime import datetime
from typing import Any, Dict, List

HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "history.json")


def load_history() -> List[Dict[str, Any]]:
    """저장된 변환 히스토리 목록을 최신순으로 불러옵니다."""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except Exception:
        return []


def save_history(history_list: List[Dict[str, Any]]) -> None:
    """히스토리 목록을 JSON 파일로 저장합니다."""
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history_list, f, ensure_ascii=False, indent=2)


def add_history_item(
    video_info: Dict[str, Any],
    audio_path: str,
    transcript: str,
) -> Dict[str, Any]:
    """새로운 변환 결과를 히스토리에 추가하고 저장합니다."""
    history = load_history()

    # 웹에서 접근 가능한 오디오 URL 경로 생성 (/downloads/파일명)
    audio_filename = os.path.basename(audio_path)
    audio_url = f"/downloads/{audio_filename}"

    item = {
        "id": f"{video_info.get('id', 'item')}_{int(datetime.now().timestamp())}",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "youtube_url": video_info.get("webpage_url", ""),
        "video_id": video_info.get("id", ""),
        "title": video_info.get("title", "제목 없음"),
        "uploader": video_info.get("uploader", "알 수 없음"),
        "thumbnail": video_info.get("thumbnail", ""),
        "duration_str": video_info.get("duration_str", "00:00"),
        "audio_path": audio_path,
        "audio_url": audio_url,
        "transcript": transcript,
    }

    history.insert(0, item)
    save_history(history)
    return item


def delete_history_item(item_id: str) -> bool:
    """특정 ID의 히스토리 항목을 삭제합니다."""
    history = load_history()
    new_history = [item for item in history if item.get("id") != item_id]
    if len(new_history) != len(history):
        save_history(new_history)
        return True
    return False


def clear_all_history() -> None:
    """모든 히스토리 내역을 초기화합니다."""
    save_history([])
