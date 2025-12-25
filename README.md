# 🎮 Steam [Ecyce](https://youtu.be/0E15Mw7pjJw?si=-Npa8tIrM50pWLoc): AI 기반 개인화 게임 분석 & 커뮤니티 플랫폼

> **AI를 통해 더 나은 스팀 라이브러리 라이프사이클을 완성합니다.**<br>
> 본 프로젝트는 사용자의 플레이 경험을 분석하고, AI 기반의 스마트한 검색 및 리뷰 요약 기능을 제공하는 개인화 플랫폼입니다.

---

## 0. 팀 정보 (Team Information)
* **팀 번호**: 8팀
* **팀원**: 신원호(팀장), 문현아, 이강우

## 1. 프로젝트 개요 (Project Overview)

### 🚩 기획 배경 및 해결 목표
* **검색의 한계**: 기존 스팀의 엄격한 검색 시스템을 보완하여 유사어 및 맥락 검색이 가능하도록 개선합니다.
* **정보의 과잉**: 방대하게 쌓인 게임 리뷰를 AI가 구조화하여 핵심 정보만 빠르게 전달합니다.
* **개인화 부족**: 단순 필터링 추천을 넘어 유저의 실제 플레이 데이터를 기반으로 정교한 분석 리포트와 추천을 제공합니다.
* **컨텐츠 부재**: 단순한 리캡(Recap) 기능을 넘어 이상형 월드컵 등 즐길 거리를 제공하고 이를 커뮤니티와 연결합니다.

---

## 2. 서비스 핵심 기능 (Key Features)

### 🔍 스마트 검색 시스템 (Smart Search)
* **기본 검색**: 게임 타이틀 기반의 빠르고 정확한 검색을 지원합니다.
* **AI 보완 검색**: 오타나 유사어 검색 시 AI가 맥락을 파악하여 적절한 결과를 추천합니다.

> **![실행 화면 1](/Docs/Images/example1.gif) ![실행 화면 2](/Docs/Images/example2.png)**

### 📝 AI 리뷰 요약 및 구조화 (Review Summary)
* **AI 큐레이터**: 흩어져 있는 수많은 유저 리뷰를 분석하여 종합 요약문을 생성합니다.
* **데이터 최신화**: 잦은 API 호출을 방지하면서도 최신 리뷰가 반영된 요약 정보를 제공합니다.

> **![실행 화면 3](/Docs/Images/example3.webp) ![실행 화면 4](/Docs/Images/example4.png)**

### 📊 개인화 분석 리포트 & 추천 (Analysis & Recommendation)
* **게이머 분석**: 사용자의 실제 플레이 타임과 장르 선호도를 기반으로 분석 리포트를 제공합니다.
* **맞춤형 추천**: 분석된 결과를 바탕으로 유저의 취향에 딱 맞는 차기 게임을 추천합니다.

> **![실행 화면 5](/Docs/Images/example5.gif) ![실행 화면 6](/Docs/Images/example6.png) ![실행 화면 7](/Docs/Images/example7.png)**

### 🏆 게임 이상형 월드컵 & 커뮤니티 (Contents)
* **월드컵 컨텐츠**: 유저 라이브러리에 있는 게임들을 대상으로 월드컵을 진행합니다.
* **최애 게임 반영**: 우승한 게임은 '최애 게임'으로 선정되어 프로필에 반영됩니다.
* **커뮤니티 공유**: 월드컵 결과와 리뷰를 커뮤니티에 공유하여 다른 유저들과 소통합니다.

> **![실행 화면 8](/Docs/Images/example8.png) ![실행 화면 9](/Docs/Images/example9.png) ![실행 화면 10](/Docs/Images/example10.png)**

[실행 예시 영상](https://youtu.be/0v7zxwRBH50?si=cdGl9m12jSptUEUy)

---

## 3. 기술적 구현 및 설계 (Technical Architecture)

### 🛠 기술 스택 (Tech Stack)
#### **Frontend**
![Vue.js](https://img.shields.io/badge/Vue.js-4FC08D?style=for-the-badge&logo=vuedotjs&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![Pinia](https://img.shields.io/badge/Pinia-FFD700?style=for-the-badge&logo=pinia&logoColor=black)
![Axios](https://img.shields.io/badge/Axios-5A29E4?style=for-the-badge&logo=axios&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)

#### **Backend**
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![Django REST Framework](https://img.shields.io/badge/DRF-FF1709?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

#### **AI & API**
![OpenAI](https://img.shields.io/badge/GPT--4o--mini-412991?style=for-the-badge&logo=openai&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Gemini--1.5--Flash-4285F4?style=for-the-badge&logo=googlegemini&logoColor=white)
![Steam](https://img.shields.io/badge/Steam_Web_API-000000?style=for-the-badge&logo=steam&logoColor=white)

#### **Tools**
![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)
![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)
![Postman](https://img.shields.io/badge/Postman-FF6C37?style=for-the-badge&logo=postman&logoColor=white)

### 🤖 AI 구현 세부 사항
* **LLM 인터페이스 통합**: GPT와 Gemini의 서로 다른 호출 방식을 `get_ai_response` 함수로 단일화하여 유지보수성을 높였습니다.
* **핵심 로직**:
  * `get_ai_analysis`: 사용자 성향 기반 게임 분석 및 추천
  * `get_ai_review_summary`: 게임 리뷰 요약문 작성
  * `get_search_recommendation`: 문맥 기반 검색 보완

### 🏗 ERD 설계
* 프로젝트의 백엔드 구조는 `Accounts`, `Games`, `Community`, `AI Analysis`의 4가지 앱으로 설계되었습니다.

> ![ERD](/Docs/Images/ERD.png)

---

