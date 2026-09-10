import os
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from gemini_chat import generate_ai_timestamps, generate_reel_chat_response
from video_helper import extract_video_id, get_video_details

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(title="hydok VIDEO JOURNAL & AI Chat", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


class VideoRequest(BaseModel):
    url: str


class ChatRequest(BaseModel):
    video_info: Dict[str, Any]
    message: str
    chat_history: Optional[List[Dict[str, str]]] = None
    api_key: Optional[str] = None


@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    """hydok Video Journal 메인 페이지를 렌더링합니다."""
    has_env_key = bool(os.environ.get("GEMINI_API_KEY"))
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request, "has_env_key": has_env_key},
    )


class ResolveUrlRequest(BaseModel):
    query_or_url: str


@app.post("/api/resolve-video-url")
async def api_resolve_video_url(payload: ResolveUrlRequest):
    """검색어 또는 유튜브 검색 URL로부터 실제 영상의 직통 URL(https://www.youtube.com/watch?v=...)을 실시간 조회합니다."""
    query = payload.query_or_url.strip()
    if not query:
        raise HTTPException(status_code=400, detail="검색어 또는 URL을 입력해 주세요.")

    video_id = extract_video_id(query)
    if video_id:
        return {"success": True, "url": f"https://www.youtube.com/watch?v={video_id}", "id": video_id}

    try:
        details = get_video_details(query)
        real_id = details.get("id")
        if not real_id:
            raise ValueError("영상 ID를 찾지 못했습니다.")
        return {
            "success": True,
            "url": f"https://www.youtube.com/watch?v={real_id}",
            "id": real_id,
            "title": details.get("title", ""),
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"실제 유튜브 영상을 조회하지 못했습니다: {str(e)}")


@app.post("/api/video-info")
async def api_get_video_info(payload: VideoRequest):
    """유튜브 URL 또는 검색어로부터 video_id 및 상세 메타데이터를 추출합니다."""
    url = payload.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="유튜브 URL 또는 검색어를 입력해 주세요.")

    try:
        details = get_video_details(url)
        return {"success": True, "data": details}
    except Exception as e:
        video_id = extract_video_id(url)
        if video_id:
            return {
                "success": True,
                "data": {
                    "id": video_id,
                    "title": "재생 중인 유튜브 영상",
                    "uploader": "YouTube Creator",
                    "avatar_letter": "Y",
                    "subscribers_str": "구독자 정보",
                    "thumbnail": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
                    "duration_str": "재생 중",
                    "duration_min_str": "영상",
                    "view_count_str": "조회수 정보",
                    "like_count_str": "추천",
                    "upload_date_str": "게시됨",
                    "description": f"URL: {url}\n영상 정보를 재생 중입니다.",
                    "category": "VIDEO",
                    "webpage_url": f"https://www.youtube.com/watch?v={video_id}",
                },
            }
        raise HTTPException(status_code=400, detail=f"영상을 불러올 수 없습니다: {str(e)}")


@app.post("/api/chat")
async def api_chat(payload: ChatRequest):
    """영상 정보를 바탕으로 Gemini 모델과 대화합니다."""
    msg = payload.message.strip()
    if not msg:
        raise HTTPException(status_code=400, detail="메시지를 입력해 주세요.")

    api_key = payload.api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=400,
            detail="Gemini API Key가 필요합니다. 상단 ⚙️ 설정을 통해 입력하거나 서버 환경변수에 GEMINI_API_KEY를 등록해 주세요.",
        )

    try:
        reply = generate_reel_chat_response(
            video_info=payload.video_info,
            user_message=msg,
            chat_history=payload.chat_history,
            api_key=api_key,
        )
        return {"success": True, "reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class TimestampRequest(BaseModel):
    video_info: Dict[str, Any]
    api_key: Optional[str] = None


@app.post("/api/timestamps")
async def api_get_timestamps(payload: TimestampRequest):
    """영상의 타임스탬프 리스트를 조회하거나 Gemini로 자동 분석하여 반환합니다."""
    video_info = payload.video_info
    existing = video_info.get("timestamps")
    if existing and isinstance(existing, list) and len(existing) > 0:
        return {"success": True, "timestamps": existing, "source": "metadata"}

    # 메타데이터에 타임스탬프가 없으면 Gemini로 생성 시도
    api_key = payload.api_key or os.environ.get("GEMINI_API_KEY")
    if api_key:
        try:
            ai_ts = generate_ai_timestamps(video_info, api_key=api_key)
            if ai_ts:
                return {"success": True, "timestamps": ai_ts, "source": "gemini"}
        except Exception as e:
            print(f"Gemini 타임스탬프 생성 오류: {e}")

    # 둘 다 없으면 기본 구간 3개 제공 (00:00 오프닝, 중간, 마무리)
    duration_sec = video_info.get("duration", 600) or 600
    mid_sec = duration_sec // 2
    return {
        "success": True,
        "timestamps": [
            {"seconds": 0, "time_str": "00:00", "title": "도입부 및 하이라이트"},
            {"seconds": mid_sec, "time_str": f"{mid_sec//60:02d}:{mid_sec%60:02d}", "title": "핵심 주제 및 본문 이야기"},
            {"seconds": max(0, duration_sec - 30), "time_str": f"{(duration_sec-30)//60:02d}:{(duration_sec-30)%60:02d}", "title": "마무리 및 맺음말"},
        ],
        "source": "fallback",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
