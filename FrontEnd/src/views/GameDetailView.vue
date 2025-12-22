<template>
  <div v-if="game" class="detail-wrapper">
    <div class="banner-section" :style="{ backgroundImage: `url(${game.header_image})` }">
      <div class="banner-overlay"></div>
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
          
          <div class="stat-item highlight" v-if="isLoggedIn && game.playtime_total !== undefined">
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
          
          <button @click="$router.push('/profile')" class="back-btn">⬅ 목록으로 돌아가기</button>
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
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';
import { useAuthStore } from '@/stores/auth';

const route = useRoute();
const authStore = useAuthStore();
const game = ref(null);

// 👇 [추가됨] 로그인 여부 판단 변수 선언 (이게 없어서 문제가 됨)
// auth.js가 저장해둔 'isLoggedIn' 플래그나 토큰 존재 여부로 초기화
const isLoggedIn = ref(!!localStorage.getItem('isLoggedIn') || !!authStore.token || !!localStorage.getItem('access_token'));

const fetchGameDetail = async () => {
  try {
    const token = authStore.token || localStorage.getItem('access_token');
    
    // 헤더 설정
    const config = {
        headers: {},
        withCredentials: true 
    };

    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }

    const response = await axios.get(`http://localhost:8000/games/${route.params.id}/`, config);
    game.value = response.data;
    
    // 데이터 로드 성공 후 상태 재확인
    if (token || localStorage.getItem('isLoggedIn')) {
        isLoggedIn.value = true;
    }

  } catch (error) {
    console.error("데이터 로드 실패:", error);
    alert("게임 정보를 가져올 수 없습니다.");
  }
};

onMounted(() => {
  fetchGameDetail();
});
</script>

<style scoped>
/* 기존 스타일 유지 */
.detail-wrapper { color: #c7d5e0; background-color: #1b2838; min-height: 100vh; }
.banner-section { position: relative; height: 350px; background-size: cover; background-position: center; display: flex; align-items: flex-end; }
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
@media (max-width: 768px) { .content-container { grid-template-columns: 1fr; } .banner-content { flex-direction: column; align-items: flex-start; } .cover-image { width: 150px; } }
</style>