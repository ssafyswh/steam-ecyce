<!-- views/ProfileView.vue -->
<template>
  <div class="profile-container">
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-box">
        <div class="spinner"></div>
        <p>스팀 라이브러리를 동기화 중입니다...</p>
        <span>잠시만 기다려주세요 (약 1분 정도 소요됩니다.)</span>
      </div>
    </div>
    <h2>🎮 내 스팀 라이브러리</h2>
    
    <!-- 게임이 하나라도 있어야 버튼이 보이게 설정 -->
    <button @click="$router.push('/recommend')" class="ai-btn">
    🤖 AI 게임 취향 분석하러 가기
    </button>
    
    <div class="controls">
      <button @click="syncLibrary" :disabled="isLoading" class="sync-btn">
        {{ isLoading ? '스팀과 동기화 중...' : '🔄 라이브러리 최신화 (Steam Sync)' }}
      </button>
      <p v-if="games.length > 0">총 {{ games.length }}개의 게임을 소유중입니다.</p>
      <!-- 게임 정렬 옵션 선택 -->
      <div class="sort-container">
        <span class="sort-label">정렬 기준:</span>
        <div class="chip-group">
          <button 
            v-for="option in sortOptions" 
            :key="option.value" 
            :class="['chip-btn', { active: sortBy === option.value }]"
            @click="sortBy = option.value"
          >
            {{ option.label }}
          </button>
        </div>
      </div>
    </div>

    <!-- 로딩 상태가 아니고 게임이 없을 때 -->
    <div v-if="!isLoading && games.length === 0" class="empty-state">
      <p>등록된 게임이 없습니다. 위 버튼을 눌러 스팀 정보를 가져오세요!</p>
    </div>

    <!-- 게임 그리드 리스트 -->
    <div class="game-grid">
      <div v-for="item in sortedGames" :key="item.game.appid" class="game-card" @click="$router.push(`/game/${item.game.appid}`)">
        <div class="image-wrapper">
          <img :src="item.game.header_image" :alt="item.game.title" loading="lazy" />
        </div>
        <div class="game-info">
          <h3 class="game-title">{{ item.game.title }}</h3>
          <p class="playtime">
            총 플레이: <span>{{ (item.playtime_total / 60).toFixed(1) }} 시간</span><br>
            최근 플레이: <span>{{ (item.playtime_recent_2weeks / 60).toFixed(1) }} 시간</span>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';

const router = useRouter();
const authStore = useAuthStore();

const games = ref([]);
const isLoading = ref(false);
const sortBy = ref('total');
const sortOptions = [
  { label: '제목', value: 'title'},
  { label: '총 플레이타임', value: 'total'},
  { label: '최근 플레이(2주)', value: 'recent'},
]

// 게임 목록 정렬 (제목 / 총 플레이 / 최근 플레이)
const sortedGames = computed(() => {
  return [...games.value].sort((a, b) => {
    if (sortBy.value === 'title') {
      return a.game.title.localeCompare(b.game.title);
    } else if (sortBy.value === 'total') {
      return b.playtime_total - a.playtime_total;
    } else if (sortBy.value === 'recent') {
      return b.playtime_recent_2weeks - a.playtime_recent_2weeks;
    }
    return 0;
  })
})


// DB에 저장된 게임 목록 가져오기
const fetchLibrary = async () => {
  try {
    const response = await axios.get('http://localhost:8000/games/library/', {
      headers: { Authorization: `Token ${authStore.token}` }
      // 만약 session/cookie 방식이라면 withCredentials: true
    });
    games.value = response.data;
  } catch (error) {
    console.error("게임 목록 로드 실패:", error);
  }
};

// 스팀 API와 동기화 요청
const syncLibrary = async () => {
  if (isLoading.value) return;
  isLoading.value = true;
  
  try {
    const response = await axios.post('http://localhost:8000/games/library/', {}, {
      // headers 또는 withCredentials 설정 확인
      withCredentials: true 
    });
    alert(`동기화 완료! ${response.data.updated_count}개의 게임이 업데이트 되었습니다.`);
    
    // 동기화 끝난 후 목록 다시 불러오기
    await fetchLibrary();
  } catch (error) {
    console.error("동기화 실패:", error);
    alert("스팀 연동에 실패했습니다.");
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  fetchLibrary();
});
</script>

<style scoped>
.profile-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.controls {
  margin-bottom: 30px;
  text-align: center;
}

.sync-btn {
  background-color: #1b2838; /* 스팀 테마색 */
  color: #66c0f4;
  padding: 10px 20px;
  font-size: 1rem;
  border: 1px solid #66c0f4;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.3s;
}

.sync-btn:hover {
  background-color: #66c0f4;
  color: white;
}

.sync-btn:disabled {
  background-color: #333;
  border-color: #555;
  cursor: not-allowed;
}

.game-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

.game-card {
  background: #2a475e;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0,0,0,0.3);
  transition: transform 0.2s;
}

.game-card:hover {
  transform: translateY(-5px);
}

.image-wrapper img {
  width: 100%;
  height: auto;
  display: block;
}

.game-info {
  padding: 15px;
  color: #c7d5e0;
  text-align: left;
}

.game-title {
  font-size: 1.1rem;
  margin: 0 0 10px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: white;
}

.playtime {
  font-size: 0.9rem;
  color: #8f98a0;
}

.playtime span {
  color: #66c0f4;
  font-weight: bold;
}

.ai-btn {
  background: linear-gradient(90deg, #8e24aa, #ba68c8);
  color: white;
  padding: 10px 20px;
  margin-left: 15px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
  box-shadow: 0 0 10px rgba(186, 104, 200, 0.4);
}
.ai-btn:hover {
  filter: brightness(1.1);
  transform: scale(1.02);
}

.sort-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  margin-bottom: 25px;
}

.sort-label {
  color: #8f98a0;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.chip-group {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: center;
}

.chip-btn {
  background-color: rgba(42, 71, 94, 0.6); /* 스팀 카드 배경색 계열 */
  color: #c7d5e0;
  border: 1px solid rgba(102, 192, 244, 0.2);
  padding: 8px 18px;
  border-radius: 20px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.chip-btn:hover {
  background-color: rgba(102, 192, 244, 0.2);
  border-color: rgba(102, 192, 244, 0.5);
  color: white;
}

/* 활성화된 칩 스타일 */
.chip-btn.active {
  background-color: #66c0f4;
  color: #1b2838;
  border-color: #66c0f4;
  font-weight: bold;
  box-shadow: 0 0 12px rgba(102, 192, 244, 0.4);
}

.game-count {
  margin-top: 15px;
  color: #8f98a0;
}

.game-count strong {
  color: #66c0f4;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(27, 40, 56, 0.85); /* 스팀 배경색 + 투명도 */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999; /* 최상단에 위치 */
  backdrop-filter: blur(4px); /* 배경 흐리게 처리 */
}

/* 로딩 박스 */
.loading-box {
  text-align: center;
  color: white;
}

.loading-box p {
  font-size: 1.2rem;
  margin-top: 20px;
  font-weight: bold;
}

.loading-box span {
  display: block;
  margin-top: 10px;
  color: #8f98a0;
  font-size: 0.9rem;
}

/*스피너 */
.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #2a475e;
  border-top-color: #66c0f4;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>