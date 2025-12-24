import requests
import json
from .views import get_ai_client  # 기존 AI 설정 로드

def fetch_steam_reviews(appid):
    """
    스팀 API에서 해당 게임의 한국어 리뷰를 수집
    """
    # language=korean을 통해 한국어 리뷰 우선 수집
    url = f"https://store.steampowered.com/appreviews/{appid}?json=1&language=korean&num_per_page=30"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            # 리뷰 텍스트만 추출
            return [r['review'] for r in data.get('reviews', []) if r.get('review')]
    except Exception as e:
        print(f"Error fetching reviews: {e}")
    return []

async def get_ai_review_summary(reviews):
    """
    AI를 통해 리뷰 원본들을 하나의 완성된 요약문으로 변환
    """
    if not reviews:
        return "표시할 리뷰가 없습니다."
        
    client = get_ai_client()
    combined_text = "\n".join(reviews[:25]) # 분석 효율을 위해 25개 내외 사용

    # 리스트 형식이 아닌 자연스러운 문장으로 작성을 유도하는 프롬프트
    system_prompt = (
        "너는 게임 전문 칼럼니스트야. 제공된 스팀 유저 리뷰들을 읽고, "
        "게임의 전반적인 특징, 장점, 단점을 모두 포함한 하나의 완성된 요약문을 작성해줘. "
        "항목을 나열하는 방식이 아니라, 문맥이 이어지는 자연스러운 문단 형태로 작성해야 해. "
        "반드시 한국어로 답변하고, 결과는 JSON 형식 {'summary': '내용'}으로 반환해."
    )
    
    user_prompt = f"다음은 유저들의 실제 리뷰 내용들이야:\n\n{combined_text}"

    try:
        response = await client.chat.completions.create(
            model="gpt-5-nano",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={ "type": "json_object" }
        )
        
        result = json.loads(response.choices[0].message.content)
        # 모델의 summary_text 필드에 들어갈 텍스트 반환
        return result.get('summary', "요약을 생성할 수 없습니다.")
    except Exception as e:
        print(f"AI Analysis Error: {e}")
        return "리뷰 분석 중 오류가 발생했습니다."