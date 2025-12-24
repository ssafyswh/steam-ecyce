<template>
  <div class="recommend-container">
    
    <!-- 분석 결과 화면 (데이터가 있을 때) -->
    <div v-if="result" class="result-box">
      
      <!-- 로딩 오버레이: 재분석 중일 때 화면을 덮음 -->
      <div v-if="isLoading" class="loading-overlay">
        <div class="spinner small"></div>
        <p>Friday가 새로운 분석을 진행 중입니다...</p>
      </div>

      <h1 class="page-title">🤖 AI 분석 결과 (Friday's Report)</h1>
      
      <div class="analysis-section">
        <h2>당신은 <span class="highlight">{{ result.gamer_type }}</span> 입니다!</h2>
        <p class="analysis-text">{{ result.analysis_text }}</p>
        <p class="date-info">최근 분석일: {{ formatDate(result.updated_at) }}</p>
      </div>

      <hr class="divider">

      <h3>✨ Friday's Pick: 추천 게임</h3>
      <div class="rec-grid">
        <div 
          v-for="(game, index) in result.recommendations" 
          :key="index" 
          class="rec-card"
          :class="{ 'ownded-card': game.is_owned }"
          @click="goToDetail(game.appid)"
        >
          <div class="card-header">
            <h4>{{ game.title }}</h4>
          </div>
          <div class="card-body">
            <p>{{ game.reason }}</p>
            <span v-if="game.is_owned" class="sleep-text">💤 라이브러리에서 잠자는 중</span>
          </div>
        </div>
      </div>
      
      <!-- 버튼들 -->
      <div class="action-buttons">
        <!-- 로딩 중이면 버튼 비활성화 & 텍스트 변경 -->
        <button 
          @click="analyzeGames(true)" 
          class="retry-btn" 
          :disabled="isLoading"
          :class="{ 'btn-loading': isLoading }"
        >
          <span v-if="isLoading">⏳ 분석 중...</span>
          <span v-else>🔄 다시 분석하기 (Update)</span>
        </button>

        <!-- 로딩 중 뒤로가기 막기 -->
        <button @click="goBack" class="back-btn" :disabled="isLoading">
          ⬅ 내 라이브러리
        </button>
      </div>
    </div>

    <!-- 초기 로딩 화면 (데이터가 아예 없을 때만) -->
    <div v-else-if="isLoading" class="loading-box">
      <div class="spinner"></div>
      <p class="loading-text">데이터를 불러오는 중입니다...</p>
      <p class="sub-text">AI(Friday)가 당신의 취향을 파악하고 있어요 🧠</p>
    </div>

    <!-- 초기 시작 화면 -->
    <div v-else class="start-box">
      <h1>🎮 AI 게임 취향 분석</h1>
      <p>당신의 스팀 라이브러리를 기반으로<br>나만의 게이머 성향을 분석하고 숨겨진 명작을 추천받으세요.</p>
      
      <div class="start-icon">🕵️‍♂️</div>
      
      <button @click="analyzeGames(false)" class="start-btn">분석 결과 보기</button>
      <button @click="goBack" class="back-btn-small">돌아가기</button>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';

const isLoading = ref(false);
const result = ref(null);
const authStore = useAuthStore();
const router = useRouter();

const formatDate = (dateString) => {
  if (!dateString) return '';
  return new Date(dateString).toLocaleString();
};

const goBack = () => {
  router.push('/profile');
};

const goToDetail = (appid) => {
  if (appid) {
    router.push(`/game/${appid}`);
  } else {
    alert("해당 게임의 상세 정보가 아직 DB에 등록되지 않았습니다.");
  }
};

const analyzeGames = async (forceUpdate = false) => {
  if (isLoading.value) return; // 중복 클릭 방지
  isLoading.value = true;
  
  try {
    const response = await axios.post('http://localhost:8000/ai/recommend/', 
      { force_update: forceUpdate }, 
      {
        headers: { Authorization: `Token ${authStore.token}` },
        withCredentials: true
      }
    );
    result.value = response.data;
  } catch (error) {
    console.error("분석 실패:", error);
    const errorMsg = error.response?.data?.error || "분석 정보를 가져오는데 실패했습니다.";
    alert(`[오류] ${errorMsg}`);
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  analyzeGames(false); 
});
</script>

<style scoped>
/* 1. 기본 컨테이너 & 레이아웃
--------------------------------------- */
.recommend-container {
  max-width: 900px;
  margin: 50px auto;
  padding: 40px;
  background-color: #1b2838;
  color: #c7d5e0;
  border-radius: 15px;
  box-shadow: 0 0 20px rgba(0,0,0,0.5);
  text-align: center;
  font-family: 'Motiva Sans', sans-serif;
  position: relative; 
  overflow: hidden;
}

h1, h2, h3, h4 { color: #ffffff; }
.page-title { margin-bottom: 30px; font-size: 2rem; }
.highlight { color: #66c0f4; font-weight: bold; }
.divider { border: 0; height: 1px; background: #2a475e; margin: 30px 0; }

/* 2. 로딩 및 오버레이 (중앙 정렬 핵심)
--------------------------------------- */
.loading-box, .loading-overlay {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.loading-box {
  padding: 100px 0; /* 초기 로딩 시 충분한 공간 확보 */
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(27, 40, 56, 0.85);
  z-index: 100;
  backdrop-filter: blur(3px);
}

.spinner {
  width: 60px;
  height: 60px;
  border: 6px solid #2a475e;
  border-top: 6px solid #66c0f4;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.spinner.small {
  width: 40px;
  height: 40px;
  border-width: 4px;
}

.loading-text { font-size: 1.3rem; margin-top: 20px; color: #fff; }
.sub-text { color: #66c0f4; margin-top: 10px; }

/* 3. AI 분석 결과 세션
--------------------------------------- */
.analysis-section {
  background: rgba(0, 0, 0, 0.2);
  padding: 25px;
  border-radius: 10px;
  margin-bottom: 30px;
  border: 1px solid #2a475e;
  text-align: left; /* 텍스트 가독성을 위해 좌측 정렬 */
}

.analysis-text {
  font-size: 1.1rem;
  line-height: 1.7;
  color: #e0e0e0;
  white-space: pre-wrap;
}

.date-info {
  margin-top: 15px;
  font-size: 0.8rem;
  color: #6a7782;
  text-align: right;
}

/* 4. 추천 게임 그리드 & 카드
--------------------------------------- */
.rec-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 25px;
  margin: 30px 0;
}

.rec-card {
  background: #233547;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.3);
  border: 1px solid #101822;
  transition: all 0.3s ease;
  overflow: hidden;
  position: relative;
}

.rec-card:hover {
  transform: translateY(-5px);
  border-color: #66c0f4;
  cursor: pointer;
}

.card-header {
  background: #171a21;
  padding: 15px;
  border-bottom: 1px solid #3d4c5d;
}

.card-header h4 { margin: 0; color: #66c0f4; }
.card-body { padding: 20px; color: #acb2b8; text-align: left; }

/* 보유 중인 게임 강조 */
.owned-card {
  border: 1px solid #66c0f4;
  background: rgba(102, 192, 244, 0.05);
}

.sleep-text {
  display: block;
  margin-top: 15px;
  font-size: 0.85rem;
  color: #66c0f4;
  text-align: right;
  font-weight: bold;
}

/* 5. 버튼 스타일
--------------------------------------- */
button {
  padding: 12px 25px;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  margin: 10px;
  transition: all 0.2s ease;
}

button:disabled {
  background-color: #3d4450 !important;
  color: #888 !important;
  cursor: not-allowed;
  transform: none !important;
}

.start-btn {
  background: linear-gradient(90deg, #06BFFF, #2D73FF);
  color: white;
  padding: 15px 40px;
  font-size: 1.2rem;
  margin-top: 20px;
}

.retry-btn { background: #66c0f4; color: #1b2838; }
.back-btn { background: #3d4450; color: white; }
.back-btn-small { background: transparent; color: #66c0f4; text-decoration: underline; }

/* 6. 애니메이션
--------------------------------------- */
@keyframes spin { 
  from { transform: rotate(0deg); } 
  to { transform: rotate(360deg); }
}

@keyframes pulse {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}

.loading-overlay p {
  animation: pulse 1.5s infinite;
}
</style>