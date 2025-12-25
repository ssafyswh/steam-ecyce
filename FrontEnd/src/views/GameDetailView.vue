<template>
  <div v-if="!isLoading && game &&game.title" class="detail-wrapper">
    <div class="banner-section" :style="{ backgroundImage: `url(${game.header_image})` }">
      <div class="banner-overlay"></div>

      <!-- Favorite게임이면 보이는거 -->
      <div v-if="isMyFavorite" class="gold-seal">
        <div class="seal-content">
          <span class="trophy">🏆</span>
          <span class="text-top">MY BEST</span>
          <span class="text-main">GAME</span>
        </div>
        <!-- 반짝이는 효과 -->
        <div class="shine"></div>
      </div>

      <div class="banner-content">
        <img :src="game.header_image" class="cover-image" />
        <div class="title-info">
          <h1>{{ game.title }}</h1>
          <div class="tags" v-if="game.genres">
            <span v-for="genre in game.genres.split(', ')" :key="genre" class="genre-tag">
              {{ genre }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <div class="content-container">
      <div class="main-column">
        <section class="description-box">
          <h3>게임 소개</h3>
          <div class="description-text" v-html="game.description || '상세 설명이 없습니다.'"></div>
        </section>

        <section class="ai-section">
          <div class="section-header">
            <h3>🤖 Friday's AI 리뷰 분석</h3>
            <span v-if="game.review_summary?.summary_text" class="update-date">
              최근 분석: {{ new Date(game.review_summary.last_updated_at).toLocaleString('ko-KR', { 
                year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' 
              }) }}
            </span>
          </div>

          <div class="ai-content-box">
            <div v-if="game.review_summary?.status === 'COMPLETED'" class="ai-summary-text">
              <p v-html="formattedSummary"></p>
            </div>

            <div v-if="game.review_summary?.status === 'PROCESSING'" class="ai-loading">
              <div class="mini-spinner"></div>
              <p>스팀 유저들의 리뷰를 AI가 정독하고 요약 중입니다...</p>
            </div>
            <div v-else-if="!game.review_summary?.summary_text && game.review_summary?.status !== 'PROCESSING'" class="ai-placeholder-text">
              <p>이 게임에 대한 AI 리뷰 분석 데이터가 아직 없습니다.</p>
            </div>
              <div class="ai-actions">
                <button 
                  @click="requestAiAnalysis" 
                  class="analysis-req-btn" 
                  :disabled="game.review_summary?.status === 'PROCESSING'"
                >
                  {{ game.review_summary?.summary_text ? '🔄 분석 업데이트' : '🚀 AI 분석 시작하기' }}
                </button>
                <p class="limit-notice" v-if="game.review_summary?.summary_text">
                  * 잦은 호출 방지를 위해 30분마다 업데이트가 가능합니다.
                </p>
              </div>
          </div>
        </section>
      </div>

      <div class="side-column">
        <div class="info-card">
          <div class="stat-item highlight" v-if="game.playtime_total !== ''">
             <span class="label">내 플레이 시간</span>
             <span class="value">{{ (game.playtime_total / 60).toFixed(1) }} 시간</span>
          </div>

          <hr class="divider" v-if="isLoggedIn">

          <div class="stat-item">
            <span class="label">가격</span>
            <span class="value price">
              {{ game.price === 0 ? 'Free to Play' : `₩ ${game.price.toLocaleString()}` }}
            </span>
          </div>

          <div class="stat-item">
            <span class="label">출시일</span>
            <span class="value">{{ game.release_date || '정보 없음' }}</span>
          </div>

          <div class="stat-item">
            <span class="label">배급사</span>
            <span class="value">{{ game.publisher || '정보 없음' }}</span>
          </div>
          
          <button class="back-btn" @click="goToSteam" >STEAM 페이지로 이동</button>
        </div>
      </div>
    </div>
  </div>

  <div v-else class="loading-screen">
    <div class="spinner"></div>
    <p>게임 정보를 불러오는 중...</p>
  </div>
</template>

<script setup>
const goToSteam = () => {
  window.open(`https://store.steampowered.com/app/${game.value.appid}/`);
};

import { ref, onMounted, watch, computed } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';
import { useAuthStore } from '@/stores/auth';

const route = useRoute();
const authStore = useAuthStore();
const game = ref(null);
const isLoading = ref(true); // 로딩 상태 추가
const retryCount = ref(0); // 재시도 횟수 제한
const isMyFavorite = ref(false);

// 👇 [추가됨] 로그인 여부 판단 변수 선언 (이게 없어서 문제가 됨)
// auth.js가 저장해둔 'isLoggedIn' 플래그나 토큰 존재 여부로 초기화
const isLoggedIn = ref(!!localStorage.getItem('isLoggedIn') || !!authStore.token || !!localStorage.getItem('access_token'));

const fetchGameDetail = async () => {
  try {
    // 토큰이 있다면 헤더에 추가해서 내 플레이타임까지 가져오기
    const headers = authStore.token ? { Authorization: `Token ${authStore.token}` } : {};
    const response = await axios.get(`http://localhost:8000/games/${route.params.id}/`, { headers });
    game.value = response.data;
    isMyFavorite.value = response.data.is_favorite;

    if (!game.value || !game.value.title || !game.value.description) {
      // 정보가 불완전할경우 잠시 후 재실행
      if (retryCount.value < 2) {
        retryCount.value++;
        console.log("LOADING...");
        setTimeout(() => fetchGameDetail(), 1000);
      } else {
        console.error("재시도 횟수 초과");
        isLoading.value = false;
        // retryCount.value = 0;
      }
      return;
    }
    isLoading.value = false;
    retryCount.value = 0;
  } catch (error) {
    console.error("데이터 로드 실패:", error);
    alert("게임 정보를 가져올 수 없습니다.");
  }
};

// AI 요약 텍스트의 줄바꿈을 <br>로 변환하여 출력
const formattedSummary = computed(() => {
  if (!game.value?.review_summary?.summary_text) return '';
  return game.value.review_summary.summary_text.replace(/\n/g, '<br>');
});

// 분석 요청 함수 (데이터가 없을 때 사용자가 수동으로 요청하는 기능)
const requestAiAnalysis = async () => {
  if (!game.value) return;
  
  try {
    // 임시로 상태 변경하여 UI 피드백 제공
    if (!game.value.review_summary) {
      game.value.review_summary = { status: 'PROCESSING' };
    } else {
      game.value.review_summary.status = 'PROCESSING';
    }

    // 백엔드에 분석 요청 (이 API는 Django 뷰에서 구현해야 함)
    const headers = authStore.token ? { Authorization: `Token ${authStore.token}` } : {};
    const response = await axios.post(`http://localhost:8000/games/${route.params.id}/analyze-reviews/`, {}, { headers });
    
    // 분석 완료 후 데이터 갱신
    if (response.data.data) {
      game.value.review_summary = response.data.data;
      console.log(response.data.message); // "최근 30분 이내..." 메시지 출력
    } else {
      game.value.review_summary = response.data;
    }
  } catch (error) {
    console.error("AI 분석 요청 실패:", error);
    if (game.value.review_summary) game.value.review_summary.status = 'FAILED';
    alert("분석 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.");
  }
};

// 페이지 이동 검사
watch(() => route.params.id, () => {
  retryCount.value = 0;
  game.value = null;
  isLoading.value = true;
  fetchGameDetail();
});

onMounted(() => {
  fetchGameDetail();
});
</script>

<style scoped>
/* ==========================================
   1. 기본 레이아웃 및 범용 스타일
   ========================================== */
.detail-wrapper { color: #c7d5e0; background-color: #1b2838; min-height: 100vh; }

.banner-section { 
    position: relative; height: 300px; background-size: cover; 
    background-position: center; display: flex; align-items: flex-end; 
}
.banner-overlay { 
    position: absolute; top: 0; left: 0; right: 0; bottom: 0; 
    background: linear-gradient(to bottom, rgba(27,40,56,0.6) 0%, #1b2838 100%); 
    backdrop-filter: blur(5px); 
}
.banner-content { 
    position: relative; z-index: 2; max-width: 1100px; width: 100%; 
    margin: 0 auto; padding: 0 20px 30px; display: flex; gap: 25px; align-items: flex-end; 
}

.cover-image { width: 280px; border-radius: 5px; box-shadow: 0 5px 15px rgba(0,0,0,0.5); }
.title-info h1 { font-size: 3rem; color: white; margin: 0 0 15px 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.8); }

.tags { display: flex; gap: 8px; flex-wrap: wrap; }
.genre-tag { background: rgba(102, 192, 244, 0.2); color: #66c0f4; padding: 4px 10px; border-radius: 4px; font-size: 0.9rem; }

.content-container { 
    max-width: 1100px; margin: 0 auto; padding: 30px 20px; 
    display: grid; grid-template-columns: 1fr 300px; gap: 30px; 
}

/* ==========================================
   2. 메인 컬럼 (게임 소개)
   ========================================== */
.description-box { background: rgba(0,0,0,0.2); padding: 25px; border-radius: 8px; margin-bottom: 30px; }
.description-box h3 { border-bottom: 1px solid #2a475e; padding-bottom: 10px; margin-bottom: 20px; color: white; }
.description-text { line-height: 1.6; font-size: 1rem; color: #acb2b8; }
:deep(.description-text img) { max-width: 100%; height: auto; margin: 10px 0; border-radius: 5px; }

/* ==========================================
   3. 🤖 AI 분석 섹션 (Friday's AI)
   ========================================== */
.ai-section { margin-top: 30px; }

.section-header {
    display: flex; justify-content: space-between; align-items: center;
    border-bottom: 1px solid #2a475e; padding-bottom: 10px; margin-bottom: 20px;
}
.section-header h3 { margin: 0; color: white; }
.update-date { font-size: 0.8rem; color: #647580; }

.ai-content-box {
    background: rgba(102, 192, 244, 0.05); border-left: 4px solid #66c0f4;
    padding: 25px; border-radius: 4px; display: flex; flex-direction: column; gap: 20px;
}

.ai-summary-text {
    line-height: 1.8; color: #dcdedf; font-size: 1.05rem; letter-spacing: 0.5px;
    background: rgba(0, 0, 0, 0.2); padding: 15px; border-radius: 8px;
}

.ai-placeholder-text { color: #8f98a0; font-style: italic; }

.ai-loading { text-align: center; padding: 20px 0; color: #66c0f4; }
.mini-spinner {
    width: 25px; height: 25px; border: 3px solid rgba(102, 192, 244, 0.2);
    border-top-color: #66c0f4; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 15px;
}

.ai-actions {
    display: flex; flex-direction: column; align-items: flex-start; gap: 8px;
    border-top: 1px solid rgba(102, 192, 244, 0.1); padding-top: 15px;
}

.analysis-req-btn {
    background: #66c0f4; color: #1b2838; border: none; padding: 10px 20px;
    border-radius: 4px; font-weight: bold; cursor: pointer; transition: 0.2s;
}
.analysis-req-btn:hover:not(:disabled) { background: white; transform: translateY(-2px); }
.analysis-req-btn:disabled { background: #4f5b66; cursor: not-allowed; opacity: 0.6; }

.limit-notice { font-size: 0.75rem; color: #647580; margin: 0; }

/* ==========================================
   4. 사이드 컬럼 (게임 정보 카드)
   ========================================== */
.info-card { background: #101822; padding: 20px; border-radius: 5px; position: sticky; top: 20px; border: 1px solid #2a475e; }
.stat-item { display: flex; justify-content: space-between; margin-bottom: 15px; align-items: center; }
.stat-item.highlight { background: rgba(102, 192, 244, 0.1); padding: 10px; border-radius: 5px; margin: -10px -10px 20px -10px; }
.label { color: #647580; font-size: 0.9rem; }
.value { color: white; font-weight: bold; text-align: right; }
.value.price { color: #a4d007; }
.divider { border: 0; height: 1px; background: #2a475e; margin: 15px 0; }
.back-btn { 
    width: 100%; margin-top: 20px; background: #2a475e; color: white; 
    border: none; padding: 12px; border-radius: 4px; cursor: pointer; 
    font-weight: bold; transition: 0.2s; 
}
.back-btn:hover { background: #66c0f4; color: black; }

/* ==========================================
   5. 🏆 금장 씰 (Gold Seal)
   ========================================== */
.gold-seal {
    position: absolute; top: 30px; right: 40px; z-index: 10;
    width: 140px; height: 140px; border-radius: 50%;
    background: linear-gradient(135deg, #bf953f, #fcf6ba, #b38728, #fbf5b7, #aa771c);
    box-shadow: 0 0 0 5px #b38728, 0 0 20px rgba(0,0,0,0.5), inset 0 0 20px rgba(107, 72, 5, 0.5);
    display: flex; align-items: center; justify-content: center;
    animation: stampIn 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275); transform: rotate(15deg);
}
.seal-content {
    width: 85%; height: 85%; border: 2px dashed #d69d41; border-radius: 50%;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    color: #5c3a00; text-align: center; font-family: serif;
}
.trophy { font-size: 1.5rem; margin-bottom: -5px; filter: drop-shadow(0 2px 2px rgba(0,0,0,0.2)); }
.text-top { font-size: 0.8rem; font-weight: bold; letter-spacing: 2px; margin-top: 5px; }
.text-main { font-size: 1.6rem; font-weight: 900; line-height: 1; text-transform: uppercase; text-shadow: 1px 1px 0px rgba(255,255,255,0.4); }
.shine {
    position: absolute; top: 0; left: 0; right: 0; bottom: 0; border-radius: 50%;
    background: linear-gradient(45deg, rgba(255,255,255,0) 40%, rgba(255,255,255,0.7) 50%, rgba(255,255,255,0) 60%);
    background-size: 200% 200%; animation: shineMove 3s infinite linear; pointer-events: none;
}

/* ==========================================
   6. 애니메이션 및 기타 (Loading 등)
   ========================================== */
.loading-screen { text-align: center; padding-top: 100px; color: white; }
.spinner { 
    width: 40px; height: 40px; border: 4px solid #2a475e; border-top-color: #66c0f4; 
    border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 20px; 
}

@keyframes spin { to { transform: rotate(360deg); } }
@keyframes stampIn { from { transform: scale(3) rotate(15deg); opacity: 0; } to { transform: scale(1) rotate(15deg); opacity: 1; } }
@keyframes shineMove { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }

/* 반응형 모바일 */
@media (max-width: 768px) {
    .content-container { grid-template-columns: 1fr; }
    .banner-content { flex-direction: column; align-items: flex-start; }
    .cover-image { width: 150px; }
    .gold-seal { width: 100px; height: 100px; top: 10px; right: 10px; }
    .text-top { font-size: 0.6rem; }
    .text-main { font-size: 1.1rem; }
    .trophy { font-size: 1.2rem; }
}
</style>