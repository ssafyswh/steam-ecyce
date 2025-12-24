<template>
  <div class="mypage-container" v-if="profileData">
    <header class="page-header">
      <h1>마이페이지</h1>
      <p class="user-title"><span>{{ profileData.nickname }}</span></p>
    </header>

    <div class="dashboard-grid">
      <section class="card ai-card">
        <h2>🎮 Friday의 유저 취향 분석</h2>
        <div v-if="profileData.ai_info" class="card-body">
          <h3 class="type-highlight">"{{ profileData.ai_info.gamer_type }}"</h3>
          <p class="analysis-text">{{ profileData.ai_info.analysis_text }}</p>
          <div class="rec-list">
            <h4>추천 게임</h4>
            <ul>
              <li v-for="game in profileData.ai_info.recommendations" :key="game.title">
                <b>{{ game.title }}</b>: {{ game.reason }}
              </li>
            </ul>
          </div>
        </div>
        <div v-else class="empty-state">아직 분석 데이터가 없습니다. 분석을 진행해 주세요!</div>
      </section>

      <section class="card fav-card">
        <h2>🏆 나의 최애 게임</h2>
        <div v-if="profileData.favorite_game" class="card-body">
          <img :src="profileData.favorite_game.header_image" class="game-img" />
          <p class="game-name">{{ profileData.favorite_game.title }}</p>
        </div>
        <div v-else class="empty-state">월드컵을 통해 최애 게임을 선정해 보세요!</div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const profileData = ref(null)

onMounted(async () => {
  try {
    const res = await axios.get('http://localhost:8000/api/auth/user/mypage/', {
      headers: { Authorization: `Bearer ${authStore.token}` }
    })
    profileData.value = res.data
  } catch (error) {
    console.error("데이터 로딩 실패:", error)
  }
})
</script>

<style scoped>
.mypage-container { max-width: 1100px; margin: 0 auto; padding: 40px 20px; color: #e5e5e5; }
.page-header { color: #166c9e; margin-bottom: 30px; border-bottom: 2px solid #2a475e; padding-bottom: 15px; }
.user-title span { color: #66c0f4; font-weight: bold; }
.dashboard-grid { display: grid; grid-template-columns: 1.5fr 1fr; gap: 30px; }
.card { background: #1b2838; border-radius: 8px; padding: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
.type-highlight { color: #42b883; margin-bottom: 15px; }
.game-img { width: 100%; border-radius: 5px; margin-bottom: 10px; }
</style>