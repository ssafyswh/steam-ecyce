<template>
  <div class="review-detail-container" v-if="review">
    
    <!-- 상단 게임 배너 (배경) -->
    <div class="header-banner" :style="{ backgroundImage: `url(${review.game_image})` }">
      <div class="overlay"></div>
      <div class="header-content">
        <h1 class="game-title">{{ review.game_title }}</h1>
        <div class="user-info">
          <img :src="review.user_avatar || '/default-avatar.png'" alt="User Avatar" class="avatar">
          <div class="user-text">
            <span class="nickname">{{ review.user_nickname || 'Unknown User' }}</span>
            <span class="created-at">{{ new Date(review.created_at).toLocaleDateString() }} 작성됨</span>
          </div>
        </div>
      </div>
    </div>

    <div class="content-body">
      <!-- 왼쪽: 5각형 지표 (별점 리스트로 표현) -->
      <div class="metrics-panel">
        <h3 class="panel-title">평가 상세</h3>
        <div class="metric-list">
          <div v-for="(label, key) in metricsLabels" :key="key" class="metric-item">
            <span class="label">{{ label }}</span>
            <div class="stars">
              <span v-for="n in 5" :key="n" :class="{ filled: n <= review[key] }">★</span>
            </div>
            <span class="score">{{ review[key] }}</span>
          </div>
        </div>

        <!-- [요청사항] 플레이타임 정보 표시 -->
        <div class="playtime-box" v-if="review.playtime_info">
          <h4 class="playtime-title">플레이 기록</h4>
          <div class="time-row">
            <span class="time-label">총 플레이:</span>
            <span class="time-value highlight">{{ review.playtime_info.total_hours }} 시간</span>
          </div>
          <div class="time-row">
            <span class="time-label">최근 2주:</span>
            <span class="time-value">{{ review.playtime_info.recent_hours }} 시간</span>
          </div>
        </div>
      </div>

      <!-- 오른쪽: 리뷰 내용 -->
      <div class="review-text-panel">
        <h3 class="panel-title">리뷰 내용</h3>
        <div class="review-content">
          <p>{{ review.content }}</p>
        </div>
        
        <div class="actions">
          <button @click="$router.go(-1)" class="btn-back">목록으로</button>
          
          <!-- 본인 글일 경우 수정/삭제 버튼 (user 비교 로직 필요) -->
          <button v-if="isMyReview" @click="deleteReview" class="btn-delete">삭제하기</button>
        </div>
      </div>
    </div>

  </div>
  <div v-else class="loading">
    로딩 중...
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth' // Pinia store 사용 가정

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const review = ref(null)
const reviewId = route.params.reviewId // 라우터에서 받아올 리뷰 ID

const metricsLabels = {
  rating_fun: '재미',
  rating_story: '스토리',
  rating_control: '조작감',
  rating_sound: '사운드',
  rating_optimization: '최적화',
}

// 현재 로그인한 유저가 작성자인지 확인
const isMyReview = computed(() => {
  if (!review.value || !authStore.user) return false;
  // user ID 혹은 nickname으로 비교 (API 응답구조에 따라 조정)
  return review.value.user === authStore.user.pk; 
})

const fetchReviewDetail = async () => {
  try {
    // Django ViewSet의 Detail URL (예: /community/reviews/1/)
    const response = await axios.get(`http://127.0.0.1:8000/community/reviews/${reviewId}/`)
    review.value = response.data
  } catch (error) {
    console.error('리뷰 불러오기 실패:', error)
    alert('존재하지 않거나 삭제된 리뷰입니다.')
    router.push({ name: 'main' })
  }
}

const deleteReview = async () => {
  if(!confirm('정말 이 리뷰를 삭제하시겠습니까?')) return

  try {
    await axios.delete(`http://127.0.0.1:8000/community/reviews/${reviewId}/`, {
      headers: { Authorization: `Token ${authStore.token}` }
    })
    alert('삭제되었습니다.')
    router.go(-1)
  } catch (error) {
    alert('삭제에 실패했습니다.')
  }
}

onMounted(() => {
  fetchReviewDetail()
})
</script>

<style scoped>
.review-detail-container {
  color: #c7d5e0;
  background-color: #1b2838;
  min-height: 100vh;
  padding-bottom: 50px;
}

/* Header Banner */
.header-banner {
  position: relative;
  height: 250px;
  background-size: cover;
  background-position: center;
  display: flex;
  align-items: flex-end;
  margin-bottom: 30px;
}
.overlay {
  position: absolute; top:0; left:0; width:100%; height:100%;
  background: linear-gradient(to bottom, rgba(27,40,56,0.3), #1b2838);
}
.header-content {
  position: relative; z-index: 2;
  width: 100%; max-width: 1000px; margin: 0 auto;
  padding: 0 20px 20px;
  display: flex; justify-content: space-between; align-items: flex-end;
}
.game-title {
  font-size: 2.5rem; color: white; margin: 0;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
}
.user-info {
  display: flex; align-items: center; gap: 15px;
  background: rgba(0,0,0,0.5); padding: 10px 20px; border-radius: 8px;
}
.avatar { width: 50px; height: 50px; border-radius: 4px; border: 2px solid #66c0f4; }
.user-text { display: flex; flex-direction: column; }
.nickname { font-weight: bold; color: #66c0f4; font-size: 1.1rem; }
.created-at { font-size: 0.8rem; color: #8f98a0; }

/* Content Body */
.content-body {
  max-width: 1000px; margin: 0 auto; padding: 0 20px;
  display: grid; grid-template-columns: 300px 1fr; gap: 30px;
}

/* Metrics Panel */
.metrics-panel {
  background: rgba(0,0,0,0.2);
  padding: 20px; border-radius: 8px; h-height: fit-content;
}
.metric-item {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 12px;
}
.label { width: 60px; font-weight: bold; color: #8f98a0; }
.stars { color: #444; }
.stars .filled { color: #ffc107; }
.score { font-weight: bold; color: white; width: 20px; text-align: right; }

.playtime-box {
  margin-top: 25px; padding-top: 20px;
  border-top: 1px solid #3c4450;
}
.playtime-title { color: white; margin-bottom: 10px; font-size: 1.1rem; }
.time-row { display: flex; justify-content: space-between; margin-bottom: 8px; }
.time-label { color: #8f98a0; }
.time-value { color: white; font-weight: bold; }
.highlight { color: #66c0f4; }

/* Review Text Panel */
.review-text-panel {
  background: rgba(0, 0, 0, 0.2);
  padding: 30px; border-radius: 8px;
  min-height: 400px; display: flex; flex-direction: column;
}
.panel-title { color: white; border-bottom: 1px solid #3c4450; padding-bottom: 15px; margin-top: 0; }
.review-content { line-height: 1.8; font-size: 1.05rem; color: #acb2b8; white-space: pre-line; flex-grow: 1; }

.actions { margin-top: 30px; display: flex; justify-content: flex-end; gap: 10px; }
.btn-back {
  background: #3c4450; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer;
}
.btn-delete {
  background: #c0392b; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer;
}

@media (max-width: 768px) {
  .content-body { grid-template-columns: 1fr; }
  .header-content { flex-direction: column; align-items: flex-start; gap: 10px; }
}
</style>