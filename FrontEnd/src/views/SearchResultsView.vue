<template>
  <div class="search-page-container">
    <div class="header-section">
      <h2>🔍 '{{ route.query.q }}' 검색 결과</h2>
      <p class="count-text">총 <span class="highlight">{{ totalCount }}</span>개의 게임이 발견되었습니다.</p>
      <button @click="$router.push('/')" class="back-btn">메인으로</button>
    </div>

    <div v-if="isLoading" class="loading-box">
      <div class="spinner"></div>
      <p>전체 게임을 불러오는 중...</p>
    </div>

    <div v-else class="game-grid">
      <div 
        v-for="game in games" 
        :key="game.appid" 
        class="game-card"
        @click="$router.push(`/game/${game.appid}`)"
      >
        <div class="image-wrapper">
          <img :src="game.header_image" :alt="game.title" loading="lazy">
        </div>
        <div class="game-info">
          <h3 class="game-title">{{ game.title }}</h3>
          <span class="appid">ID: {{ game.appid }}</span>
        </div>
      </div>
    </div>
    
    <div v-if="!isLoading && games.length === 0" class="no-result">
      <p>검색 결과가 없습니다.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';

const route = useRoute();
const router = useRouter();
const games = ref([]);
const totalCount = ref(0);
const isLoading = ref(false);

const fetchAllResults = async () => {
  const query = route.query.q;
  if (!query) return;

  isLoading.value = true;
  try {
    // limit 없이 요청 -> 전체 데이터 가져옴
    const response = await axios.get(`http://localhost:8000/games/search/?q=${query}`);
    games.value = response.data.results;
    totalCount.value = response.data.count;
  } catch (error) {
    console.error("검색 실패:", error);
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  fetchAllResults();
});

// URL 쿼리가 바뀌면 다시 검색 (뒤로가기 등 대응)
watch(() => route.query.q, () => {
  fetchAllResults();
});
</script>

<style scoped>
.search-page-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
  color: #c7d5e0;
}

.header-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 30px;
  border-bottom: 1px solid #2a475e;
  padding-bottom: 20px;
}

h2 { margin: 0; font-size: 2rem; color: white; }
.highlight { color: #66c0f4; font-weight: bold; }
.count-text { font-size: 1.1rem; color: #8f98a0; margin-left: 20px; flex: 1; }

.back-btn {
  background: #2a475e;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  transition: 0.2s;
}
.back-btn:hover { background: #66c0f4; color: black; }

.game-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

.game-card {
  background: #16202d;
  border-radius: 5px;
  overflow: hidden;
  box-shadow: 0 4px 10px rgba(0,0,0,0.3);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  border: 1px solid #1b2838;
}

.game-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(102, 192, 244, 0.2);
  border-color: #66c0f4;
}

.image-wrapper img { width: 100%; height: auto; display: block; }
.game-info { padding: 15px; }
.game-title { margin: 0 0 5px 0; font-size: 1.1rem; color: white; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.appid { font-size: 0.8rem; color: #66c0f4; }

.loading-box, .no-result { text-align: center; padding: 50px; font-size: 1.2rem; color: #8f98a0; }
.spinner { width: 40px; height: 40px; border: 4px solid #2a475e; border-top-color: #66c0f4; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 20px; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>