# ai_analysis/utils.py
import requests
import json
import re
import httpx
import environ
from pathlib import Path
from openai import AsyncOpenAI
from django.conf import settings

# 환경 변수 로드
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env(DEBUG=(bool, False))
env_file = BASE_DIR / '.env'
if env_file.exists():
    environ.Env.read_env(env_file)

# GMS_KEY 통합 사용
GMS_KEY = env('GMS_KEY').strip()

def get_gpt_client():
    """GPT 계열 전용 OpenAI SDK 클라이언트 생성"""
    return AsyncOpenAI(
        api_key=GMS_KEY,
        base_url="https://gms.ssafy.io/gmsapi/api.openai.com/v1"
    )

async def call_gemini_native(model_name, system_prompt, user_prompt):
    """Gemini 계열 전용 직접 HTTP 호출 (URL 오염 완벽 차단)"""
    # URL을 한 줄로 정의하여 특수기호 삽입 방지
    url = f"https://gms.ssafy.io/gmsapi/generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GMS_KEY}"
    
    payload = {
        "contents": [{"parts": [{"text": f"{system_prompt}\n\n{user_prompt}"}]}]
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url.strip(), json=payload, timeout=30.0)
        response.raise_for_status()
        res_data = response.json()
        return res_data['candidates'][0]['content']['parts'][0]['text'].strip()

async def get_ai_response(model_name, system_prompt, user_prompt):
    """[통합 엔드포인트] 모든 AI 기능을 이 함수 하나로 처리"""
    try:
        if 'gpt' in model_name:
            client = get_gpt_client()
            response = await client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
            )
            return response.choices[0].message.content.strip()
        elif 'gemini' in model_name:
            return await call_gemini_native(model_name, system_prompt, user_prompt)
        raise ValueError(f"Unsupported model: {model_name}")
    except Exception as e:
        print(f"❌ [AI Error] {model_name}: {e}")
        return ""

def parse_ai_json(raw_content):
    """AI 응답 텍스트에서 JSON을 안전하게 추출"""
    if not raw_content: return None
    try:
        content = re.sub(r"```json|```", "", raw_content).strip()
        match = re.search(r"(\{.*\}|\[.*\])", content, re.DOTALL)
        if match: return json.loads(match.group())
        return json.loads(content)
    except: return None

# --- 3번 기능: 리뷰 수집 및 요약 관련 ---
def fetch_steam_reviews(appid):
    """스팀 API에서 한국어 리뷰 수집"""
    url = f"https://store.steampowered.com/appreviews/{appid}?json=1&language=korean&num_per_page=30&purchase_type=all"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return [r['review'] for r in response.json().get('reviews', []) if r.get('review')]
    except Exception as e:
        print(f"Review Fetch Error: {e}")
    return []

async def get_ai_review_summary(reviews):
    """리뷰 요약 실행 (통합 함수 사용)"""
    print(f"🔍 [DEBUG] 요약 시작 - 리뷰 개수: {len(reviews)}")
    if not reviews: 
        return "표시할 리뷰가 없습니다."
    
    combined_text = "\n".join(reviews[:25])
    system_prompt = (
        "너는 게임 전문 칼럼니스트야. 제공된 스팀 유저 리뷰들을 읽고, "
        "게임의 전반적인 특징, 장점, 단점을 모두 포함한 하나의 완성된 요약문을 작성해줘. "
        "항목을 나열하는 방식이 아니라, 문맥이 이어지는 자연스러운 문단 형태로 작성해야 해. "
        "반드시 한국어로 답변하고, 결과는 JSON 형식 {'summary': '내용'}으로 반환해."
    )
    user_prompt = f"다음은 유저들의 실제 리뷰 내용들이야:\n\n{combined_text}"
    
    # 모델은 상황에 맞게 변경 가능 (예: gpt-5-nano)
    raw_res = await get_ai_response("gpt-5-nano", system_prompt, user_prompt)
    result = parse_ai_json(raw_res)
    return result.get('summary', "요약을 생성할 수 없습니다.") if result else "분석 결과가 유효하지 않습니다."