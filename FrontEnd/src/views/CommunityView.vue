<!-- views/CommunityView.vue -->
<template>
  <div class="community-container">
    
    <!-- 1. 헤더 섹션 -->
    <div class="header-section">
      <div class="header-texts">
        <h1>GAMERS HUB</h1>
        <p>유저들의 솔직한 평가와 인생 게임을 만나보세요.</p>
      </div>
      <div class="header-actions">
         <button class="action-btn article-btn" @click="$router.push({ name: 'Worldcup' })">
            🏆 인생게임 찾기
         </button>
         <!-- 리뷰 작성은 게임 상세 페이지에서 진입하므로 여기서는 검색 등으로 유도하거나 생략 가능 -->
      </div>
    </div>

    <div v-if="loading" class="loading-area">
      <div class="spinner"></div>
      <p>데이터를 분석 중입니다...</p>
    </div>

    <div v-else>
      <!-- 2. 명예의 전당 (분야별 1위) -->
      <section v-if="hasReviews" class="hall-of-fame">
        <h2 class="section-title">👑 분야별 최고의 게임</h2>
        <div class="fame-grid">
          <div 
            v-for="(game, category) in topGames" 
            :key="category" 
            class="fame-card"
            @click="goToGameDetail(game.gameId)"
            v-if="game"
          >
            <div class="fame-bg" :style="{ backgroundImage: `url(${game.image})` }"></div>
            <div class="fame-overlay"></div>
            <div class="fame-content">
              <span class="category-badge" :class="category">{{ categoryLabels[category] }} 1위</span>
              <h3 class="fame-title">{{ game.title }}</h3>
              <div class="fame-score">
                <span class="score-num">{{ game.score.toFixed(1) }}</span>
                <span class="score-max">/ 5.0</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 3. 하이브리드 피드 (게시글 + 리뷰) -->
      <section class="feed-section">
        <div class="feed-header">
          <h2 class="section-title">🔥 실시간 피드</h2>
          <div class="sort-options">
            <!-- 추후 필터 기능 추가 가능 -->
            <span>전체보기</span>
          </div>
        </div>

        <div v-if="mixedFeed.length === 0" class="no-data">
          아직 등록된 글이 없습니다. 첫 번째 주인공이 되어보세요!
        </div>

        <div class="feed-list">
          <div 
            v-for="item in mixedFeed" 
            :key="`${item.type}-${item.id}`"
            class="feed-card"
            :class="item.type"
            @click="goToDetail(item)"
          >
            <!-- 썸네일 (공통) -->
            <div class="card-thumb">
              <img :src="item.image || '/default-game.png'" alt="game cover" loading="lazy" />
              <div class="type-icon">
                {{ item.type === 'article' ? '🏆' : '⭐' }}
              </div>
            </div>

            <!-- 카드 내용 -->
            <div class="card-body">
              <div class="card-meta-top">
                <span class="game-name">{{ item.gameTitle }}</span>
                <span class="date">{{ formatDate(item.createdAt) }}</span>
              </div>

              <!-- Article(월드컵) 스타일 -->
              <div v-if="item.type === 'article'" class="content-wrapper">
                <h3 class="item-title">{{ item.title }}</h3>
                <p class="preview">{{ truncateText(item.content, 80) }}</p>
                <div class="badge-area">
                  <span class="badge-worldcup">USER'S BEST PICK</span>
                </div>
              </div>

              <!-- Review(평가) 스타일 -->
              <div v-else class="content-wrapper">
                <div class="review-score-row">
                  <div class="stars">
                    <span v-for="n in 5" :key="n" :class="{ filled: n <= Math.round(item.averageScore) }">★</span>
                  </div>
                  <span class="score-text">{{ item.averageScore.toFixed(1) }}</span>
                </div>
                <p class="preview review-text">"{{ truncateText(item.content, 60) }}"</p>
                <div class="stat-tags">
                   <!-- 점수가 높은 상위 2개 항목만 태그로 표시 -->
                   <span v-for="tag in getTopTags(item)" :key="tag" class="stat-tag">
                     #{{ tag }}
                   </span>
                </div>
              </div>

              <div class="user-info">
                <img :src="item.userAvatar || '/default-avatar.png'" class="avatar" />
                <span class="nickname">{{ item.userNickname }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const router = useRouter();
const loading = ref(true);
const mixedFeed = ref([]);
const topGames = ref({
  fun: null, story: null, control: null, sound: null, optimization: null
});

const categoryLabels = {
  fun: '재미', story: '스토리', control: '조작감', sound: '사운드', optimization: '최적화'
};

const hasReviews = computed(() => Object.values(topGames.value).some(v => v !== null));

// API 호출 및 데이터 가공
const fetchData = async () => {
  try {
    // 1. 병렬 요청 (Articles + Reviews)
    const [articlesRes, reviewsRes] = await Promise.all([
      axios.get('http://localhost:8000/community/articles/'),
      axios.get('http://localhost:8000/community/reviews/')
    ]);

    const articlesData = articlesRes.data.results || articlesRes.data;
    const reviewsData = reviewsRes.data.results || reviewsRes.data;

    // 2. 명예의 전당 계산 (리뷰 데이터 기반)
    calculateHallOfFame(reviewsData);

    // 3. 피드 합치기 (데이터 구조 통일)
    const formattedArticles = articlesData.map(a => ({
      type: 'article',
      id: a.id,
      title: a.title,
      content: a.content,
      gameId: a.game_id, 
      gameTitle: a.game_title,
      image: a.game_image,
      userNickname: a.user_nickname,
      userAvatar: a.user_avatar,
      createdAt: a.created_at
    }));

    const formattedReviews = reviewsData.map(r => {
      // 5개 지표 평균 계산 (화면 표시용)
      const avg = (r.rating_fun + r.rating_story + r.rating_control + r.rating_sound + r.rating_optimization) / 5;
      
      return {
        type: 'review',
        id: r.id,
        content: r.content,
        gameId: r.game_id,
        gameTitle: r.game_title,
        image: r.game_image,
        userNickname: r.user_nickname,
        userAvatar: r.user_avatar,
        createdAt: r.created_at,
        averageScore: avg,
        // 태그 추출용 원본 점수
        ratings: {
          '재미': r.rating_fun,
          '스토리': r.rating_story,
          '조작감': r.rating_control,
          '사운드': r.rating_sound,
          '최적화': r.rating_optimization
        }
      };
    });

    // 4. 합치고 최신순 정렬
    mixedFeed.value = [...formattedArticles, ...formattedReviews].sort((a, b) => {
      return new Date(b.createdAt) - new Date(a.createdAt);
    });

  } catch (error) {
    console.error('데이터 로드 실패:', error);
  } finally {
    loading.value = false;
  }
};

// 명예의 전당 계산 로직 (게임별 평균 점수 산출 -> 최고점 선정)
const calculateHallOfFame = (reviews) => {
  const gameStats = {}; // { gameId: { sumFun: 0, count: 0, title: '', image: '' ... } }

  // 1. 게임별 점수 합산
  reviews.forEach(r => {
    if (!gameStats[r.game_id]) {
      gameStats[r.game_id] = {
        title: r.game_title,
        image: r.game_image,
        count: 0,
        fun: 0, story: 0, control: 0, sound: 0, optimization: 0
      };
    }
    const target = gameStats[r.game_id];
    target.count++;
    target.fun += r.rating_fun;
    target.story += r.rating_story;
    target.control += r.rating_control;
    target.sound += r.rating_sound;
    target.optimization += r.rating_optimization;
  });

  // 2. 분야별 최고 게임 선정
  const bests = { fun: null, story: null, control: null, sound: null, optimization: null };
  const maxScores = { fun: 0, story: 0, control: 0, sound: 0, optimization: 0 };

  Object.entries(gameStats).forEach(([gId, stat]) => {
    // 각 분야 평균 계산
    const avgs = {
      fun: stat.fun / stat.count,
      story: stat.story / stat.count,
      control: stat.control / stat.count,
      sound: stat.sound / stat.count,
      optimization: stat.optimization / stat.count,
    };

    // 최고점 갱신 확인
    for (const key in bests) {
      if (avgs[key] > maxScores[key]) {
        maxScores[key] = avgs[key];
        bests[key] = {
          gameId: gId,
          title: stat.title,
          image: stat.image,
          score: avgs[key]
        };
      }
    }
  });

  topGames.value = bests;
};

// 리뷰 카드에서 점수가 높은 항목 2개 태그로 뽑기
const getTopTags = (reviewItem) => {
  const entries = Object.entries(reviewItem.ratings);
  // 점수 내림차순 정렬
  entries.sort((a, b) => b[1] - a[1]);
  // 상위 2개 키만 반환 (점수가 3점 이상인 것만)
  return entries.slice(0, 2).filter(e => e[1] >= 3).map(e => e[0]);
};

// 이동 함수
const goToDetail = (item) => {
  if (item.type === 'article') {
    router.push({ name: 'ArticleDetail', params: { id: item.id } });
  } else {
    router.push({ name: 'UserRecommendDetail', params: { reviewId: item.id } });
  }
};

const goToGameDetail = (gameId) => {
  router.push({ name: 'GameDetail', params: { id: gameId } });
};

// 유틸리티
const formatDate = (dateString) => {
  const date = new Date(dateString);
  const now = new Date();
  const diff = (now - date) / 1000; // 초 단위

  if (diff < 60) return '방금 전';
  if (diff < 3600) return `${Math.floor(diff / 60)}분 전`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}시간 전`;
  return date.toLocaleDateString();
};

const truncateText = (text, len) => {
  if (!text) return '';
  return text.length > len ? text.substring(0, len) + '...' : text;
};

onMounted(fetchData);
</script>

<style scoped>
/* 전체 레이아웃 */
.community-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
  color: #c7d5e0;
  min-height: 100vh;
}

/* 1. 헤더 */
.header-section {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 40px;
  border-bottom: 2px solid #2a475e;
  padding-bottom: 20px;
}
.header-texts h1 {
  font-size: 2.5rem;
  color: white;
  margin: 0 0 10px 0;
  letter-spacing: 1px;
}
.header-texts p {
  color: #8f98a0;
  margin: 0;
}
.action-btn {
  padding: 10px 20px;
  border-radius: 4px;
  border: none;
  font-weight: bold;
  cursor: pointer;
  transition: transform 0.2s;
}
.article-btn {
  background: #42b883; /* Vue Green */
  color: white;
}
.article-btn:hover { transform: translateY(-2px); background: #3aa876; }

/* 2. 명예의 전당 */
.hall-of-fame {
  margin-bottom: 60px;
}
.section-title {
  font-size: 1.5rem;
  color: white;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}
.fame-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}
.fame-card {
  position: relative;
  height: 250px;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
  box-shadow: 0 4px 10px rgba(0,0,0,0.3);
}
.fame-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0,0,0,0.5);
}
.fame-bg {
  width: 100%; height: 100%;
  background-size: cover; background-position: center;
  transition: transform 0.3s;
}
.fame-card:hover .fame-bg { transform: scale(1.05); }
.fame-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(to top, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.2) 60%, transparent 100%);
}
.fame-content {
  position: absolute; bottom: 0; left: 0; right: 0;
  padding: 20px;
}
.category-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: bold;
  margin-bottom: 8px;
  color: #1b2838;
}
/* 카테고리별 색상 */
.category-badge.fun { background: #ffc107; }
.category-badge.story { background: #9b59b6; color: white; }
.category-badge.control { background: #e74c3c; color: white; }
.category-badge.sound { background: #3498db; color: white; }
.category-badge.optimization { background: #2ecc71; }

.fame-title {
  color: white; margin: 0 0 5px 0; font-size: 1.1rem;
  text-shadow: 1px 1px 2px black;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.fame-score { color: #ffc107; font-weight: bold; }
.score-num { font-size: 1.2rem; }
.score-max { font-size: 0.8rem; color: #8f98a0; }

/* 3. 하이브리드 피드 */
.feed-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 20px;
}
.feed-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.feed-card {
  background: #16202d;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  height: 160px;
  cursor: pointer;
  transition: border 0.2s, background 0.2s;
  border: 1px solid #2a475e;
}
.feed-card:hover {
  background: #1b2838;
  border-color: #66c0f4;
}

/* 카드 타입별 테두리 포인트 */
.feed-card.article:hover { border-left: 4px solid #42b883; }
.feed-card.review:hover { border-left: 4px solid #ffc107; }

/* 썸네일 영역 */
.card-thumb {
  width: 120px;
  position: relative;
  flex-shrink: 0;
}
.card-thumb img { width: 100%; height: 100%; object-fit: cover; }
.type-icon {
  position: absolute; top: 8px; left: 8px;
  width: 28px; height: 28px;
  background: rgba(0,0,0,0.6);
  backdrop-filter: blur(2px);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.2rem;
}

/* 내용 영역 */
.card-body {
  flex-grow: 1; padding: 15px;
  display: flex; flex-direction: column;
  justify-content: space-between;
  min-width: 0;
}

.card-meta-top {
  display: flex; justify-content: space-between;
  font-size: 0.85rem; margin-bottom: 8px;
}
.game-name { color: #66c0f4; font-weight: bold; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 70%; }
.date { color: #647580; }

.item-title {
  margin: 0 0 5px 0; font-size: 1.1rem; color: white;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.preview {
  font-size: 0.9rem; color: #8f98a0; margin: 0; line-height: 1.4;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}

/* Article 전용 */
.badge-worldcup {
  display: inline-block; background: rgba(66, 184, 131, 0.15); color: #42b883;
  font-size: 0.75rem; padding: 2px 6px; border-radius: 4px; margin-top: 8px; border: 1px solid rgba(66, 184, 131, 0.3);
}

/* Review 전용 */
.review-score-row { display: flex; align-items: center; gap: 8px; margin-bottom: 5px; }
.stars .filled { color: #ffc107; }
.stars { color: #444; font-size: 1rem; }
.score-text { color: #ffc107; font-weight: bold; }
.review-text { font-style: italic; color: #a0a0a0; }
.stat-tags { margin-top: 6px; display: flex; gap: 5px; }
.stat-tag { font-size: 0.75rem; color: #66c0f4; background: rgba(102, 192, 244, 0.1); padding: 2px 6px; border-radius: 3px; }

/* 유저 정보 */
.user-info {
  display: flex; align-items: center; gap: 8px; margin-top: auto; padding-top: 10px;
}
.avatar { width: 20px; height: 20px; border-radius: 50%; }
.nickname { font-size: 0.85rem; color: #8f98a0; }

/* 로딩 & 반응형 */
.loading-area { text-align: center; padding: 100px 0; color: #66c0f4; }
.spinner {
  width: 40px; height: 40px; border: 4px solid rgba(102, 192, 244, 0.2);
  border-top-color: #66c0f4; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 15px;
}
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 768px) {
  .feed-list { grid-template-columns: 1fr; }
  .header-section { flex-direction: column; align-items: flex-start; gap: 15px; }
}
</style>