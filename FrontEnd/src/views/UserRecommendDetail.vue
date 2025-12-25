<template>
  <div class="review-detail-container" v-if="review">
    
    <div class="header-banner" :style="{ backgroundImage: `url(${review.game_image || '/default-game-bg.jpg'})` }">
      <div class="banner-overlay"></div>
      <div class="banner-content">
        <div class="game-meta">
          <span class="category-label">GAME REVIEW</span>
          <h1 class="game-title">{{ review.game_title }}</h1>
        </div>
        
        <div class="author-box">
          <img :src="review.user_avatar || '/default-avatar.png'" alt="Avatar" class="author-avatar">
          <div class="author-info">
            <span class="author-name">{{ review.user_nickname || '익명 사용자' }}</span>
            <span class="post-date">{{ formatDate(review.created_at) }} 작성</span>
          </div>
        </div>
      </div>
    </div>

    <div class="content-layout">
      
      <aside class="side-panel">
        <div class="card metrics-card">
          <h3 class="card-title">상세 평가</h3>
          <div class="metric-list">
            <div v-for="(label, key) in metricsLabels" :key="key" class="metric-item">
              <span class="metric-label">{{ label }}</span>
              <div class="metric-values">
                <div class="stars">
                  <span v-for="n in 5" :key="n" :class="{ filled: n <= review[key] }">★</span>
                </div>
                <span class="score-num">{{ review[key] }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="card playtime-card" v-if="review.playtime_info">
          <h3 class="card-title">플레이 기록</h3>
          <div class="playtime-stats">
            <div class="stat-row">
              <span class="stat-label">총 플레이 시간</span>
              <span class="stat-value highlight">{{ review.playtime_info.total_hours }}시간</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">최근 2주</span>
              <span class="stat-value">{{ review.playtime_info.recent_hours }}시간</span>
            </div>
          </div>
        </div>
      </aside>

      <main class="main-panel">
        <div class="card content-card">
          <div class="quote-icon">“</div>
          <div class="review-body">
            <p>{{ review.content }}</p>
          </div>
        </div>

        <div class="action-footer">
          <button @click="$router.go(-1)" class="btn btn-secondary">목록으로 돌아가기</button>
          <div class="owner-actions" v-if="isMyReview">
            <button @click="deleteReview" class="btn btn-danger">리뷰 삭제</button>
          </div>
        </div>
      </main>
    </div>

  </div>

  <div v-else class="loading-state">
    <div class="spinner"></div>
    <p>리뷰를 불러오는 중입니다...</p>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const review = ref(null)
const reviewId = route.params.reviewId

const metricsLabels = {
  rating_fun: '재미',
  rating_story: '스토리',
  rating_control: '조작감',
  rating_sound: '사운드',
  rating_optimization: '최적화',
}

const isMyReview = computed(() => {
  if (!review.value || !authStore.user) return false;
  return review.value.user === authStore.user.pk || review.value.user === authStore.user.id;
})

const fetchReviewDetail = async () => {
  try {
    const response = await axios.get(`http://127.0.0.1:8000/community/reviews/${reviewId}/`)
    review.value = response.data
  } catch (error) {
    console.error('리뷰 로드 실패:', error)
    alert('존재하지 않는 리뷰입니다.')
    router.push({ name: 'community' })
  }
}

const deleteReview = async () => {
  if(!confirm('작성하신 리뷰를 정말 삭제하시겠습니까?\n삭제 후에는 복구가 불가능합니다.')) return

  try {
    await axios.delete(`http://127.0.0.1:8000/community/reviews/${reviewId}/`, {
      headers: { Authorization: `Bearer ${authStore.token}` },
      withCredentials: true
    })
    alert('리뷰가 정상적으로 삭제되었습니다.')
    router.push({ name: 'community' })
  } catch (error) {
    console.error('삭제 실패:', error)
    alert('삭제에 실패했습니다.')
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return `${date.getFullYear()}년 ${date.getMonth() + 1}월 ${date.getDate()}일`
}

onMounted(() => {
  fetchReviewDetail()
})
</script>

<style scoped>
/* 전체 배경: 라이트 모드 테마 */
.review-detail-container {
  min-height: 100vh;
  background-color: #f8f9fa;
  padding-bottom: 80px;
}

/* 1. 배너 섹션 (이미지 온전히 보여주기) */
.header-banner {
  position: relative;
  height: 380px; /* 배너 높이 확보 */
  background-size: cover;
  background-position: center;
  display: flex;
  align-items: flex-end;
  border-bottom: 1px solid #e2e8f0;
}
.banner-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(to top, rgba(0,0,0,0.8) 0%, rgba(0,0,0,0.2) 100%);
}
.banner-content {
  position: relative;
  max-width: 1100px; margin: 0 auto; width: 100%;
  padding: 0 20px 40px;
  display: flex; justify-content: space-between; align-items: flex-end;
}
.game-title { font-size: 3rem; color: #fff; margin: 5px 0 0; font-weight: 800; text-shadow: 0 2px 10px rgba(0,0,0,0.3); }
.category-label { color: #42b883; font-weight: 800; font-size: 0.9rem; }

.author-box {
  display: flex; align-items: center; gap: 12px;
  background: rgba(255,255,255,0.15); backdrop-filter: blur(10px);
  padding: 12px 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.2);
}
.author-avatar { width: 44px; height: 44px; border-radius: 50%; border: 2px solid #fff; }
.author-name { color: #fff; font-weight: 700; display: block; }
.post-date { color: rgba(255,255,255,0.8); font-size: 0.8rem; }

/* 2. 레이아웃 (마이너스 마진 제거) */
.content-layout {
  max-width: 1100px;
  margin: 40px auto 0; /* 배너 아래로 완전히 내림 */
  padding: 0 20px;
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 30px;
}

/* 카드 스타일 */
.card {
  background: #fff; border-radius: 16px; padding: 25px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06); border: 1px solid #e2e8f0;
}
.card-title { font-size: 1.1rem; font-weight: 700; color: #2d3748; margin-bottom: 20px; border-left: 4px solid #2d3748; padding-left: 12px; }

/* 상세 평가 정렬 수정 */
.metric-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f7fafc;
}
.metric-item:last-child { border-bottom: none; }
.metric-label { font-size: 0.95rem; color: #4a5568; font-weight: 700; }
.metric-values { display: flex; align-items: center; gap: 12px; }
.stars { color: #e2e8f0; font-size: 1.1rem; letter-spacing: -1px; }
.stars .filled { color: #ecc94b; }
.score-num { font-weight: 800; color: #2d3748; width: 15px; text-align: right; }

/* 플레이타임 */
.playtime-stats { display: flex; flex-direction: column; gap: 12px; }
.stat-row { display: flex; justify-content: space-between; }
.stat-label { color: #718096; font-size: 0.9rem; }
.stat-value { font-weight: 700; color: #2d3748; }
.stat-value.highlight { color: #3182ce; }

/* 리뷰 본문 */
.content-card { min-height: 450px; position: relative; }
.quote-icon { font-size: 4rem; color: #f1f5f9; position: absolute; top: 10px; left: 20px; font-family: serif; }
.review-body { position: relative; z-index: 1; color: #4a5568; line-height: 1.9; font-size: 1.1rem; white-space: pre-line; }

/* 버튼 */
.action-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 10px; }
.btn { padding: 12px 24px; border-radius: 12px; font-weight: 700; cursor: pointer; border: none; transition: all 0.2s; }
.btn-secondary { background: #edf2f7; color: #4a5568; }
.btn-danger { background: #fff; color: #e53e3e; border: 1px solid #fed7d7; }

/* 로딩 */
.loading-state { text-align: center; padding: 100px 0; }
.spinner { width: 40px; height: 40px; border: 4px solid #f3f3f3; border-top: 4px solid #2d3748; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 20px; }
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 900px) {
  .content-layout { grid-template-columns: 1fr; }
  .header-banner { height: 300px; }
  .game-title { font-size: 2rem; }
}
</style>