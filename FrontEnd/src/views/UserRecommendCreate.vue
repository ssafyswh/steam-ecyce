<!-- views/UserRecommendCreate.vue -->
<template>
  <div class="review-create-container">
    <div class="review-card">
      <h1 class="page-title">게임 리뷰 작성</h1>
      <p class="subtitle">이 게임의 5가지 매력을 평가해주세요!</p>
      
      <form @submit.prevent="submitReview">
        <!-- 5가지 지표 별점 입력 -->
        <div class="ratings-group">
          <div v-for="(label, key) in metrics" :key="key" class="rating-item">
            <label class="metric-label">{{ label }}</label>
            <div class="stars">
              <span 
                v-for="star in 5" 
                :key="star" 
                @click="setRating(key, star)"
                class="star-icon"
                :class="{ 'filled': star <= reviewData[key] }"
              >
                ★
              </span>
            </div>
            <span class="score-text">{{ reviewData[key] }}점</span>
          </div>
        </div>

        <!-- 리뷰 내용 입력 -->
        <div class="content-group">
          <label for="content" class="content-label">상세 후기</label>
          <textarea 
            id="content" 
            v-model="reviewData.content" 
            placeholder="게임에 대한 솔직한 감상평을 남겨주세요 (최소 10자 이상)"
            class="review-textarea"
            required
          ></textarea>
        </div>

        <div class="button-group">
          <button type="button" @click="goBack" class="cancel-btn">취소</button>
          <button type="submit" class="submit-btn">리뷰 등록</button>
        </div>
      </form>
    </div>
  </div>
</template>
<script setup>
import { reactive, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const gameId = route.params.id || route.params.gameId
const reviewId = ref(null) // 기존 리뷰가 있을 경우 ID 저장

const metrics = {
  rating_fun: '재미',
  rating_story: '스토리',
  rating_control: '조작감',
  rating_sound: '사운드',
  rating_optimization: '최적화',
}

const reviewData = reactive({
  rating_fun: 0,
  rating_story: 0,
  rating_control: 0,
  rating_sound: 0,
  rating_optimization: 0,
  content: '',
})

const setRating = (key, score) => {
  reviewData[key] = score
}

// 기존 리뷰 존재 여부 확인 및 데이터 로드
const loadExistingReview = async () => {
  try {
    const response = await axios.get(`http://localhost:8000/community/reviews/`, {
      params: { game_id: gameId },
      withCredentials: true
    })
    
    // [에러 해결] DRF 페이지네이션으로 인해 데이터는 results 안에 있습니다.
    const results = response.data.results || response.data;
    
    // 이미 views.py에서 본인 리뷰만 나오도록 필터링했으므로 첫 번째 항목을 가져옵니다.
    if (results && results.length > 0) {
      const myReview = results[0];
      
      reviewId.value = myReview.id
      reviewData.rating_fun = myReview.rating_fun
      reviewData.rating_story = myReview.rating_story
      reviewData.rating_control = myReview.rating_control
      reviewData.rating_sound = myReview.rating_sound
      reviewData.rating_optimization = myReview.rating_optimization
      reviewData.content = myReview.content
    }
  } catch (error) {
    console.error("기존 리뷰 로드 실패:", error)
  }
}

onMounted(() => {
  if (!authStore.isAuthenticated) {
    alert('로그인이 필요합니다.')
    router.push({ name: 'login' })
    return
  }
  loadExistingReview()
})

const submitReview = async () => {
  // 유효성 검사 로직 (기존과 동일)
  for (const key in metrics) {
    if (reviewData[key] === 0) {
      alert(`${metrics[key]} 점수를 선택해주세요!`)
      return
    }
  }
  if (reviewData.content.length < 10) {
    alert('리뷰 내용을 10자 이상 작성해주세요.')
    return
  }

  try {
    const payload = { game_id: Number(gameId), ...reviewData }
    const config = {
      headers: { Authorization: `Bearer ${authStore.token}` },
      withCredentials: true
    }

    let response
    if (reviewId.value) {
      // [수정] 기존 리뷰가 있으면 PUT 요청
      response = await axios.put(`http://localhost:8000/community/reviews/${reviewId.value}/`, payload, config)
    } else {
      // [신규] 없으면 POST 요청
      response = await axios.post('http://localhost:8000/community/reviews/', payload, config)
    }

    router.push({ name: 'UserRecommendDetail', params: { reviewId: response.data.id } })
  } catch (error) {
    alert('처리 중 오류가 발생했습니다.')
  }
}
</script>

<style scoped>
/* 디자인은 유지 */
.review-create-container {
  min-height: 100vh;
  padding: 40px 20px;
  background-color: #f9fbfd;
}

.review-card {
  max-width: 600px;
  margin: 0 auto;
  padding: 40px;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.page-title {
  text-align: center;
  margin: 0 0 10px 0;
  color: #2c3e50;
  font-size: 1.8rem;
  font-weight: 700;
}

.subtitle {
  text-align: center;
  color: #666;
  margin-bottom: 30px;
}

/* 별점 영역 */
.ratings-group {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 30px;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
}

.rating-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.metric-label {
  font-weight: bold;
  width: 70px;
  color: #444;
}

.stars {
  flex-grow: 1;
  text-align: center;
}

.star-icon {
  font-size: 28px;
  cursor: pointer;
  color: #e0e0e0;
  transition: color 0.2s, transform 0.1s;
  padding: 0 5px;
}

.star-icon:hover {
  transform: scale(1.1);
}

.star-icon.filled {
  color: #ffc107; 
}

.score-text {
  width: 40px;
  text-align: right;
  font-weight: bold;
  color: #ffc107;
}

/* 텍스트 영역 */
.content-group {
  margin-bottom: 30px;
}

.content-label {
  display: block;
  font-weight: bold;
  margin-bottom: 10px;
  color: #444;
}

.review-textarea {
  width: 100%;
  height: 150px;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  resize: none;
  font-size: 1rem;
  background-color: #fff;
}

.review-textarea:focus {
  outline: none;
  border-color: #42b883;
  box-shadow: 0 0 0 3px rgba(66, 184, 131, 0.2);
}

/* 버튼 영역 */
.button-group {
  display: flex;
  justify-content: center;
  gap: 15px;
}

.submit-btn {
  padding: 14px 40px;
  background-color: #42b883;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: bold;
  cursor: pointer;
  font-size: 1rem;
  transition: background 0.2s;
  flex: 1;
}

.submit-btn:hover {
  background-color: #36a273;
}

.cancel-btn {
  padding: 14px 40px;
  background-color: #edf2f7;
  color: #4a5568;
  border: none;
  border-radius: 6px;
  font-weight: bold;
  cursor: pointer;
  font-size: 1rem;
  transition: background 0.2s;
  flex: 1;
}

.cancel-btn:hover {
  background-color: #e2e8f0;
}
</style>