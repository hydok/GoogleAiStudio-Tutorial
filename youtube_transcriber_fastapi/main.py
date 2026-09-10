import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from downloader import download_audio, get_video_info
from history_manager import (
    add_history_item,
    clear_all_history,
    delete_history_item,
    load_history,
)
from transcriber import transcribe_youtube_audio

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

app = FastAPI(title="YouTube Audio Transcriber API", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 다운로드된 오디오 정적 스트리밍 마운트
app.mount("/downloads", StaticFiles(directory=DOWNLOAD_DIR), name="downloads")

# Jinja2 템플릿 설정
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


class VideoInfoRequest(BaseModel):
    url: str


class TranscribeRequest(BaseModel):
    url: str
    api_key: str | None = None


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """메인 웹페이지 UI를 렌더링합니다."""
    has_env_key = bool(os.environ.get("GEMINI_API_KEY"))
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request, "has_env_key": has_env_key},
    )


@app.post("/api/info")
async def api_get_info(payload: VideoInfoRequest):
    """유튜브 URL로부터 영상 썸네일, 제목, 채널 등 정보를 추출합니다."""
    url = payload.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="유튜브 URL을 입력해 주세요.")
    try:
        info = get_video_info(url)
        return {"success": True, "data": info}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/transcribe")
async def api_transcribe(payload: TranscribeRequest):
    """오디오를 다운로드하고 Gemini 3.6 Flash 모델을 통해 STT 및 요약을 수행합니다."""
    url = payload.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="유튜브 URL을 입력해 주세요.")

    api_key = payload.api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=400,
            detail="Gemini API Key가 제공되지 않았습니다. API 키를 입력하거나 서버 환경변수에 설정해 주세요.",
        )

    try:
        # 1. 오디오 다운로드
        audio_path, video_info = download_audio(url, output_dir=DOWNLOAD_DIR)
        
        # 2. Gemini STT 전사 및 요약
        transcript_text = transcribe_youtube_audio(audio_path, api_key=api_key)

        # 3. 히스토리 자동 저장
        history_item = add_history_item(video_info, audio_path, transcript_text)

        return {
            "success": True,
            "data": {
                "video_info": video_info,
                "audio_url": history_item["audio_url"],
                "transcript": transcript_text,
                "history_id": history_item["id"],
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history")
async def api_get_history():
    """저장된 변환 히스토리 목록을 반환합니다."""
    history = load_history()
    return {"success": True, "data": history}


@app.delete("/api/history/{item_id}")
async def api_delete_history(item_id: str):
    """특정 히스토리 항목을 삭제합니다."""
    success = delete_history_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="해당 항목을 찾을 수 없습니다.")
    return {"success": True, "message": "삭제되었습니다."}


@app.delete("/api/history")
async def api_clear_history():
    """모든 히스토리 내역을 초기화합니다."""
    clear_all_history()
    return {"success": True, "message": "모든 히스토리가 초기화되었습니다."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
