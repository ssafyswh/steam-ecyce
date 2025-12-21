<!-- views/GameDetailView.vue -->
<template>
  <div v-if="game" class="detail-container">
    <section class="game-header">
      <img :src="game.header_image" :alt="game.title" class="main-banner" />
      <div class="header-info">
        <h1>{{ game.title }}</h1>
        <div class="user-stats" v-if="game.playtime_total">
          내 플레이 시간: <span>{{ (game.playtime_total / 60).toFixed(1) }}시간</span>
        </div>
      </div>
    </section>

    <section class="ai-review-section">
      <div class="section-title">
        <span class="ai-icon">🤖</span>
        <h3>Friday의 AI 리뷰 분석 리포트</h3>
      </div>

      <div v-if="game.review_summary" class="review-content">
        <div class="summary-card">
          <h4>"{{ game.review_summary.one_liner }}"</h4>
        </div>
        </div>


      <div v-else class="no-data">
        <p>아직 이 게임에 대한 AI 분석 데이터가 없습니다.</p>
        <button @click="requestAiAnalysis" class="analysis-btn">분석 요청하기</button>
      </div>
    </section>
  </div>
</template>

<script setup>
    import { ref, onMounted } from 'vue';
    import { useRoute } from 'vue-router';
    import axios from 'axios';

    const route = useRoute();
    const game = ref(null);

    const fetchGameDetail = async () => {
        const response = await axios.get(`http://localhost:8000/games/${route.params.id}/`);
        game.value = response.data;
    }

    onMounted(fetchGameDetail);
</script>

<style scoped>
.detail-container { max-width: 1000px; margin: 0 auto; padding: 30px; }

.main-banner { width: 100%; border-radius: 10px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }

.ai-review-section {
  background: #1b2838;
  border: 1px solid #2a475e;
  border-radius: 12px;
  padding: 30px;
  margin-top: 40px;
}

.section-title { display: flex; align-items: center; gap: 10px; margin-bottom: 25px; }
.ai-icon { font-size: 1.5rem; }

.summary-card {
  background: rgba(102, 192, 244, 0.1);
  border-left: 5px solid #66c0f4;
  padding: 20px;
  margin-bottom: 25px;
  font-style: italic;
  font-size: 1.2rem;
  color: #ffffff;
}

.review-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }

.review-box { padding: 20px; border-radius: 8px; background: rgba(0,0,0,0.2); }
.review-box h5 { margin-bottom: 15px; font-size: 1.1rem; }

.positive { border-top: 3px solid #a3cf06; } /* 스팀 긍정색 */
.positive h5 { color: #a3cf06; }

.negative { border-top: 3px solid #c1594a; } /* 스팀 부정색 */
.negative h5 { color: #c1594a; }

.review-box ul { padding-left: 20px; color: #acb2b8; }
.review-box li { margin-bottom: 8px; line-height: 1.4; }

.target-box {
  margin-top: 25px;
  padding: 15px;
  background: #2a475e;
  border-radius: 6px;
  color: #ffffff;
}

.analysis-btn {
  background: #66c0f4;
  color: #1b2838;
  padding: 10px 25px;
  border: none;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
}
</style>