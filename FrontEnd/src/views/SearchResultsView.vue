<!-- views/SearchResultsView.vue -->

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
          <img 
            v-if="!game.isImageError"
            :src="game.header_image || `https://cdn.akamai.steamstatic.com/steam/apps/${game.appid}/header.jpg`" 
            @error="handleImageError(game)"
            :alt="game.title" 
            loading="lazy"
          >
          <div v-else class="fallback-placeholder">
            <span class="placeholder-icon">🎮</span>
            <span>NO IMAGE</span>
          </div>
        </div>
        <div class="game-info">
          <h3 class="game-title">{{ game.title }}</h3>
        </div>
      </div>
    </div>
    <div v-if="hasMore && games.length > 0" class="load-more-section">
      <button @click="loadMore" :disabled="isLoading" class="load-more-btn">
        <span v-if="isLoading" class="btn-spinner"></span>
        {{ isLoading ? '불러오는 중...' : '결과 더 보기' }}
      </button>
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

const currentPage = ref(0);
const pageSize = 20;
const hasMore = ref(true);

const fetchResults = async (isNewSearch = true) => {
  const query = route.query.q;
  if (!query) return;

  if (isNewSearch) {
    games.value = [];
    currentPage.value = 0;
    hasMore.value = true;
    window.scrollTo(0, 0);
  }

  isLoading.value = true;
  try {
    const offset = currentPage.value * pageSize;
    // limit 없이 요청 -> 전체 데이터 가져옴
    const response = await axios.get(`http://localhost:8000/games/search/`, {
      params: {
        q: query,
        offset: offset,
        limit: pageSize,
      }
    });
    const newGames = response.data.results
    if (isNewSearch) {
      games.value = newGames;
    } else {
      const existingIds = new Set(games.value.map(g => g.appid));
      const filteredNewGames = newGames.filter(g => !existingIds.has(g.appid));

      games.value = [...games.value, ...filteredNewGames];
    };
    
    totalCount.value = response.data.count;
    if (newGames.length < pageSize || games.value.length >= totalCount.value) {
      hasMore.value = false;
    }
  } catch (error) {
    console.error("검색 실패:", error);
  } finally {
    isLoading.value = false;
  }
};

const loadMore = async () => {
  const currentScrollPos = window.scrollY;
  currentPage.value++;
  await fetchResults(false);
  setTimeout(() => {
    window.scrollTo(0, currentScrollPos);
  }, 0);
};

const handleImageError = (game) => {
  game.isImageError = true;
}

onMounted(() => {
  fetchResults(true);
});

// URL 쿼리가 바뀌면 다시 검색 (뒤로가기 등 대응)
watch(() => route.query.q, () => {
  fetchResults(true);
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

.image-wrapper {
  width: 100%;
  aspect-ratio: 460 / 215;
  background: #1b2838; /* 스팀 기본 배경색 */
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  position: relative;
}

.image-wrapper img { width: 100%; height: auto; display: block; object-fit: cover;}

/* 💡 이미지가 없을 때의 스타일 */
.fallback-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #4b6171; /* 차분한 청회색 */
  font-weight: bold;
}

.placeholder-icon {
  font-size: 2.5rem;
  opacity: 0.5;
}

.placeholder-text {
  font-size: 0.8rem;
  letter-spacing: 1px;
  opacity: 0.7;
}

/* 호버 시 배경색을 살짝 밝게 해서 반응형 느낌 주기 */
.game-card:hover .image-wrapper {
  background: #2a475e;
}

.game-info { padding: 15px; }
.game-title { margin: 0 0 5px 0; font-size: 1.1rem; color: white; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.appid { font-size: 0.8rem; color: #66c0f4; }

.loading-box, .no-result { text-align: center; padding: 50px; font-size: 1.2rem; color: #8f98a0; }
.spinner { width: 40px; height: 40px; border: 4px solid #2a475e; border-top-color: #66c0f4; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 20px; }
@keyframes spin { to { transform: rotate(360deg); } }

.load-more-section {
  display: flex;
  justify-content: center;
  margin-top: 40px;
  padding-bottom: 50px;
}

.load-more-btn {
  background: transparent;
  color: #66c0f4;
  border: 1px solid #66c0f4;
  padding: 12px 40px;
  font-size: 1.1rem;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 10px;
}

.load-more-btn:hover:not(:disabled) {
  background: rgba(102, 192, 244, 0.1);
  box-shadow: 0 0 10px rgba(102, 192, 244, 0.3);
}

.load-more-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  border-color: #2a475e;
  color: #8f98a0;
}

/* 버튼 내 작은 스피너 */
.btn-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #2a475e;
  border-top-color: #66c0f4;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
</style>