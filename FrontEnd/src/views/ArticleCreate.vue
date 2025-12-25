<!-- views/ArticleCreate.vue -->
<template>
  <div class="create-article">
    <div class="container">
      <h1 class="page-title">월드컵 결과 공유하기</h1>
      
      <form @submit.prevent="submitForm" class="article-form">
        <div v-if="gameInfo.id" class="winner-header">
          <div class="game-thumbnail">
            <img :src="gameInfo.image" :alt="gameInfo.title" />
          </div>
          <div class="game-details">
            <span class="badge">내가 뽑은 최고의 게임</span>
            <h2 class="game-title">{{ gameInfo.title }}</h2>
          </div>
        </div>

        <div class="form-group">
          <label for="content">게임은 어떠셨나요? 소감을 들려주세요</label>
          <textarea 
            id="content" 
            v-model="content" 
            required 
            rows="12"
          ></textarea>
        </div>

        <div class="form-actions">
          <button type="button" class="btn-cancel" @click="$router.back()">취소</button>
          <button type="submit" class="btn-submit" :disabled="isSubmitting || !content.trim()">
            {{ isSubmitting ? '공유 중...' : '게시글 등록하기' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import axios from 'axios';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

const content = ref('');
const isSubmitting = ref(false);

// 월드컵에서 넘어온 게임 정보 (게시글 제목으로 사용됨)
const gameInfo = ref({
  id: null,
  title: '',
  image: ''
});

onMounted(() => {
  if (!authStore.isAuthenticated) {
    alert('로그인이 필요한 서비스입니다.');
    router.push('/login');
    return;
  }

  // URL 쿼리 파라미터에서 게임 정보 수신
  if (route.query.gameId) {
    gameInfo.value.id = route.query.gameId;
    gameInfo.value.title = route.query.gameTitle;
    gameInfo.value.image = route.query.gameImage;
  } else {
    alert('월드컵 결과를 찾을 수 없습니다.');
    router.push({ name: 'Worldcup' });
  }
});

const submitForm = async () => {
  if (isSubmitting.value) return;
  isSubmitting.value = true;
  
  // 페이로드 구성: 제목을 게임 타이틀로 자동 설정
  const payload = {
    title: `[인생게임] ${gameInfo.value.title}`, // 앞에 말머리를 붙여 구분감을 줄 수도 있습니다
    content: content.value,
    game_id: Number(gameInfo.value.id),
  };
  console.log('디버깅!!!!!!', gameInfo.value, gameInfo)
  try {
    await axios.post('http://localhost:8000/community/articles/', payload, {
      headers: { Authorization: `Token ${authStore.token}` },
      withCredentials: true
    });

    alert('커뮤니티에 소감이 등록되었습니다!');
    router.push({ name: 'community' });

  } catch (error) {
    console.error('등록 에러:', error);
    alert('작성 실패: ' + (error.response?.data?.detail || '오류가 발생했습니다.'));
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
.create-article {
  padding: 40px 20px;
  background-color: #f9fbfd;
  min-height: 100vh;
}

.container {
  max-width: 800px;
  margin: 0 auto;
}

.page-title {
  font-size: 2rem;
  color: #2c3e50;
  margin-bottom: 30px;
  text-align: center;
}

.article-form {
  background: white;
  padding: 30px;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

/* [수정] 우승 게임 헤더 스타일 - 모든 요소 중앙 정렬 */
.winner-header {
  display: flex;
  flex-direction: column;
  align-items: center;      /* 가로축 중앙 정렬 */
  justify-content: center;   /* 세로축 중앙 정렬 */
  text-align: center;        /* 텍스트 중앙 정렬 */
  gap: 20px;
  background: linear-gradient(to bottom, #ffffff, #f0fff4);
  padding: 40px 30px;
  border-radius: 12px;
  margin-bottom: 30px;
  border: 1px dashed #42b883;
}

.game-thumbnail img {
  width: 300px;
  height: 180px;
  object-fit: cover;
  border-radius: 12px;
  box-shadow: 0 8px 16px rgba(0,0,0,0.1);
  display: block;           /* 하단 여백 제거용 */
}

/* 게임 정보 텍스트 영역 */
.game-details {
  display: flex;
  flex-direction: column;
  align-items: center;      /* 내부 요소(뱃지, 타이틀) 중앙 정렬 */
  gap: 8px;
}

.badge {
  display: inline-block;
  background: #42b883;
  color: white;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
}

.game-title {
  margin: 5px 0 0 0;
  font-size: 1.8rem;
  color: #2c3e50;
  font-weight: 800;
  line-height: 1.2;
}

/* 폼 요소 스타일 */
.form-group {
  margin-bottom: 25px;
  text-align: left;         /* 입력 안내 문구는 좌측 정렬 유지 */
}

.form-group label {
  display: block;
  font-weight: 600;
  font-size: 1.1rem;
  margin-bottom: 12px;
  color: #2c3e50;
}

/* Textarea 스타일 */
textarea {
  width: 100%;
  padding: 15px;
  border: 2px solid #c2e9d7; /* 가시적인 연한 초록색 */
  border-radius: 8px;
  background-color: #ffffff;
  font-size: 1rem;
  font-family: inherit;
  line-height: 1.6;
  transition: all 0.2s ease-in-out;
  resize: vertical;
}

textarea:focus {
  outline: none;
  border-color: #42b883; 
  background-color: #fcfdfd;
  box-shadow: 0 0 8px rgba(66, 184, 131, 0.2);
}

/* 버튼 영역 */
.form-actions {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-top: 30px;
}

.btn-cancel {
  flex: 1.5; 
  padding: 16px;
  border: none;
  background: #edf2f7;
  color: #4a5568;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-cancel:hover {
  background: #e2e8f0;
}

.btn-submit {
  flex: 3; 
  padding: 16px;
  border: none;
  background: #42b883;
  color: white;
  border-radius: 8px;
  font-weight: 600;
  font-size: 1.1rem;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-submit:hover:not(:disabled) {
  background: #36a273;
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 600px) {
  .game-thumbnail img {
    width: 100%;
    height: auto;
  }
  .game-title {
    font-size: 1.5rem;
  }
}
</style>