<!-- views/WorldcupView.vue -->
<template>
  <div class="worldcup-container">
    
    <!-- 1. 설정 화면 -->
    <div v-if="gameState === 'setup'" class="setup-screen">
      <h1 class="title">보유 게임 이상형 월드컵</h1>
      
      <!-- [변경] 데이터 로딩 상태 표시 -->
      <p v-if="isLoading" class="subtitle">게임 목록을 불러오는 중입니다...</p>
      <p v-else class="subtitle">총 {{ allGames.length }}개의 게임을 보유 중입니다.</p>
      
      <div class="round-select-container" v-if="!isLoading">
        
        <!-- 게임이 2개 미만일 때 경고 -->
        <div v-if="allGames.length < 2" class="warning-msg">
          게임을 최소 2개 이상 보유해야 월드컵을 진행할 수 있습니다!!
        </div>

        <!-- 버튼 영역 -->
        <div v-else class="buttons-wrapper">
          <div class="round-buttons">
            <!-- 1. 표준 라운드 (16, 32, 64...) -->
            <button 
              v-for="round in availableRounds" 
              :key="round" 
              class="btn btn-outline"
              @click="startGame(round)"
            >
              {{ round }}강
            </button>

            <!-- 2. 전체 게임 -->
            <button 
              class="btn btn-outline"
              @click="startGame('all')"
            >
              전체 ({{ allGames.length }}강)
            </button>
          </div>
        </div>

      </div>
    </div>

    <!-- 2. 게임 진행 화면 (기존 동일) -->
    <div v-else-if="gameState === 'playing'" class="game-screen">
      <div class="header-status">
        <h2>{{ roundLabel }}</h2>
        <p>{{ currentMatchIndex + 1 }} / {{ totalMatchesInRound }} 매치</p>
        
      </div>

      <div class="match-container">
        <!-- 왼쪽 게임 -->
        <div class="game-card left" @click="selectWinner(leftGame)">
          <div class="img-wrapper">
            <img :src="leftGame.image" :alt="leftGame.name" />
          </div>
          <div class="game-info">
            <h3>{{ leftGame.name }}</h3>
            <p>{{ formatPlaytime(leftGame.playtime) }}시간</p>
          </div>
          <div class="overlay"></div>
        </div>

        <div class="vs-badge">VS</div>

        <!-- 오른쪽 게임 -->
        <div class="game-card right" @click="selectWinner(rightGame)">
          <div class="img-wrapper">
            <img :src="rightGame.image" :alt="rightGame.name" />
          </div>
          <div class="game-info">
            <h3>{{ rightGame.name }}</h3>
            <p>{{ formatPlaytime(rightGame.playtime) }}시간</p>
          </div>
          <div class="overlay"></div>
        </div>
      </div>
    </div>

    <!-- 3. 결과 화면 (기존 동일) -->
    <div v-else-if="gameState === 'finished'" class="result-screen">
      <h1>🏆 우승! 🏆</h1>
      
      <div class="winner-card">
        <img :src="winner.image" :alt="winner.name" class="winner-img" @click="$router.push(`/game/${winner.id}`)"/>
        <h2>{{ winner.name }}</h2>
        <p>총 플레이 시간: {{ formatPlaytime(winner.playtime) }}시간</p>
      </div>

      <div class="action-buttons">
        <button class="btn btn-primary" @click="resetGame">다시 하기</button>
        <button class="btn btn-text" @click="$router.push('/')">메인으로</button>
        <button class="btn btn-outline" @click="goToSharePage">결과 공유하기</button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
// [변경] 실제 데이터 연동을 위한 라이브러리 임포트
import axios from 'axios';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const authStore = useAuthStore(); // [변경] Auth Store 사용

// --- 상태 변수들 ---
const gameState = ref('setup'); 
const allGames = ref([]);       
const currentRoundList = ref([]); 
const nextRoundList = ref([]);    
const currentMatchIndex = ref(0); 
const roundCountDisplay = ref(0); 
const isLoading = ref(false);
const isSaving = ref(false);
const saveMessage = ref('');

// [추가] 우승 게임 서버로 전송하는 함수
const saveWinnerToServer = async (winnerGame) => {
  isSaving.value = true;
  saveMessage.value = '내 인생 게임으로 등록 중...';
  
  try {
    await axios.post('http://localhost:8000/games/favorite/', 
      { game_id: winnerGame.id },
      { headers: { Authorization: `Token ${authStore.token}` } }
    );
  } catch (error) {
    console.error(error);
  } finally {
    isSaving.value = false;
  }
};

// [변경] 실제 내 라이브러리 게임 가져오기 (ProfileView 로직 참고)
const fetchMyGames = async () => {
  if (isLoading.value) return;
  isLoading.value = true;

  try {
    // 1. Django 백엔드에서 데이터 요청 (Header에 토큰 포함)
    const response = await axios.get('http://localhost:8000/games/library/', {
      headers: { Authorization: `Token ${authStore.token}` }
    });

    const rawData = response.data;

    // 2. 월드컵을 위해 플레이 시간 순(내림차순) 정렬
    // (보통 좋아하는 게임은 플레이 시간이 긴 경우가 많으므로 상위 라운드 배정을 위해 정렬)
    rawData.sort((a, b) => b.playtime_total - a.playtime_total);

    // 3. API 데이터 구조를 월드컵 컴포넌트 구조로 매핑(변환)
    // ProfileView 구조: item.game.title, item.playtime_total, item.game.header_image
    // WorldcupView 구조: name, playtime, image
    allGames.value = rawData.map(item => ({
      id: item.game.appid,
      name: item.game.title,
      playtime: item.playtime_total, // 분 단위
      image: item.game.header_image
    }));

  } catch (error) {
    console.error("게임 목록 로드 실패:", error);
    alert("게임 정보를 불러오는데 실패했습니다. 로그인이 되어있나요?");
    router.push('/'); // 실패 시 메인으로 이동
  } finally {
    isLoading.value = false;
  }
};

// 공유 페이지로 이동
const goToSharePage = () => {
  router.push({
    name: 'ArticleCreate',
    query: {
      gameId: winner.value.id,
      gameTitle: winner.value.name,
      gameImage: winner.value.image
    }
  });
};

onMounted(() => {
  // [변경] 더미 데이터 대신 실제 데이터 패치 함수 실행
  // 로그인이 안되어있으면 바로 튕겨내는 로직 추가 가능
  if (!authStore.isAuthenticated) {
    alert("로그인이 필요한 서비스입니다.");
    router.push('/');
  } else {
    fetchMyGames();
  }
});

// --- 표시 가능한 라운드 계산 ---
const availableRounds = computed(() => {
  const rounds = [16, 32, 64, 128];
  return rounds.filter(round => allGames.value.length >= round);
});

// --- Computed (기존 유지) ---
const leftGame = computed(() => currentRoundList.value[currentMatchIndex.value * 2]);
const rightGame = computed(() => currentRoundList.value[currentMatchIndex.value * 2 + 1]);
const totalMatchesInRound = computed(() => Math.floor(currentRoundList.value.length / 2));

const roundLabel = computed(() => {
  if (roundCountDisplay.value === 2) return "결승전";
  if (roundCountDisplay.value === 4) return "준결승";
  return `${roundCountDisplay.value}강`;
});

const winner = computed(() => nextRoundList.value[0]);

// --- 로직 함수들 (기존 유지) ---
const shuffle = (array) => {
  return array.sort(() => Math.random() - 0.5);
};

const startGame = (selectedRound) => {
  let targetList = [];
  if (selectedRound === 'all') {
    targetList = [...allGames.value];
  } else {
    // 플레이 시간 상위 N개만 잘라서 가져옴
    targetList = allGames.value.slice(0, selectedRound);
  }

  nextRoundList.value = [];
  currentMatchIndex.value = 0;
  
  // 셔플해서 시작 (플레이 타임 순 정렬된 것을 섞어서 대진표 작성)
  setupRound(shuffle(targetList));
  gameState.value = 'playing';
};

const setupRound = (list) => {
  roundCountDisplay.value = list.length; 

  // 부전승 로직
  if (list.length % 2 !== 0 && list.length > 1) {
    const luckyGame = list.pop(); 
    nextRoundList.value.push(luckyGame); 
  }

  currentRoundList.value = list;
};

const selectWinner = (selectedGame) => {
  nextRoundList.value.push(selectedGame);

  if (currentMatchIndex.value + 1 < totalMatchesInRound.value) {
    currentMatchIndex.value++;
  } else {
    proceedToNextRound();
  }
};

const proceedToNextRound = () => {
  if (nextRoundList.value.length === 1) {
    gameState.value = 'finished';
    saveWinnerToServer(nextRoundList.value[0]);
    return;
  }
  const nextList = [...nextRoundList.value];
  nextRoundList.value = [];
  currentMatchIndex.value = 0;
  setupRound(shuffle(nextList));
};

const resetGame = () => {
  gameState.value = 'setup';
  currentRoundList.value = [];
  nextRoundList.value = [];
};

const formatPlaytime = (minutes) => (minutes / 60).toFixed(1);
</script>

<style scoped>
/* 기존 스타일과 완전히 동일합니다 */
.worldcup-container {
  width: 100%;
  max-width: 1000px;
  margin: 0 auto;
  text-align: center;
  padding-bottom: 40px;
}

.setup-screen { padding-top: 60px; }
.title { font-size: 2.5rem; margin-bottom: 10px; color: #333; }
.subtitle { color: #666; margin-bottom: 40px; }

.round-select-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.buttons-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
  width: 100%;
}

.round-buttons {
  display: flex;
  justify-content: center;
  gap: 15px;
  flex-wrap: wrap; 
  max-width: 800px; 
}

.btn-outline {
  padding: 15px 30px;
  font-size: 1.2rem;
  border: 2px solid #42b883;
  background: white;
  color: #42b883;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 100px; 
}

.btn-outline:hover {
  background: #42b883;
  color: white;
}

.warning-msg {
  color: #ff4757;
  font-weight: bold;
  background: #fff5f5;
  padding: 15px;
  border-radius: 8px;
}

@keyframes popIn {
  from { transform: scale(0.8); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

.header-status h2 { font-size: 2rem; margin-bottom: 5px; color: #42b883; }
.header-status p { color: #888; margin-bottom: 10px; }
.match-container {
  display: flex; justify-content: space-between; align-items: center; position: relative; height: 500px;
}
.game-card {
  flex: 1; height: 100%; border-radius: 12px; overflow: hidden; position: relative; cursor: pointer;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1); transition: transform 0.3s, box-shadow 0.3s;
  display: flex; flex-direction: column;
}
.game-card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(66, 184, 131, 0.3); border: 2px solid #42b883; }
.img-wrapper { flex: 1; background: #000; display: flex; align-items: center; justify-content: center; overflow: hidden; }
.img-wrapper img { width: 100%; height: 100%; object-fit: cover; }
.game-info {
  height: 80px; background: #fff; display: flex; flex-direction: column; justify-content: center; align-items: center; border-top: 1px solid #eee;
}
.game-info h3 { margin: 0; font-size: 1.1rem; color: #333; }
.game-info p { margin: 5px 0 0; font-size: 0.9rem; color: #777; }
.overlay {
  position: absolute; top: 0; left: 0; width: 100%; height: 100%;
  /* background: rgba(66, 184, 131, 0.2); */
  display: flex; align-items: center; justify-content: center;
  color: white; font-size: 2rem; font-weight: bold; opacity: 0; transition: opacity 0.2s;
  text-shadow: 0 2px 4px rgba(0,0,0,0.5);
}
.game-card:hover .overlay { opacity: 1; }
.vs-badge {
  position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%);
  background: #ff4757; color: white; font-weight: 900; font-size: 1.5rem;
  width: 60px; height: 60px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center; z-index: 10;
  box-shadow: 0 4px 10px rgba(0,0,0,0.2); border: 4px solid white;
}
.result-screen { padding-top: 40px; animation: fadeIn 0.5s; }
.winner-card {
  background: white; padding: 20px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.15);
  display: inline-block; margin-bottom: 30px;
}
.winner-img { width: 400px; height: 300px; object-fit: cover; border-radius: 8px; margin-bottom: 15px; }
.action-buttons { display: flex; justify-content: center; gap: 15px; }
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
@media (max-width: 768px) {
  .match-container { flex-direction: column; height: auto; gap: 20px; }
  .game-card { width: 100%; height: 300px; }
  .vs-badge { position: relative; top: 0; left: 0; transform: none; margin: -10px auto; }
}
</style>