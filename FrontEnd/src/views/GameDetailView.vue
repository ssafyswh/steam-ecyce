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
            <h3>🤖 Friday's AI 분석</h3>
          </div>
          <div class="ai-placeholder">
             <p>AI 분석 기능이 곧 추가될 예정입니다!</p>
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

import { ref, onMounted, watch } from 'vue';
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
      if (retryCount.value < 10) {
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
/* 기존 스타일 유지 */
.detail-wrapper { color: #c7d5e0; background-color: #1b2838; min-height: 100vh; }
.banner-section { position: relative; height: 300px; background-size: cover; background-position: center; display: flex; align-items: flex-end; }
.banner-overlay { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(to bottom, rgba(27,40,56,0.6) 0%, #1b2838 100%); backdrop-filter: blur(5px); }
.banner-content { position: relative; z-index: 2; max-width: 1100px; width: 100%; margin: 0 auto; padding: 0 20px 30px; display: flex; gap: 25px; align-items: flex-end; }
.cover-image { width: 280px; border-radius: 5px; box-shadow: 0 5px 15px rgba(0,0,0,0.5); }
.title-info h1 { font-size: 3rem; color: white; margin: 0 0 15px 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.8); }
.tags { display: flex; gap: 8px; flex-wrap: wrap; }
.genre-tag { background: rgba(102, 192, 244, 0.2); color: #66c0f4; padding: 4px 10px; border-radius: 4px; font-size: 0.9rem; }
.content-container { max-width: 1100px; margin: 0 auto; padding: 30px 20px; display: grid; grid-template-columns: 1fr 300px; gap: 30px; }
.description-box { background: rgba(0,0,0,0.2); padding: 25px; border-radius: 8px; margin-bottom: 30px; }
.description-box h3 { border-bottom: 1px solid #2a475e; padding-bottom: 10px; margin-bottom: 20px; color: white; }
.description-text { line-height: 1.6; font-size: 1rem; color: #acb2b8; }
:deep(.description-text img) { max-width: 100%; height: auto; margin: 10px 0; border-radius: 5px; }
.info-card { background: #101822; padding: 20px; border-radius: 5px; position: sticky; top: 20px; border: 1px solid #2a475e; }
.stat-item { display: flex; justify-content: space-between; margin-bottom: 15px; align-items: center; }
.stat-item.highlight { background: rgba(102, 192, 244, 0.1); padding: 10px; border-radius: 5px; margin: -10px -10px 20px -10px; }
.label { color: #647580; font-size: 0.9rem; }
.value { color: white; font-weight: bold; text-align: right; }
.value.price { color: #a4d007; }
.divider { border: 0; height: 1px; background: #2a475e; margin: 15px 0; }
.back-btn { width: 100%; margin-top: 20px; background: #2a475e; color: white; border: none; padding: 12px; border-radius: 4px; cursor: pointer; font-weight: bold; transition: 0.2s; }
.back-btn:hover { background: #66c0f4; color: black; }
.loading-screen { text-align: center; padding-top: 100px; color: white; }
.spinner { width: 40px; height: 40px; border: 4px solid #2a475e; border-top-color: #66c0f4; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 20px; }
@keyframes spin { to { transform: rotate(360deg); } }

/* 반응형 */
@media (max-width: 768px) {
  .content-container { grid-template-columns: 1fr; }
  .banner-content { flex-direction: column; align-items: flex-start; }
  .cover-image { width: 150px; }
}

/* ---------------------------------- */
/* 🏆 금장 씰 (Gold Seal) 스타일 */
/* ---------------------------------- */
.gold-seal {
  position: absolute;
  top: 30px;    /* 배너 상단에서의 거리 */
  right: 40px;  /* 배너 우측에서의 거리 */
  z-index: 10;
  
  width: 140px;
  height: 140px;
  border-radius: 50%;
  
  /* 금색 그라데이션 배경 */
  background: linear-gradient(135deg, #bf953f, #fcf6ba, #b38728, #fbf5b7, #aa771c);
  
  /* 입체적인 그림자 (도장 찍힌 느낌) */
  box-shadow: 
    0 0 0 5px #b38728, /* 바깥 테두리 */
    0 0 20px rgba(0,0,0,0.5), /* 전체 그림자 */
    inset 0 0 20px rgba(107, 72, 5, 0.5); /* 안쪽 음영 */
    
  display: flex;
  align-items: center;
  justify-content: center;
  
  /* 쿵! 하고 찍히는 애니메이션 */
  animation: stampIn 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  transform: rotate(15deg); /* 살짝 기울이기 */
}

/* 씰 내부 점선 테두리 */
.seal-content {
  width: 85%;
  height: 85%;
  border: 2px dashed #d69d41; /* 진한 금색 점선 */
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #5c3a00; /* 글자색: 짙은 갈색/금색 */
  text-align: center;
  font-family: serif; /* 명조체 계열이 고급스러움 */
}

.trophy {
  font-size: 1.5rem;
  margin-bottom: -5px;
  filter: drop-shadow(0 2px 2px rgba(0,0,0,0.2));
}

.text-top {
  font-size: 0.8rem;
  font-weight: bold;
  letter-spacing: 2px;
  margin-top: 5px;
}

.text-main {
  font-size: 1.6rem;
  font-weight: 900;
  line-height: 1;
  text-transform: uppercase;
  text-shadow: 1px 1px 0px rgba(255,255,255,0.4);
}

/* 은은하게 지나가는 반짝임 효과 */
.shine {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  border-radius: 50%;
  background: linear-gradient(45deg, rgba(255,255,255,0) 40%, rgba(255,255,255,0.7) 50%, rgba(255,255,255,0) 60%);
  background-size: 200% 200%;
  animation: shineMove 3s infinite linear;
  pointer-events: none;
}

/* 애니메이션 정의 */
@keyframes stampIn {
  from { transform: scale(3) rotate(15deg); opacity: 0; }
  to { transform: scale(1) rotate(15deg); opacity: 1; }
}

@keyframes shineMove {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* 모바일 대응: 크기 좀 줄이기 */
@media (max-width: 768px) {
  .gold-seal {
    width: 100px;
    height: 100px;
    top: 10px;
    right: 10px;
  }
  .text-top { font-size: 0.6rem; }
  .text-main { font-size: 1.1rem; }
  .trophy { font-size: 1.2rem; }
}

</style>