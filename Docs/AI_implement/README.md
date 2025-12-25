ai 구현 내용
- LLM 클라이언트 호출 관련
  - GMS에서 제공하는 LLM 중 GPT와 Gemini를 후보로 선정
  - 두 모델의 호출, 응답 방식이 다르기 때문에, 반복 사용에 용이하도록 get_ai_response 함수로 통합
  ![LLM client](/Docs/AI_implement/images/ai1.png)

- AI 사용 기능 구현 관련
  - 사용자 경험을 바탕으로 성향을 분석하고 추천 게임을 선정하여 제공
  ![get_ai_analysis](/Docs/AI_implement/images/ai2.png)
  - 전달받은 게임 리뷰들을 바탕으로 그 게임의 정보를 담은 요약문을 작성
  ![get_ai_review_summary](/Docs/AI_implement/images/ai3.png)
  - 사용자 입력 검색어를 바탕으로 유사도 높은 검색 결과 제공
  ![get_search_recommendation](/Docs/AI_implement/images/ai4.png)
  
  