<!-- views/CommunityView.vue -->
<template>
  <div class="community-container">
    <div class="header-section">
      <h1>커뮤니티 게시판</h1>
    </div>

    <div v-if="loading" class="loading">데이터를 불러오는 중입니다...</div>

    <div v-else class="article-list">
      <div v-if="articles.length === 0" class="no-data">작성된 게시글이 없습니다.</div>

      <div 
        v-for="article in articles" 
        :key="article.id" 
        class="article-card"
        @click="goToDetail(article.id)"
      >
        <div class="thumbnail-area">
          <img 
            v-if="article.game_image" 
            :src="article.game_image" 
            :alt="article.game_title" 
          />
          <div v-else class="no-image">No Game Info</div>
        </div>

        <div class="content-area">
          <h2 class="title">{{ article.title }}</h2>
          
          <p class="preview-text">{{ truncateText(article.content, 100) }}</p>
          
          <div class="meta-info">
            <div class="author-info">
              <img 
                :src="article.user_avatar || '/default-avatar.png'" 
                class="user-avatar" 
                alt="profile"
              />
              <span class="author-name">{{ article.user_nickname || 'Unknown' }}</span>
            </div>
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
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const authStore = useAuthStore();

const articles = ref([]);
const loading = ref(true);

const fetchArticles = async () => {
  try {
    const response = await axios.get('http://localhost:8000/community/articles/');
    // DRF Pagination을 쓰는 경우 response.data.results, 아니면 response.data
    articles.value = response.data.results || response.data; 
  } catch (error) {
    console.error('게시글 로드 실패:', error);
  } finally {
    loading.value = false;
  }
};

const goToCreate = () => {
  // 그냥 글쓰기 버튼을 눌렀을 때는 월드컵 페이지로 보내는 것이 
  // 우리 기획(우승작 공유)에 더 맞을 수 있습니다.
  router.push({ name: 'Worldcup' }); 
};

const goToDetail = (id) => {
  router.push({ name: 'ArticleDetail', params: { id } });
};

const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};

const truncateText = (text, length) => {
  if (!text) return '';
  return text.length > length ? text.substring(0, length) + '...' : text;
};

onMounted(fetchArticles);
</script>

<style scoped>
/* 1. 레이아웃 및 컨테이너 */
.community-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 20px;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.header-section h1 {
  font-size: 1.8rem;
  color: #2c3e50;
  margin: 0;
}

/* 2. 게시글 목록 및 카드 구조 */
.article-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.article-card {
  display: flex;
  border: 1px solid #eef2f7;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s ease;
  background: white;
  height: 140px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.article-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.1);
  border-color: #42b883;
}

/* 3. 카드 내부 이미지 영역 */
.thumbnail-area {
  width: 220px;
  background-color: #f0f0f0;
  flex-shrink: 0;
}

.thumbnail-area img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 4. 카드 내부 콘텐츠 영역 */
.content-area {
  padding: 20px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  flex-grow: 1;
  text-align: left;
  min-width: 0; /* flex 자식의 텍스트 말줄임표 처리를 위함 */
}

.title {
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0;
  color: #2c3e50;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.preview-text {
  font-size: 0.95rem;
  color: #64748b;
  margin: 10px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.5;
}

/* 5. 메타 정보 (작성자 및 날짜) */
.meta-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
  color: #94a3b8;
  margin-top: auto;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid #eee;
}

.author-name {
  font-weight: 600;
  color: #475569;
}

/* 6. 공통 컴포넌트 및 상태 */
.write-btn {
  background-color: #42b883;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
  transition: background 0.2s;
}

.write-btn:hover {
  background-color: #36a273;
}

.loading, .no-data {
  padding: 100px 0;
  color: #94a3b8;
  font-size: 1.1rem;
  text-align: center;
}
</style>