<template>
  <div class="main-container">
    <div class="search-wrapper">
      <h1 class="logo">
        <span class="friday">FRIDAY</span>
        <span class="games">GAMES</span>
      </h1>
      
      <div class="search-box" :class="{ 'active': searchKeyword.length > 0 || searchResults.length > 0 }">
        <span class="search-icon">🔍</span>
        <input 
          type="text" 
          v-model="searchKeyword" 
          @keyup.enter="onSearchInput"
          placeholder="게임 이름 또는 AppID를 입력하세요" 
        />
        <button v-if="searchKeyword" @click="clearSearch" class="clear-btn">✕</button>
      </div>

      <!-- <div class="button-group" v-if="searchResults.length === 0">
        <button @click="onSearchInput" class="steam-btn">Friday 검색</button>
        <button @click="$router.push('/profile')" class="steam-btn secondary">내 라이브러리</button>
      </div> -->

      <div v-if="searchResults.length > 0" class="result-list">
        <div 
          v-for="game in searchResults" 
          :key="game.appid" 
          class="result-item"
          @click="goToDetail(game.appid)"
        >
          <div class="thumb-wrapper">
            <img :src="game.header_image" alt="cover" class="thumb">
          </div>
          <div class="info-wrapper">
            <span class="game-title">{{ game.title }}</span>
            <span class="appid-badge">ID: {{ game.appid }}</span>
          </div>
        </div>

        <div v-if="totalCount > 20" class="view-all-container">
           <button @click="goToFullSearch" class="view-all-btn">
             + 전체 결과 보기 ({{ totalCount }}개)
           </button>
        </div>
      </div>

      <div v-if="isSearched && searchResults.length === 0" class="no-result">
        <p>검색 결과가 없습니다.</p>
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
const totalCount = ref(0); // 전체 개수 저장용
const isSearched = ref(false);

const clearSearch = () => {
  searchKeyword.value = '';
  searchResults.value = [];
  totalCount.value = 0;
  isSearched.value = false;
  router.push({ query: {} });
};

const goToDetail = (appid) => {
  router.push(`/game/${appid}`);
};

// [추가] 전체 결과 페이지로 이동
const goToFullSearch = () => {
  router.push({ name: 'search-results', query: { q: searchKeyword.value } });
};

const onSearchInput = () => {
  const query = searchKeyword.value.trim();
  if (!query) return;

  if (/^\d+$/.test(query)) {
    goToDetail(query);
    return;
  }
  router.push({ name: 'main', query: { q: query } }).catch(()=>{});
};

const performSearch = async (query) => {
  if (!query) {
      searchResults.value = [];
      isSearched.value = false;
      return;
  }
  try {
    isSearched.value = false;
    searchKeyword.value = query; 
    
    // 👇 [변경] limit=20 파라미터 추가
    const response = await axios.get(`http://localhost:8000/games/search/?q=${query}&limit=20`);
    
    // 백엔드 구조 변경(dict)에 맞춰 데이터 바인딩
    searchResults.value = response.data.results;
    totalCount.value = response.data.count;
    
    isSearched.value = true;
  } catch (error) {
    console.error("검색 실패:", error);
    searchResults.value = [];
    isSearched.value = true;
  }
};

onMounted(() => {
  if (route.query.q) performSearch(route.query.q);
});

watch(() => route.query.q, (newQuery) => {
  performSearch(newQuery);
});
</script>

<style scoped>
/* 기존 스타일 그대로 유지 (생략된 부분은 위와 동일) */
.main-container { display: flex; justify-content: center; align-items: center; min-height: 80vh; background-color: #ffffff; color: #171a21; flex-direction: column; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; }
.search-wrapper { width: 100%; max-width: 650px; text-align: center; padding: 0 20px; }
.logo { font-size: 5rem; margin-bottom: 40px; font-weight: 900; letter-spacing: -2px; line-height: 1; display: flex; justify-content: center; gap: 15px; align-items: center; }
.friday { color: #171a21; text-shadow: 2px 2px 0px #dcdcdc; }
.games { color: #66c0f4; font-weight: 300; }
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
.thumb-wrapper { width: 90px; height: 42px; margin-right: 20px; border-radius: 3px; overflow: hidden; background: #eee; }
.thumb { width: 100%; height: 100%; object-fit: cover; }
.info-wrapper { display: flex; flex-direction: column; }
.game-title { font-weight: 600; color: #171a21; font-size: 1rem; }
.appid-badge { color: #66c0f4; font-size: 0.8rem; margin-top: 2px; font-weight: 500; }
.no-result { margin-top: 50px; color: #5f6368; }

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
</style>