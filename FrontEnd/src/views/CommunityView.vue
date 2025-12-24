<template>
  <div class="community-container">
    <div class="header-section">
      <h1>커뮤니티 게시판</h1>
      <!-- 로그인한 사용자에게만 글쓰기 버튼 표시 -->
      <button v-if="authStore.isAuthenticated" @click="goToCreate" class="write-btn">
        글쓰기
      </button>
    </div>

    <!-- 로딩 상태 -->
    <div v-if="loading" class="loading">
      데이터를 불러오는 중입니다...
    </div>

    <!-- 게시글 목록 -->
    <div v-else class="article-list">
      <!-- 게시글이 없을 경우 -->
      <div v-if="articles.length === 0" class="no-data">
        작성된 게시글이 없습니다.
      </div>

      <!-- 게시글 카드 (반복) -->
      <div 
        v-for="article in articles" 
        :key="article.id" 
        class="article-card"
        @click="goToDetail(article.id)"
      >
        <!-- 썸네일 이미지 (이미지가 있을 경우 첫 번째 사진 표시) -->
        <div class="thumbnail-area">
          <img 
            v-if="article.images && article.images.length > 0" 
            :src="getImageUrl(article.images[0].image)" 
            alt="thumbnail" 
          />
          <div v-else class="no-image">No Image</div>
        </div>

        <!-- 게시글 정보 -->
        <div class="content-area">
          <h2 class="title">{{ article.title }}</h2>
          <p class="preview-text">{{ truncateText(article.article, 100) }}</p>
          
          <div class="meta-info">
            <span class="author">작성자 ID: {{ article.user }}</span>
            <span class="date">{{ formatDate(article.created_at) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth'; // 경로 확인 필요

const router = useRouter();
const authStore = useAuthStore();

const articles = ref([]);
const loading = ref(true);

// API 호출
const fetchArticles = async () => {
  try {
    const response = await axios.get('http://localhost:8000/community/articles/');
    
    // Django Pagination을 사용 중이므로 데이터는 results 안에 있습니다.
    console.log('게시글 목록:', response.data);
    articles.value = response.data.results; 
    
  } catch (error) {
    console.error('게시글 로드 실패:', error);
  } finally {
    loading.value = false;
  }
};

// 글쓰기 페이지 이동
const goToCreate = () => {
  router.push({ name: 'ArticleCreate' }); // 라우터 이름 확인
};

// 상세 페이지 이동 (추후 구현 시 사용)
const goToDetail = (id) => {
  // router.push({ name: 'ArticleDetail', params: { id } });
  console.log(`${id}번 게시글 클릭됨`);
};

// 날짜 포맷팅 함수 (YYYY-MM-DD HH:mm)
const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleString('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// 본문 미리보기 (글자수 자르기)
const truncateText = (text, length) => {
  if (!text) return '';
  return text.length > length ? text.substring(0, length) + '...' : text;
};

// 이미지 URL 처리 (http가 포함되어 있지 않으면 붙여줌)
const getImageUrl = (path) => {
  if (!path) return '';
  if (path.startsWith('http')) return path;
  return `http://localhost:8000${path}`;
};

// 컴포넌트 마운트 시 데이터 가져오기
onMounted(() => {
  fetchArticles();
});
</script>

<style scoped>
.community-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.write-btn {
  background-color: #4CAF50;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
}

.write-btn:hover {
  background-color: #45a049;
}

.article-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.article-card {
  display: flex;
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  background: white;
  height: 120px;
}

.article-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.thumbnail-area {
  width: 120px;
  height: 120px;
  background-color: #f0f0f0;
  flex-shrink: 0;
}

.thumbnail-area img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-image {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 0.8rem;
}

.content-area {
  padding: 15px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  flex-grow: 1;
}

.title {
  font-size: 1.2rem;
  margin: 0 0 5px 0;
  color: #333;
}

.preview-text {
  font-size: 0.9rem;
  color: #666;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2; /* 두 줄까지만 표시 */
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.meta-info {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  color: #999;
  margin-top: 5px;
}

.loading, .no-data {
  text-align: center;
  padding: 50px;
  color: #666;
}
</style>