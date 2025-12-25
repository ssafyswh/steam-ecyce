<template>
  <div class="community-container">
    
    <div class="header-section">
      <div class="header-texts">
        <h1 class="main-title">Gamers Hub</h1>
        <p class="main-subtitle">유저들이 직접 뽑은 최고의 게임과 솔직한 리뷰를 확인하세요.</p>
      </div>
      <div class="header-actions">
         <button class="action-btn worldcup-btn" @click="$router.push({ name: 'Worldcup' })">
           🏆 내 인생 게임 찾기
         </button>
      </div>
    </div>

    <div v-if="loading" class="loading-area">
      <div class="spinner"></div>
      <p>커뮤니티 데이터를 불러오는 중...</p>
    </div>

    <div v-else>
      <section v-if="hasReviews" class="hall-of-fame">
        <h2 class="sub-section-title">👑 CATEGORY BEST GAMES</h2>
        <div class="fame-grid">
          <div 
            v-for="(game, category) in filteredTopGames" 
            :key="category" 
            class="fame-card-vertical"
            :class="category"
            @click="goToGameDetail(game.gameId)"
          >
            <div class="glow-effect"></div>
            
            <div class="poster-container">
              <img :src="game.image || '/default-game.png'" class="poster-img" alt="game cover" />
              <div class="rank-tag">Top 1</div>
              <div class="category-badge-floating">{{ categoryLabels[category] }}</div>
              
              <div class="poster-info-overlay">
                <h3 class="fame-game-title">{{ game.title }}</h3>
                <div class="fame-score-box">
                  <span class="score-star">★</span>
                  <span class="score-val">{{ game.score.toFixed(1) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="feed-section">
        <div class="feed-filter-bar">
          <div class="tabs">
            <button 
              v-for="tab in ['all', 'article', 'review']" 
              :key="tab"
              :class="['tab-btn', { active: currentTab === tab }]"
              @click="currentTab = tab"
            >
              {{ tab === 'all' ? '전체 피드' : tab === 'article' ? '인생 게임 🏆' : '솔직 리뷰 ⭐' }}
            </button>
          </div>
        </div>

        <div v-if="filteredFeed.length === 0" class="no-data-card">
          <p>등록된 게시글이 없습니다.</p>
        </div>

        <div class="feed-grid">
          <div 
            v-for="item in filteredFeed" 
            :key="`${item.type}-${item.id}`"
            class="content-card"
            @click="goToDetail(item)"
          >
            <div class="content-img">
              <img :src="item.image || '/default-game.png'" alt="game thumbnail" />
              <div class="type-badge" :class="item.type">
                {{ item.type === 'article' ? 'BEST PICK' : 'REVIEW' }}
              </div>
            </div>

            <div class="content-info">
              <div class="meta-info">
                <span class="game-tag">{{ item.gameTitle }}</span>
                <span class="time-tag">{{ formatDate(item.createdAt) }}</span>
              </div>

              <h3 class="content-title">
                {{ item.type === 'article' ? item.title : `${item.gameTitle} 후기` }}
              </h3>
              
              <p class="content-preview">
                {{ truncateText(item.content, 75) }}
              </p>

              <div v-if="item.type === 'review'" class="review-stats">
                <div class="stars-row">
                   <span v-for="n in 5" :key="n" :class="{ filled: n <= Math.round(item.averageScore) }">★</span>
                   <span class="avg-num">{{ item.averageScore.toFixed(1) }}</span>
                </div>
              </div>

              <div class="user-profile">
                <img :src="item.userAvatar || '/default-avatar.png'" alt="avatar" />
                <span class="user-name">{{ item.userNickname }}</span>
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
const currentTab = ref('all');
const mixedFeed = ref([]);
const topGames = ref({
  fun: null, story: null, control: null, sound: null, optimization: null
});

const categoryLabels = {
  fun: '재미', story: '스토리', control: '조작감', sound: '사운드', optimization: '최적화'
};

const hasReviews = computed(() => Object.values(topGames.value).some(v => v !== null));

const filteredTopGames = computed(() => {
  const result = {};
  for (const key in topGames.value) {
    if (topGames.value[key]) result[key] = topGames.value[key];
  }
  return result;
});

const filteredFeed = computed(() => {
  if (currentTab.value === 'all') return mixedFeed.value;
  return mixedFeed.value.filter(item => item.type === currentTab.value);
});

const fetchData = async () => {
  try {
    const [articlesRes, reviewsRes] = await Promise.all([
      axios.get('http://localhost:8000/community/articles/'),
      axios.get('http://localhost:8000/community/reviews/')
    ]);

    const articlesData = articlesRes.data.results || articlesRes.data;
    const reviewsData = reviewsRes.data.results || reviewsRes.data;

    calculateHallOfFame(reviewsData);

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
      const avg = (r.rating_fun + r.rating_story + r.rating_control + r.rating_sound + r.rating_optimization) / 5;
      return {
        type: 'review',
        id: r.id,
        content: r.content,
        gameId: r.game_id,
        gameTitle: r.game_title,
        // [해결] r.game_image가 백엔드에서 내려오면 정상 출력됩니다.
        image: r.game_image, 
        userNickname: r.user_nickname,
        userAvatar: r.user_avatar,
        createdAt: r.created_at,
        averageScore: avg
      };
    });

    mixedFeed.value = [...formattedArticles, ...formattedReviews].sort((a, b) => {
      return new Date(b.createdAt) - new Date(a.createdAt);
    });

  } catch (error) {
    console.error('데이터 로드 실패:', error);
  } finally {
    loading.value = false;
  }
};

const calculateHallOfFame = (reviews) => {
  if (!reviews || reviews.length === 0) return;
  const gameStats = {};

  reviews.forEach(r => {
    if (!gameStats[r.game_appid]) {
      gameStats[r.game_appid] = {
        title: r.game_title,
        image: r.game_image,
        count: 0,
        fun: 0, story: 0, control: 0, sound: 0, optimization: 0
      };
    }
    const target = gameStats[r.game_appid];
    target.count++;
    target.fun += r.rating_fun;
    target.story += r.rating_story;
    target.control += r.rating_control;
    target.sound += r.rating_sound;
    target.optimization += r.rating_optimization;
  });

  const bests = { fun: null, story: null, control: null, sound: null, optimization: null };
  const maxScores = { fun: 0, story: 0, control: 0, sound: 0, optimization: 0 };

  Object.entries(gameStats).forEach(([gId, stat]) => {
    const categories = ['fun', 'story', 'control', 'sound', 'optimization'];
    categories.forEach(cat => {
      const avg = stat[cat] / stat.count;
      if (avg > maxScores[cat]) {
        maxScores[cat] = avg;
        bests[cat] = { gameId: gId, title: stat.title, image: stat.image, score: avg };
      }
    });
  });
  topGames.value = bests;
};

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

const formatDate = (dateString) => {
  const date = new Date(dateString);
  const now = new Date();
  const diff = (now - date) / 1000;
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
.community-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 60px 20px;
  background-color: #ffffff;
}

/* 1. 헤더 */
.header-section { display: flex; justify-content: space-between; align-items: center; margin-bottom: 60px; }
.main-title { font-size: 2.8rem; font-weight: 900; color: #1a202c; letter-spacing: -1px; }
.main-subtitle { color: #718096; font-size: 1.1rem; }
.action-btn { padding: 14px 24px; border-radius: 12px; border: none; font-weight: 700; cursor: pointer; transition: all 0.2s; }
.worldcup-btn { background: #2d3748; color: #fff; }
.worldcup-btn:hover { background: #1a202c; transform: translateY(-2px); }

/* 2. 명예의 전당 (세로형 + 글로우) */
.hall-of-fame { margin-bottom: 80px; }
.sub-section-title { font-size: 1.2rem; font-weight: 800; color: #2d3748; margin-bottom: 30px; letter-spacing: 2px; text-align: center; }

.fame-grid { 
  display: grid; 
  grid-template-columns: repeat(5, 1fr); 
  gap: 25px; 
}

.fame-card-vertical {
  position: relative;
  aspect-ratio: 2 / 3; /* 세로 포스터 비율 */
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

/* 카테고리별 글로우 컬러 변수 */
.fame-card-vertical.fun { --glow-color: #ffc107; }
.fame-card-vertical.story { --glow-color: #a855f7; }
.fame-card-vertical.control { --glow-color: #ef4444; }
.fame-card-vertical.sound { --glow-color: #3b82f6; }
.fame-card-vertical.optimization { --glow-color: #10b981; }

.glow-effect {
  position: absolute; inset: 0;
  border-radius: 16px;
  background: var(--glow-color);
  opacity: 0;
  filter: blur(20px);
  transition: opacity 0.4s;
  z-index: 0;
}

.poster-container {
  position: relative;
  width: 100%; height: 100%;
  border-radius: 16px;
  overflow: hidden;
  z-index: 1;
  background: #000;
  box-shadow: 0 10px 20px rgba(0,0,0,0.1);
}

.poster-img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.6s; }

.rank-tag {
  position: absolute; top: 12px; left: 12px;
  background: var(--glow-color); color: #fff;
  padding: 4px 10px; border-radius: 6px; font-size: 0.7rem; font-weight: 900;
}

.category-badge-floating {
  position: absolute; top: 12px; right: 12px;
  background: rgba(0,0,0,0.5); backdrop-filter: blur(4px);
  color: #fff; padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 600;
}

.poster-info-overlay {
  position: absolute; bottom: 0; left: 0; right: 0;
  padding: 40px 15px 15px;
  background: linear-gradient(to top, rgba(0,0,0,0.95), transparent);
  color: #fff;
}

.fame-game-title { font-size: 1rem; font-weight: 800; margin-bottom: 5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.fame-score-box { display: flex; align-items: center; gap: 4px; color: var(--glow-color); font-weight: 800; }

/* 호버 애니메이션 */
.fame-card-vertical:hover { transform: translateY(-15px) scale(1.05); }
.fame-card-vertical:hover .glow-effect { opacity: 0.6; }
.fame-card-vertical:hover .poster-img { transform: scale(1.15); }

/* 3. 피드 섹션 */
.feed-filter-bar { border-bottom: 2px solid #edf2f7; margin-bottom: 40px; }
.tabs { display: flex; gap: 35px; }
.tab-btn { padding: 15px 0; background: none; border: none; font-weight: 600; color: #718096; cursor: pointer; position: relative; font-size: 1rem; }
.tab-btn.active { color: #1a202c; }
.tab-btn.active::after { content: ''; position: absolute; bottom: -2px; left: 0; right: 0; height: 2px; background: #1a202c; }

.feed-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 30px; }
.content-card {
  background: #fff; border-radius: 20px; overflow: hidden;
  border: 1px solid #edf2f7; box-shadow: 0 4px 15px rgba(0,0,0,0.03);
  cursor: pointer; transition: all 0.25s;
}
.content-card:hover { transform: translateY(-5px); box-shadow: 0 15px 35px rgba(0,0,0,0.08); }

.content-img { position: relative; height: 190px; background-color: #f7fafc; }
.content-img img { width: 100%; height: 100%; object-fit: cover; }
.type-badge { position: absolute; top: 15px; right: 15px; padding: 6px 12px; border-radius: 8px; font-size: 0.7rem; font-weight: 800; }
.type-badge.article { background: #2d3748; color: #fff; }
.type-badge.review { background: #fff; color: #2d3748; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }

.content-info { padding: 25px; }
.meta-info { display: flex; justify-content: space-between; margin-bottom: 15px; font-size: 0.8rem; font-weight: 600; }
.game-tag { color: #3182ce; }
.time-tag { color: #a0aec0; }
.content-title { font-size: 1.3rem; font-weight: 800; color: #1a202c; margin-bottom: 12px; line-height: 1.3; }
.content-preview { font-size: 0.95rem; color: #4a5568; line-height: 1.6; margin-bottom: 20px; }

.review-stats { margin-bottom: 15px; }
.stars-row { color: #e2e8f0; font-size: 1.1rem; display: flex; align-items: center; gap: 3px; }
.stars-row .filled { color: #ecc94b; }
.avg-num { color: #2d3748; font-weight: 800; margin-left: 8px; }

.user-profile { display: flex; align-items: center; gap: 10px; border-top: 1px solid #f7fafc; padding-top: 20px; }
.user-profile img { width: 30px; height: 30px; border-radius: 50%; }
.user-name { font-size: 0.9rem; font-weight: 600; color: #4a5568; }

/* 로딩 애니메이션 */
.spinner { width: 50px; height: 50px; border: 5px solid #f3f3f3; border-top: 5px solid #2d3748; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 20px; }
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 1024px) { .fame-grid { grid-template-columns: repeat(3, 1fr); } }
@media (max-width: 640px) { .fame-grid { grid-template-columns: repeat(2, 1fr); } .main-title { font-size: 2rem; } }
</style>