<!-- views/ProfileView.vue -->
<template>
  <div class="profile-container">
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-box">
        <div class="spinner"></div>
        <p>스팀 라이브러리를 동기화 중입니다...</p>
        <span>잠시만 기다려주세요 (최초 동기화 시 약 1분 정도 소요됩니다.)</span>
      </div>
    </div>

    <div class="profile-header-card">
      <div class="header-top">
        <div class="header-info">
          <h2 class="main-title">🎮 내 스팀 라이브러리</h2>
          <div class="stats-badge" v-if="games.length > 0">
            총 <strong>{{ games.length }}</strong>개의 게임을 소유중
          </div>
        </div>
    
        <div class="header-actions">
          <button v-if="games.length !== 0" @click="$router.push('/recommend')" class="ai-btn">
           🤖 AI 게임 취향 분석
          </button>
          <button @click="syncLibrary" :disabled="isLoading" class="sync-btn-modern">
            {{ isLoading ? '동기화 중...' : '🔄 라이브러리 최신화' }}
          </button>
        </div>
      </div>

      <div class="header-footer">
        <p class="privacy-notice">
          <i class="info-icon">i</i> 라이브러리 정보를 불러오기 위해 스팀 프로필을 <strong>'공개'</strong>로 설정해주세요.
        </p>
      </div>
    </div>

    <!-- 게임 정렬 옵션 선택 -->
    <div class="sort-container">
      <span class="sort-label">정렬 기준</span>
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
    
    <!-- 로딩 상태가 아니고 게임이 없을 때 -->
    <div v-if="!isLoading && games.length === 0" class="empty-state">
      <p>등록된 게임이 없습니다! 위 버튼을 눌러 스팀 정보를 가져오세요!</p>
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
    alert("스팀 연동에 실패했습니다.\n 스팀 프로필의 공개 설정에서 게임 세부 정보가 '공개'로 되어있는지 확인해주세요!");
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  fetchLibrary();
});
</script>

<style scoped>
/* 기본 레이아웃 */
.profile-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

/* 로딩 오버레이 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(27, 40, 56, 0.85);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  backdrop-filter: blur(4px);
}

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

/* 상단 헤더 */
.profile-header-card {
  background: linear-gradient(135deg, #1b2838 0%, #2a475e 100%);
  border-radius: 12px;
  padding: 30px;
  margin-bottom: 30px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(102, 192, 244, 0.1);
  text-align: left;
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  flex-wrap: wrap;
  gap: 20px;
}

.main-title {
  font-size: 2rem;
  margin: 0 0 10px 0;
  color: white;
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.stats-badge {
  display: inline-block;
  background: rgba(102, 192, 244, 0.15);
  color: #66c0f4;
  padding: 6px 16px;
  border-radius: 30px;
  font-size: 0.95rem;
  border: 1px solid rgba(102, 192, 244, 0.3);
}

.stats-badge strong {
  font-size: 1.1rem;
  margin: 0 2px;
}

/* 헤더 내 버튼들 */
.header-actions {
  display: flex;
  gap: 12px;
}

.ai-btn {
  background: linear-gradient(90deg, #8e24aa, #ba68c8);
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
  box-shadow: 0 0 10px rgba(186, 104, 200, 0.4);
  transition: all 0.2s;
}

.ai-btn:hover {
  filter: brightness(1.1);
  transform: scale(1.02);
}

.sync-btn-modern {
  background-color: transparent;
  color: #66c0f4;
  padding: 12px 24px;
  font-weight: bold;
  border: 2px solid #66c0f4;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.sync-btn-modern:hover:not(:disabled) {
  background-color: #66c0f4;
  color: #1b2838;
  box-shadow: 0 0 20px rgba(102, 192, 244, 0.4);
}

.sync-btn-modern:disabled {
  border-color: #4f5b66;
  color: #4f5b66;
  cursor: not-allowed;
}

/* 헤더 푸터 (안내 문구) */
.header-footer {
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.privacy-notice {
  font-size: 0.85rem;
  color: #8f98a0;
  margin: 0;
}

.privacy-notice strong {
  color: #c7d5e0;
}

.info-icon {
  display: inline-block;
  width: 16px;
  height: 16px;
  background: #4f5b66;
  color: white;
  border-radius: 50%;
  text-align: center;
  line-height: 16px;
  font-style: normal;
  font-size: 11px;
  margin-right: 6px;
}

/* 정렬 필터 */
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
  background-color: rgba(42, 71, 94, 0.6);
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

.chip-btn.active {
  background-color: #66c0f4;
  color: #1b2838;
  border-color: #66c0f4;
  font-weight: bold;
  box-shadow: 0 0 12px rgba(102, 192, 244, 0.4);
}

/* 게임 리스트 그리드 */
.empty-state {
  text-align: center;
  padding: 50px;
  color: #8f98a0;
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
  cursor: pointer;
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
  line-height: 1.5;
}

.playtime span {
  color: #66c0f4;
  font-weight: bold;
}
</style>