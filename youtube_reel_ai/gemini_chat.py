import os
from typing import Any, Dict, List, Optional
# pyrefly: ignore [missing-import]
from google import genai
# pyrefly: ignore [missing-import]
from google.genai import types


def generate_reel_chat_response(
    video_info: Dict[str, Any],
    user_message: str,
    chat_history: Optional[List[Dict[str, str]]] = None,
    api_key: Optional[str] = None,
) -> str:
    """현재 보고 있는 유튜브 영상 정보를 바탕으로 Gemini 모델을 통해 지능적이고 따뜻한 대화 답변을 생성합니다."""
    key = api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise ValueError(
            "GEMINI_API_KEY가 설정되어 있지 않습니다. 웹 UI에서 API 키를 입력하거나 서버 환경변수에 등록해 주세요."
        )

    client = genai.Client(api_key=key)

    title = video_info.get("title", "")
    uploader = video_info.get("uploader", "")
    duration_str = video_info.get("duration_str", "")
    description = video_info.get("description", "")
    category = video_info.get("category", "JOURNAL")

    system_instruction = f"""
    당신은 고급 비디오 저널 플랫폼 'hydok VIDEO JOURNAL'의 영상 전문 AI 어시스턴트 'HYDOK AI'입니다.
    사용자는 현재 아래의 유튜브 영상을 감상하면서 당신과 대화하고 있습니다.

    [현재 감상 중인 영상 정보]
    - 제목: {title}
    - 채널/제작자: {uploader}
    - 카테고리: {category}
    - 재생 시간: {duration_str}
    - 영상 설명 및 자막/배경 컨텍스트:
    \"\"\"{description[:2000]}\"\"\"

    [답변 지침]
    1. 사용자의 질문에 정중하고, 따뜻하며, 문화적/인문학적 깊이가 느껴지는 어조(해요체)로 답변하세요.
    2. '3줄 요약', '인터뷰 부분', '용어 설명' 등의 질문에는 가독성 좋은 불릿 포인트와 명확한 문단 구분을 사용하세요.
    4. 영상 설명에 직접 언급되지 않은 디테일이라도, 영상의 주제와 한국 문화/역사/상식에 부합하는 신뢰할 수 있고 유익한 정보를 풍성하게 보충해 주세요.
    5. **비슷한 영상이나 관련 영상 추천 시**:
       - 현재 감상 중인 영상의 분위기나 주제와 잘 어울리는 고품질 추천 영상 2~3편을 엄선해 주세요.
       - 각 추천 항목마다 [영상 제목], [채널명], [선정 이유]를 정갈하게 설명하세요.
       - 각 추천 항목 끝에 사용자가 클릭하여 실제 유튜브 직통 주소를 복사할 수 있도록 반드시 아래 마크다운 링크 문법을 지켜 작성하세요:
         * 문법: `[링크복사](영상제목 채널명)`
         * 예시: `[링크복사](손흥민 LAFC 데뷔전 쿠팡플레이 스포츠)`
         * 주의: 괄호 안에 URL 대신 반드시 찾고자 하는 '영상 제목과 채널명'을 넣어주세요. 일반 텍스트로만 '링크복사'를 적지 마세요.
    6. 답변은 정갈한 마크다운 문법으로 작성하세요.
    """

    # 대화 기록 및 컨텐츠 구성
    contents: List[types.Content] = []

    if chat_history:
        for chat in chat_history[-6:]:  # 최근 6턴 대화 반영
            role = "user" if chat.get("role") == "user" else "model"
            text = chat.get("text", "")
            if text:
                contents.append(
                    types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=text)],
                    )
                )

    # 현재 유저 질문 추가
    contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_message)],
        )
    )

    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.7,
        max_output_tokens=8192,
    )

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=contents,
        config=config,
    )

    return response.text or ""


def generate_ai_timestamps(
    video_info: Dict[str, Any],
    api_key: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Gemini 3.6 Flash를 이용해 영상의 메타데이터와 설명을 분석하여 핵심 타임스탬프 리스트를 생성합니다."""
    key = api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        return []

    client = genai.Client(api_key=key)

    title = video_info.get("title", "")
    duration_sec = video_info.get("duration", 600) or 600
    description = video_info.get("description", "")[:2000]

    prompt = f"""
    당신은 영상 콘텐츠 분석 및 챕터 큐레이터입니다.
    아래 유튜브 영상의 제목과 설명, 총 재생시간({duration_sec}초)을 분석하여,
    영상의 핵심 흐름을 알 수 있는 4~7개의 구간별 타임스탬프(챕터)를 생성해 주세요.

    [영상 정보]
    - 제목: {title}
    - 총 재생 시간(초): {duration_sec}초
    - 영상 설명:
    {description}

    [출력 규칙]
    반드시 유효한 JSON 배열(Array) 형식만 출력하세요.
    각 원소는 다음 키를 포함해야 합니다:
    - "seconds": 해당 구간 시작 초 (정수, 0 이상 {duration_sec} 이하)
    - "time_str": "MM:SS" 형식의 시간 문자열 (예: "00:00", "02:15")
    - "title": 해당 구간의 핵심 주제 또는 소제목 (간결하고 매력적인 한국어, 15자 내외)
    """

    try:
        import json
        response = client.models.generate_content(
            model="gemini-3.7-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.3,
            ),
        )
        text = response.text.strip()
        data = json.loads(text)
        if isinstance(data, list):
            return data
    except Exception as e:
        print(f"AI 타임스탬프 생성 실패: {e}")
    return []

