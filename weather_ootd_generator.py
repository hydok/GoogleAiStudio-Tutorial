import os
import sys
from google import genai
from google.genai import types

#dev
def adjust_to_aspect_ratio_3_5(image_bytes: bytes) -> bytes:
    """이미지 데이터를 가로:세로 = 3:5 비율로 정밀하게 맞춰 반환합니다."""
    try:
        import io
        from PIL import Image

        img = Image.open(io.BytesIO(image_bytes))
        w, h = img.size

        # 목표 비율: 가로 3 : 세로 5 (h / w = 5 / 3)
        target_h = int(w * 5 / 3)
        if target_h <= h:
            # 높이가 더 길면 위아래 중앙 크롭
            top = (h - target_h) // 2
            img_cropped = img.crop((0, top, w, top + target_h))
        else:
            # 너비가 더 넓으면 좌우 중앙 크롭
            target_w = int(h * 3 / 5)
            left = (w - target_w) // 2
            img_cropped = img.crop((left, 0, left + target_w, h))

        buf = io.BytesIO()
        img_cropped.save(buf, format="JPEG", quality=95)
        return buf.getvalue()
    except Exception:
        # Pillow 미설치 또는 예외 시 원본 반환
        return image_bytes


def generate_weather_fashion(weather_description: str):
    """Gemini 3.1 Flash Image로 날씨 맞춤 3D 클레이 아트토이 3:5 비율 패션 이미지를 생성합니다."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[오류] GEMINI_API_KEY 환경변수가 설정되어 있지 않습니다.")
        print("터미널에서 'export GEMINI_API_KEY=\"your_api_key\"'를 먼저 실행해 주세요.")
        return

    client = genai.Client(api_key=api_key)

    print(f"🌦️  입력된 날씨: {weather_description}")
    print("1단계: Gemini 3.6 Flash가 날씨에 어울리는 3D 아트토이 캐릭터 착장을 기획 중 (비율 3:5)...")

    # 1단계: 날씨에 어울리는 착장 및 3D 클레이 피규어 영문 이미지 프롬프트 기획
    planning_prompt = f"""
    당신은 세계적인 아트토이/피규어 디자이너이자 3D 캐릭터 아티스트입니다.
    오늘의 날씨는 다음과 같습니다: "{weather_description}"

    이 날씨에 가장 잘 어울리는 트렌디하고 감각적인 패션 코디를 기획하고, 
    '3D 클레이 아트토이 피규어(Pop Mart 블라인드 박스 토이 스타일)' 느낌으로 옷을 입고 있는 캐릭터 이미지를 생성할 수 있도록 영문 프롬프트를 작성해 주세요.

    [프롬프트 필수 포함 요건 (첨부 스타일 및 3:5 비율 엄격 준수)]:
    - 화풍/스타일 (핵심): Cute stylized 3D clay figurine, Pop Mart blind box art toy aesthetic, minimalist cartoon 3D character design, smooth matte clay texture, chunky sculpted solid hair locks with soft highlights
    - 캐릭터 및 이목구비: Simple minimalist cute facial features, clean stylized dark eyes, tiny button nose, gentle subtle smile, porcelain-smooth skin tone
    - 의상 디테일: 날씨에 어울리는 트렌디한 캐주얼 스트릿웨어(후디, 집업 자켓, 아우터 등)의 지퍼와 포켓이 조각된 클레이 형태, 감각적인 뉴트럴 어스 톤(beige, khaki, camel, warm ochre, muted brown, charcoal)
    - 배경 및 조명: Clean solid minimalist warm-beige/neutral studio background, soft diffuse studio lighting, subtle ambient occlusion, Blender 3D claymation finish, Octane render quality
    - 구도 및 종횡비 (매우 중요): Aspect ratio 3:5, 3:5 vertical aspect ratio composition, portrait orientation, centered fashion lookbook shot framed perfectly in 3:5 format

    오직 이미지 생성 모델에 입력할 영문 프롬프트 1문단만 출력하세요. 부가 설명이나 따옴표는 제외하세요.
    """

    plan_response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=planning_prompt,
    )
    image_prompt = plan_response.text.strip()

    print("\n🎨 [기획된 이미지 생성 프롬프트]:")
    print(image_prompt)
    print("\n2단계: gemini-3.1-flash-image 모델로 이미지 생성 중...")

    # 2단계: 이미지 생성
    output_image = "weather_fashion_lookbook.jpg"
    saved = False

    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-image",
            contents=image_prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
            ),
        )

        if response.candidates:
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.data:
                    final_image_data = adjust_to_aspect_ratio_3_5(part.inline_data.data)
                    with open(output_image, "wb") as f:
                        f.write(final_image_data)
                    print(f"✨ 3:5 비율 이미지 생성 완료: {output_image}")
                    saved = True
                    break

        if not saved:
            print("\n[알림] 이미지 생성 응답에 데이터가 없습니다.")
            if response.text:
                print(f"응답 내용: {response.text}")

    except Exception as e:
        print(f"\n[이미지 생성 중 오류 발생]: {e}")

if __name__ == "__main__":
    default_weather = "비가 조금 내리고 쌀쌀한 늦가을 날씨, 기온 11도, 살짝 부는 바람"
    weather_input = sys.argv[1] if len(sys.argv) > 1 else default_weather
    generate_weather_fashion(weather_input)
