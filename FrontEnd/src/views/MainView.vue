<!-- views/MainView.vue -->
<template>
  <div class="main-container">
    <div class="bg-decorative-layer">
      <div class="dot-pattern"></div>
      <div class="floating-tags">
        <span class="tag t1">#RPG</span>
        <span class="tag t2">#Action</span>
        <span class="tag t3">#Indie</span>
        <span class="tag t4">#FPS</span>
        <span class="tag t5">#Simulation</span>
        <span class="tag t6">#Strategy</span>
      </div>
    </div>
    <div class="search-wrapper">
      <div v-if="showSecretVideo" class="video-container">
        <iframe 
          width="800" 
          height="735" 
          src="https://www.youtube.com/embed/0E15Mw7pjJw?autoplay=1" 
          title="YouTube video player" 
          frameborder="0" 
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
          allowfullscreen>
        </iframe>
        <button @click="showSecretVideo = false" class="close-video-btn">✕</button>
      </div>

      <h1 class="logo">
        <span class="steam" style="user-select: none;">Steam</span>
        <span class="ecyce" @click="openEcyce" style="user-select: none;">Ecyce</span>
      </h1>
      
      <div class="search-box" :class="{ 'active': searchKeyword.length > 0 || searchResults.length > 0 }">
        <span class="search-icon">🔍</span>
        <input 
          type="text" 
          :value="searchKeyword"
          @input="e => { searchKeyword = e.target.value; handleInput(); }"
          @keyup.enter="onSearchInput"
          placeholder="검색어를 입력하세요" 
        />
        <button v-if="searchKeyword" @click="clearSearch" class="clear-btn">✕</button>
      </div>

      <div v-if="searchResults.length > 0" class="result-list">
        <div 
          v-for="game in searchResults" 
          :key="game.appid" 
          class="result-item"
          @click="goToDetail(game.appid)"
        >
          <div class="thumb-wrapper">
            <img 
              v-if="!game.isImageError"
              :src="game.header_image || `https://cdn.akamai.steamstatic.com/steam/apps/${game.appid}/header.jpg`"
              @error="handleImageError(game)" 
              alt="cover" 
              class="thumb">
            <div v-else class="fallback-placeholder">
              <span class="placeholder-icon">🎮</span>
            </div>
          </div>
          <div class="info-wrapper">
            <span class="game-title">{{ game.title }}</span>
          </div>
        </div>

        <div v-if="totalCount > 5" class="view-all-container">
           <button @click="goToFullSearch" class="view-all-btn">
             + 전체 결과 보기 ({{ totalCount }}개)
           </button>
        </div>
      </div>

      <div v-if="isSearched && searchResults.length === 0" class="no-result-container">
        <p>🔍 '{{ searchKeyword }}'에 대한 정확한 검색 결과가 없습니다.</p>
      </div>
      <div v-if="recommendations.length > 0" class="recommendation-section">
        <p class="recommend-title">✨ 혹시 이 게임을 찾으셨나요?</p>
        <div class="result-list ai-recommend-list">
          <div
            v-for="game in recommendations"
            :key="game.appid"
            class="result-item"
            @click="goToDetail(game.appid)"
          >
            <div class="thumb-wrapper">
              <img
                v-if="!game.isImageError"
                :src="game.header_image || `https://cdn.akamai.steamstatic.com/steam/apps/${game.appid}/header.jpg`"
                @error="handleImageError(game)"
                class="thumb"
              >
              <div v-else class="fallback-placeholder">
                <span class="placeholder-icon">🎮</span>
              </div>
            </div>
            <div class="info-wrapper">
              <span class="game-title">{{ game.title }}</span>
              <span class="recommend-badge">추천됨</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import axios from 'axios';

const router = useRouter();
const route = useRoute();

const searchKeyword = ref('');
const searchResults = ref([]);
const recommendations = ref([])
const totalCount = ref(0); // 전체 개수 저장용
const isSearched = ref(false);
const isLoading = ref(false)

let debounceTimeout = null;
let abortController = null;
const lastRequestTime = ref(0);

// 이미지 url이 유효하지 않을 때
const handleImageError = (game) => {
  game.isImageError = true;
};

// 검색 메인 로직
const performSearch = async (query) => {
  if (!query) {
      searchResults.value = [];
      recommendations.value = [];
      isSearched.value = false;
      totalCount.value = 0;
      return;
  }

  if (abortController) {
    abortController.abort();
  }

  abortController = new AbortController();
  const currentRequestTime = Date.now();
  lastRequestTime.value = currentRequestTime;

  try {
    isLoading.value = true;
    searchKeyword.value = query; 

    const response = await axios.get(`http://localhost:8000/games/search/`, {
      params: {q: query, limit: 5},
      signal: abortController.signal
    });

    if (currentRequestTime !== lastRequestTime.value) {
      return;
    }

    searchResults.value = response.data.results;
    totalCount.value = response.data.count;
    // 검색 결과가 없을 경우 ai 추천 결과 할당
    if (searchResults.value.length === 0) {
      recommendations.value = response.data.recommendations || [];
      console.log("추천 데이터 확인:", recommendations.value);
    } else {
      recommendations.value = [];
    }

    isSearched.value = true;
  } catch (error) {
    if (axios.isCancel(error)) {
      console.log('이전 요청 취소됨:', query);
    } else {
      console.log('검색 실패:', error);
    }
  } finally {
    if (currentRequestTime === lastRequestTime.value) {
      isLoading.value = false;
    }
  }
};

const handleInput = () => {
  const query = searchKeyword.value.trim();

  if (debounceTimeout) clearTimeout(debounceTimeout);

  if (!query) {
    if (abortController) abortController.abort();
    searchResults.value = [];
    recommendations.value = [];
    isSearched.value = false;
    totalCount.value = 0;
    router.replace({ query: {} });
    return;
  }

  debounceTimeout = setTimeout(() => {
    performSearch(query);
    router.replace({ query: { q: query }}).catch(() => {});
  }, 1200);
}

// 엔터 입력하면 바로 실행
const onSearchInput = () => {
  if (debounceTimeout) clearTimeout(debounceTimeout);
  const query = searchKeyword.value.trim();
  if (query) performSearch(query);
};

// 검색어 초기화
const clearSearch = () => {
  if (abortController) abortController.abort();
  searchKeyword.value = '';
  searchResults.value = [];
  recommendations.value = [];
  totalCount.value = 0;
  isSearched.value = false;
  router.push({ query: {} });
};

// 개별 게임 페이지로 이동
const goToDetail = (appid) => {
  router.push(`/game/${appid}`);
};

// 전체 결과 페이지로 이동
const goToFullSearch = () => {
  router.push({ name: 'search-results', query: { q: searchKeyword.value } });
};

// 이스터에그
const showSecretVideo = ref(false);
const clickCount = ref(0);
let clickTimer = null;

const openEcyce = () => {
  clickCount.value++;
  if (clickTimer) clearTimeout(clickTimer);
  if (clickCount.value === 3) {
    showSecretVideo.value = true;
    clickCount.value = 0;
    return;
  }
  clickTimer = setTimeout(() => {
    clickCount.value = 0;
  }, 400);
};

onMounted(() => {
  if (route.query.q) {
    searchKeyword.value = route.query.q;
    performSearch(route.query.q)
  };
});

watch(() => route.query.q, (newQuery) => {
  if (newQuery) {
    performSearch(newQuery);
  } else {
    // 검색어가 없어지면 결과창을 비움
    clearSearch();
  }
});
</script>

<style scoped>
/* 1. 레이아웃 메인 컨테이너 */
.main-container {
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: flex-start; /* 검색 결과 생성 시 위치 고정을 위해 상단 정렬 */
  align-items: center;
  
  width: 100%;
  min-height: 100vh;
  padding-top: 15vh; /* 로고와 검색창의 초기 높이 결정 */
  padding-bottom: 10vh;
  
  background-color: #ffffff;
  overflow-x: hidden;
  box-sizing: border-box;
}

/* 2. 배경 장식 레이어 */
.bg-decorative-layer {
  position: absolute;
  inset: 0;
  z-index: 1;
  pointer-events: none;
  user-select: none;
}

.dot-pattern {
  width: 100%;
  height: 100%;
  background-image: radial-gradient(#dcdcdc 1.2px, transparent 1.2px);
  background-size: 40px 40px;
  opacity: 0.6;
}

.tag {
  position: absolute;
  padding: 6px 14px;
  font-size: 0.85rem;
  font-weight: 700;
  color: #66c0f4;
  background: rgba(255, 255, 255, 0.8);
  border: 1.5px solid rgba(102, 192, 244, 0.3);
  border-radius: 20px;
  opacity: 0.5;
  animation: subtleFloat 6s infinite ease-in-out;
}

.t1 { top: 10%; left: 8%; animation-delay: 0s; }
.t2 { top: 15%; right: 8%; animation-delay: 1s; }
.t3 { bottom: 15%; left: 10%; animation-delay: 2s; }
.t4 { bottom: 12%; right: 10%; animation-delay: 3s; }
.t5 { top: 45%; left: 5%; animation-delay: 4s; }
.t6 { top: 50%; right: 5%; animation-delay: 5.5s; }

@keyframes subtleFloat {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-15px) rotate(2deg); }
}

/* 3. 콘텐츠 영역 (검색창 & 로고) */
.search-wrapper {
  position: relative;
  z-index: 10;
  width: 100%;
  max-width: 650px;
  padding: 0 20px;
  text-align: center;
}

.logo {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  margin-bottom: 40px;
  font-size: 5rem;
  font-weight: 900;
  letter-spacing: -2px;
}

.steam { color: #171a21; text-shadow: 2px 2px 0px #dcdcdc; }
.ecyce { color: #66c0f4; font-weight: 300; }

/* 검색 박스 */
.search-box {
  display: flex;
  align-items: center;
  padding: 15px 25px;
  background: #ffffff;
  border: 2px solid #e0e0e0;
  border-radius: 50px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  transition: all 0.3s ease;
  margin-bottom: 30px;
}

.search-box.active, .search-box:focus-within {
  border-color: #66c0f4;
  box-shadow: 0 4px 12px rgba(102, 192, 244, 0.3);
}

.search-icon { margin-right: 15px; font-size: 1.2rem; color: #66c0f4; }
.search-box input { flex: 1; border: none; outline: none; font-size: 1.2rem; background: transparent; color: #171a21; }
.clear-btn { background: none; border: none; color: #9aa0a6; cursor: pointer; font-size: 1.2rem; padding: 0 10px; }

/* 4. 결과 리스트 및 아이템 */
.result-list {
  margin-top: 25px;
  background: #ffffff;
  border: 1px solid #dfe1e5;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
  overflow: hidden;
  text-align: left;
  max-height: 500px;
  overflow-y: auto;
}

.result-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  border-bottom: 1px solid #f1f3f4;
  cursor: pointer;
  transition: background 0.2s;
}

.result-item:hover { background-color: #f0f8ff; }

.thumb-wrapper {
  width: 90px; height: 42px;
  margin-right: 20px;
  border-radius: 3px;
  overflow: hidden;
  background: #f1f3f4;
  flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
}

.thumb { width: 100%; height: 100%; object-fit: cover; }
.game-title { font-weight: 600; color: #171a21; font-size: 1rem; }

/* 5. 추천 섹션 및 특수 요소 */
.recommendation-section { margin-top: 20px; text-align: left; }
.recommend-title { font-size: 0.9rem; color: #2D73FF; font-weight: bold; margin-bottom: 8px; padding-left: 5px; }
.ai-recommend-list { border-color: #66c0f4; background: #fdfdff; }
.recommend-badge {
  font-size: 0.75rem; color: #2D73FF; background: rgba(45, 115, 255, 0.1);
  padding: 2px 8px; border-radius: 4px; margin-top: 4px; display: inline-block;
}

.view-all-container { padding: 10px; text-align: center; background: #f8f9fa; border-top: 1px solid #dfe1e5; }
.view-all-btn { background: none; border: none; color: #66c0f4; font-weight: bold; cursor: pointer; width: 100%; padding: 10px; }
.view-all-btn:hover { text-decoration: underline; }

.no-result-container { margin-top: 30px; text-align: left; color: #5f6368; }

/* 6. 비디오 및 기타 */
.video-container { margin-bottom: 30px; display: flex; flex-direction: column; align-items: center; gap: 15px; }
.video-container iframe { border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
.close-video-btn { background: #f1f3f4; border: none; padding: 8px 20px; border-radius: 20px; cursor: pointer; transition: 0.2s; }
.close-video-btn:hover { background: #e8eaed; }

/* 플레이스홀더 */
.fallback-placeholder { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; background-color: #e8eaed; color: #9aa0a6; }
</style>