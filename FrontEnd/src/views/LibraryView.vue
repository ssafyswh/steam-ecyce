<!-- views/LibraryView.vue -->
<template>
  <div class="profile-container">
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-box">
        <div class="spinner"></div>
        <p>스팀 라이브러리를 동기화 중입니다...</p>
        <span>최초 동기화 시 약 1분 정도 소요됩니다.</span>
      </div>
    </div>

    <div class="profile-header-card">
      <div class="header-top">
        <div class="header-info">
          <h2 class="main-title">내 스팀 라이브러리</h2>
          <div class="stats-badge" v-if="games.length > 0">
            총 <strong>{{ games.length }}</strong>개의 게임
          </div>
        </div>
    
        <div class="header-actions">
          <button 
            v-if="games.length !== 0" 
            @click="$router.push('/recommend')" 
            class="ai-btn"
          >
            🤖 AI 취향 분석
          </button>
          <button 
            @click="syncLibrary" 
            :disabled="isLoading" 
            class="sync-btn-modern"
          >
            {{ isLoading ? '동기화 중...' : '🔄 라이브러리 최신화' }}
          </button>
        </div>
      </div>

      <div class="header-footer">
        <p class="privacy-notice">
          <span class="info-badge">TIP</span>
          라이브러리를 불러오려면 스팀 프로필을
          <a :href="steamSettingsUrl" target="_blank" class="privacy-link">'공개'</a>
          로 설정해 주세요.
        </p>
      </div>
    </div>

    <div class="sort-container">
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
    
    <div v-if="!isLoading && games.length === 0" class="empty-state">
      <div class="empty-icon">📂</div>
      <p>등록된 게임이 없습니다.<br>상단 버튼을 눌러 스팀 정보를 가져오세요!</p>
    </div>

    <div class="game-grid">
      <div 
        v-for="item in sortedGames" 
        :key="item.game.appid" 
        class="game-card" 
        @click="$router.push(`/game/${item.game.appid}`)"
      >
        <div class="image-wrapper">
          <img :src="item.game.header_image" :alt="item.game.title" loading="lazy" />
        </div>
        <div class="game-info">
          <h3 class="game-title">{{ item.game.title }}</h3>
          <div class="playtime-box">
            <p>총 플레이타임 <span>{{ (item.playtime_total / 60).toFixed(1) }} 시간</span></p>
            <p>최근 플레이타임 <span>{{ (item.playtime_recent_2weeks / 60).toFixed(1) }} 시간</span></p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const authStore = useAuthStore();

const games = ref([]);
const isLoading = ref(false);
const sortBy = ref('total');

const sortOptions = [
  { label: '제목', value: 'title'},
  { label: '총 플레이타임', value: 'total'},
  { label: '최근 플레이타임(2주)', value: 'recent'},
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

const steamSettingsUrl = computed(() => {
  const steamId = authStore.user?.steam_id; 
  return steamId 
    ? `https://steamcommunity.com/profiles/${steamId}/edit/settings`
    : 'https://steamcommunity.com/my/edit/settings'; // 아이디가 없을 때의 기본 경로
});

// DB에 저장된 게임 목록 가져오기
const fetchLibrary = async () => {
  try {
    const response = await axios.get('http://localhost:8000/games/library/', {
      headers: { Authorization: `Token ${authStore.token}` }
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
/* 1. 레이아웃 메인 컨테이너 */
.profile-container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 40px 20px;
  min-height: 100vh;
  background-color: #f8f9fa; /* 아주 밝은 그레이 배경 */
  font-family: 'Pretendard', -apple-system, sans-serif;
  color: #333;
}

/* 2. 로딩 오버레이 */
.loading-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(255, 255, 255, 0.9);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  backdrop-filter: blur(5px);
}

.loading-box {
  text-align: center;
  color: #2c3e50;
}

.spinner {
  width: 45px;
  height: 45px;
  border: 4px solid #e9ecef;
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin { 
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); } 
}

/* 3. 헤더 카드 섹션 */
.profile-header-card {
  background: #ffffff;
  border-radius: 20px;
  padding: 35px;
  margin-bottom: 30px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
  border: 1px solid #eee;
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

.main-title {
  font-size: 1.8rem;
  margin: 0 0 12px 0;
  color: #1a1a1a;
  font-weight: 800;
}

.stats-badge {
  display: inline-block;
  background: #eef2ff;
  color: #4f46e5;
  padding: 6px 14px;
  border-radius: 10px;
  font-size: 0.9rem;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 10px;
}

/* 4. 버튼 스타일 */
.ai-btn {
  background: #6366f1;
  color: white;
  padding: 12px 20px;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 700;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.ai-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(99, 102, 241, 0.4);
}

.sync-btn-modern {
  background-color: #ffffff;
  color: #555;
  padding: 12px 20px;
  font-weight: 600;
  border: 1px solid #ddd;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.sync-btn-modern:hover:not(:disabled) {
  background-color: #f3f4f6;
  border-color: #ccc;
}

.sync-btn-modern:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 5. 헤더 안내 문구 */
.header-footer {
  margin-top: 25px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.privacy-notice {
  font-size: 0.9rem;
  color: #777;
  margin: 0;
}

.info-badge {
  background: #ffedd5;
  color: #f97316;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 800;
  margin-right: 6px;
}

.privacy-link {
  color: #4f46e5;
  text-decoration: underline;
  font-weight: 800;
  transition: color 0.2s;
}

.privacy-link:hover {
  color: #312e81;
}

/* 6. 정렬 필터 (칩 스타일) */
.sort-container {
  margin-bottom: 30px;
  display: flex;
  justify-content: center;
}

.chip-group {
  display: inline-flex;
  background: #eee;
  padding: 4px;
  border-radius: 14px;
}

.chip-btn {
  background: transparent;
  color: #666;
  border: none;
  padding: 8px 18px;
  border-radius: 10px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.chip-btn.active {
  background: #ffffff;
  color: #1a1a1a;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* 7. 게임 리스트 그리드 */
.game-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 25px;
}

.game-card {
  background: #ffffff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0,0,0,0.05);
  transition: all 0.3s ease;
  cursor: pointer;
  border: 1px solid #f0f0f0;
  display: flex;
  flex-direction: column;
}

.game-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 25px rgba(0,0,0,0.1);
}

.image-wrapper {
  width: 100%;
  aspect-ratio: 460 / 215;
  overflow: hidden;
  background: #f1f3f4;
}

.image-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.game-info {
  padding: 16px;
  flex-grow: 1;
}

.game-title {
  font-size: 1.05rem;
  margin: 0 0 12px 0;
  color: #222;
  font-weight: 700;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.playtime-box {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.playtime-box p {
  margin: 0;
  font-size: 0.85rem;
  color: #888;
  display: flex;
  justify-content: space-between;
}

.playtime-box span {
  color: #3498db;
  font-weight: 700;
}

/* 8. 빈 상태 */
.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 80px 0;
  color: #aaa;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 20px;
}
</style>