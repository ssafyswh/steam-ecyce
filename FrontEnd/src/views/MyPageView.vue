<template>
  <div class="mypage-wrapper" v-if="profileData">
    
    <header class="profile-header">
      <div class="header-container">
        <div class="avatar-section">
          <img :src="profileData.avatar || 'https://via.placeholder.com/150'" alt="Avatar" class="profile-avatar" />
          <div class="status-indicator"></div>
        </div>
        <div class="user-text-info">
          <h1 class="nickname">{{ profileData.nickname || 'Guest' }}</h1>
          <p class="user-id">@{{ route.params.username || authStore.user?.username || 'unknown' }}</p>
        </div>
      </div>
    </header>

    <div class="content-grid">
      <section class="info-card ai-report">
        <div class="card-title">
          <span class="emoji">🔍</span>
          <h2>AI 게임 성향 리포트</h2>
        </div>
        
        <div v-if="profileData.ai_info" class="card-content">
          <div class="analysis-hero">
            <span class="label">당신의 플레이 스타일은?</span>
            <h3 class="gamer-type">"{{ profileData.ai_info.gamer_type }}"</h3>
          </div>
          <p class="description-text">{{ profileData.ai_info.analysis_text }}</p>
          
          <div class="recommend-box">
            <h4>✨ 추천 드리는 새로운 게임</h4>
            <div class="rec-items">
              <div v-for="game in profileData.ai_info.recommendations" :key="game.title" class="rec-bubble">
                <span class="rec-title">{{ game.title }}</span>
                <span class="rec-reason">{{ game.reason }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <div v-else class="empty-placeholder">
          <p>아직 분석된 정보가 없습니다.</p>
          <router-link to="/worldcup" class="btn-primary">월드컵 하러 가기</router-link>
        </div>
      </section>

      <aside class="side-area">
        <section class="info-card favorite-game">
          <div class="card-title">
            <span class="emoji">⭐</span>
            <h2>나의 최애 게임</h2>
          </div>
          <div v-if="profileData.favorite_game" class="fav-content">
            <router-link :to="{ name: 'GameDetail', params: { id: profileData.favorite_game.appid } }" class="game-link">
              <div class="img-frame">
                <img :src="profileData.favorite_game.header_image" alt="Game" />
              </div>
              <p class="game-title">{{ profileData.favorite_game.title }}</p>
            </router-link>
          </div>
          <div v-else class="empty-small">등록된 게임이 없습니다.</div>
        </section>

        <div class="management-zone">
          <button @click="handleWithdraw" class="btn-withdraw">회원 탈퇴</button>
        </div>
      </aside>
    </div>
  </div>

  <div v-else class="loading-state">
    <p>데이터를 불러오는 중입니다...</p>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

// 1. 모든 반응형 변수는 반드시 최상단(top-level)에 선언해야 템플릿이 인식합니다.
const route = useRoute()
const authStore = useAuthStore()
const profileData = ref(null) // 범인: 이게 선언 안 되어 있거나 오타나면 에러 남

const fetchProfileData = async () => {
  try {
    const username = route.params.username
    // API 주소 설정
    const url = username 
      ? `http://localhost:8000/api/auth/user/mypage/${username}/`
      : `http://localhost:8000/api/auth/user/mypage/`
    
    const res = await axios.get(url, {
      headers: { Authorization: `Bearer ${authStore.token}` },
      withCredentials: true
    })
    
    profileData.value = res.data
    console.log("데이터 로드 성공:", res.data)
  } catch (error) {
    console.error("데이터 로딩 실패:", error)
  }
}

onMounted(() => {
  fetchProfileData()
})

// 유저가 바뀔 때(남의 페이지로 이동 시) 재호출
watch(() => route.params.username, () => {
  fetchProfileData()
})

const handleWithdraw = async () => {
  if (!confirm("정말로 탈퇴하시겠습니까?")) return
  try {
    await axios.delete('http://localhost:8000/api/auth/user/withdraw/', {
      headers: { Authorization: `Bearer ${authStore.token}` },
      withCredentials: true
    })
    alert("탈퇴 성공")
    window.location.href = '/'
  } catch (err) {
    alert("탈퇴 실패")
  }
}
</script>

<style scoped>
/* 밝은 테마 스타일 */
.mypage-wrapper {
  max-width: 1100px;
  margin: 0 auto;
  padding: 40px 20px;
  background-color: #f8f9fa;
  min-height: 100vh;
}

.profile-header {
  background: white;
  padding: 40px;
  border-radius: 20px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  margin-bottom: 30px;
  border: 1px solid #eee;
}

.header-container { display: flex; align-items: center; gap: 30px; }

.profile-avatar {
  width: 120px; height: 120px;
  border-radius: 50%;
  border: 4px solid #fff;
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
  object-fit: cover;
}

.nickname { font-size: 2rem; margin: 0; color: #333; }
.user-id { color: #888; margin: 5px 0; }

.badge-row { display: flex; gap: 8px; margin-top: 10px; }
.badge {
  padding: 4px 12px; border-radius: 20px; font-size: 0.8rem;
  background: #e3f2fd; color: #1976d2; font-weight: 600;
}
.badge.secondary { background: #e8f5e9; color: #2e7d32; }

.content-grid { display: grid; grid-template-columns: 1.5fr 1fr; gap: 25px; }

.info-card {
  background: white; border-radius: 15px; padding: 25px;
  border: 1px solid #eee; box-shadow: 0 2px 8px rgba(0,0,0,0.02);
}

.card-title { display: flex; align-items: center; gap: 8px; margin-bottom: 20px; }
.card-title h2 { font-size: 1.1rem; margin: 0; color: #444; }

.gamer-type { color: #42b883; font-size: 1.5rem; margin: 10px 0; }
.description-text { line-height: 1.6; color: #555; }

.rec-items { display: flex; flex-direction: column; gap: 10px; margin-top: 15px; }
.rec-bubble {
  background: #f1f3f5; padding: 15px; border-radius: 10px;
  border-left: 4px solid #42b883;
}
.rec-title { font-weight: bold; display: block; color: #333; }
.rec-reason { font-size: 0.85rem; color: #666; }

.img-frame { border-radius: 12px; overflow: hidden; margin-top: 10px; }
.img-frame img { width: 100%; display: block; transition: 0.3s; }
.game-link:hover img { transform: scale(1.05); }
.game-title { text-align: center; font-weight: bold; margin-top: 10px; }

.management-zone { margin-top: 20px; text-align: right; }
.btn-withdraw { background: none; border: none; color: #ccc; cursor: pointer; text-decoration: underline; }
.btn-withdraw:hover { color: #f44336; }

.loading-state { text-align: center; padding: 100px; color: #888; }
</style>