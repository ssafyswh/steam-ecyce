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
.main-container {
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 90vh; 
  padding-bottom: 17vh;
  box-sizing: border-box;
  width: 100%;
  overflow: hidden;
  background-color: #ffffff;
}
.search-wrapper { 
  width: 100%; 
  max-width: 650px; 
  text-align: center; 
  padding: 0 20px; 
  position: relative;
  z-index: 10; /* 배경 레이어(1)보다 높은 값 */
  /* margin: auto 제거 - 부모의 flex가 이미 중앙 정렬 중 */
}
.logo { font-size: 5rem; margin-bottom: 40px; font-weight: 900; letter-spacing: -2px; line-height: 1; display: flex; justify-content: center; gap: 15px; align-items: center; }
.steam { color: #171a21; text-shadow: 2px 2px 0px #dcdcdc; }
.ecyce { color: #66c0f4; font-weight: 300; }
.search-box { display: flex; align-items: center; background: #ffffff; border: 2px solid #e0e0e0; border-radius: 50px; padding: 15px 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); transition: all 0.3s ease; margin-bottom: 30px; }
.search-box:hover, .search-box.active { border-color: #66c0f4; box-shadow: 0 4px 12px rgba(102, 192, 244, 0.3); }
.search-icon { margin-right: 15px; font-size: 1.2rem; color: #66c0f4; }
input { flex: 1; background: transparent; border: none; color: #171a21; font-size: 1.2rem; outline: none; }
input::placeholder { color: #9aa0a6; }
.clear-btn { background: none; border: none; color: #9aa0a6; cursor: pointer; font-size: 1.2rem; padding: 0 10px; }
.clear-btn:hover { color: #171a21; }
.button-group { display: flex; justify-content: center; gap: 15px; }
.steam-btn { background: linear-gradient(90deg, #66c0f4 0%, #2D73FF 100%); color: white; border: none; padding: 12px 30px; border-radius: 4px; font-size: 1rem; font-weight: bold; cursor: pointer; transition: all 0.2s; box-shadow: 0 2px 5px rgba(45, 115, 255, 0.3); }
.steam-btn:hover { transform: translateY(-2px); box-shadow: 0 4px 8px rgba(45, 115, 255, 0.4); }
.steam-btn.secondary { background: #ffffff; color: #171a21; border: 1px solid #dfe1e5; box-shadow: none; }
.steam-btn.secondary:hover { background: #f8f9fa; border-color: #171a21; }
.result-list { margin-top: 25px; background: #ffffff; border: 1px solid #dfe1e5; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1); text-align: left; max-height: 450px; overflow-y: auto; }
.result-item { display: flex; align-items: center; padding: 12px 20px; border-bottom: 1px solid #f1f3f4; cursor: pointer; transition: background 0.2s; }
.result-item:hover { background-color: #f0f8ff; }
.thumb-wrapper { 
  width: 90px; 
  height: 42px; 
  margin-right: 20px; 
  border-radius: 3px; 
  overflow: hidden; 
  background: #f1f3f4; /* 밝은 배경에 어울리는 연회색 */
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0; /* 이미지가 줄어들지 않게 고정 */
}
.thumb { 
  width: 100%; 
  height: 100%; 
  object-fit: cover; 
}
.info-wrapper { display: flex; flex-direction: column; }
.game-title { font-weight: 600; color: #171a21; font-size: 1rem; }
.appid-badge { color: #66c0f4; font-size: 0.8rem; margin-top: 2px; font-weight: 500; }
.no-result { margin-top: 50px; color: #5f6368; }

/* 플레이스홀더 전용 스타일 */
.fallback-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  background-color: #e8eaed;
  color: #9aa0a6;
}

.placeholder-icon {
  font-size: 1.2rem; /* 리스트용이므로 작은 사이즈 */
  opacity: 0.6;
}

/* 👇 [추가] 전체 보기 버튼 스타일 */
.view-all-container {
  padding: 10px;
  text-align: center;
  background: #f8f9fa;
  border-top: 1px solid #dfe1e5;
}

.view-all-btn {
  background: none;
  border: none;
  color: #66c0f4;
  font-weight: bold;
  font-size: 0.95rem;
  cursor: pointer;
  padding: 10px 20px;
  width: 100%;
  transition: background 0.2s;
}

.view-all-btn:hover {
  background: #eef6fc;
  text-decoration: underline;
}

.no-result-container {
  margin-top: 30px;
  text-align: left;
}

.no-result-msg {
  text-align: center;
  color: #8f98a0;
  margin-bottom: 20px;
}

.recommendation-section {
  margin-top: 20px;
  text-align: left;
}

/* 추천 섹션 내의 리스트는 상단 여백을 줄임 */
.recommendation-section .result-list {
  margin-top: 10px;
}

.ai-recommend-list {
  border-color: #66c0f4;
  background: #fdfdff;
}

.ai-item:hover {
  background-color: #eef6fc;
}

.recommend-title {
  font-size: 0.9rem;
  color: #2D73FF;
  margin-bottom: 8px;
  font-weight: bold;
  padding-left: 5px;
}

.recommend-badge {
  font-size: 0.75rem;
  color: #2D73FF;
  background: rgba(45, 115, 255, 0.1);
  padding: 2px 8px;
  border-radius: 4px;
  width: fit-content;
  margin-top: 4px;
  font-weight: 500;
}

/* MainView.vue <style scoped> 내부 하단에 추가 */

.video-container {
  margin-bottom: 20px;
  animation: fadeIn 0.5s ease-in-out;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.video-container iframe {
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

.close-video-btn {
  background: #f1f3f4;
  border: none;
  padding: 5px 15px;
  border-radius: 20px;
  font-size: 0.8rem;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.close-video-btn:hover {
  background: #e8eaed;
  color: #171a21;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.bg-decorative-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1; /* 콘텐츠보다 뒤로 */
  pointer-events: none;
  user-select: none;
}

/* 도트 그리드 패턴 */
.dot-pattern {
  width: 100%;
  height: 100%;
  background-image: radial-gradient(#dcdcdc 1.2px, transparent 1.2px);
  background-size: 40px 40px; 
  opacity: 0.7;
}

.floating-tags {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.tag {
  position: absolute;
  font-size: 0.85rem;
  font-weight: 700;
  color: #66c0f4;
  /* 가시성을 위해 투명도를 0.2에서 0.5로 상향 */
  opacity: 0.5; 
  padding: 6px 14px;
  border: 1.5px solid rgba(102, 192, 244, 0.4);
  border-radius: 20px;
  background-color: rgba(255, 255, 255, 0.8); /* 흰 배경에서 더 선명하게 */
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
  50% { transform: translateY(-20px) rotate(2deg); }
}


</style>