<!-- views/ArticleDetail.vue -->
<template>
  <div class="article-detail-container" v-if="article">
    <section class="game-banner">
      <div class="banner-overlay">
        <img :src="article.game_image" class="banner-bg" alt="Game Banner" />
        <div class="banner-content">
          <span class="badge">TOP PICK GAME</span>
          <h1 class="game-title">{{ article.game_title }}</h1>
        </div>
      </div>
    </section>

    <div class="detail-content-wrapper">
      <header class="article-header">
        <h2 class="article-title">{{ article.title }}</h2>
        
        <div class="header-meta-area">
          <div class="author-box" @click="goToProfile(article.user)">
            <img :src="article.user_avatar || '/default-avatar.png'" class="author-avatar" />
            <div class="author-text">
              <span class="author-nickname">{{ article.user_nickname || '익명' }}</span>
              <span class="created-at">{{ formatDate(article.created_at) }}</span>
            </div>
          </div>
          
          <div v-if="isAuthor" class="author-actions">
            <button @click="editArticle" class="btn-edit">수정</button>
            <button @click="deleteArticle" class="btn-delete">삭제</button>
          </div>
        </div>
      </header>

      <hr class="divider" />

      <article class="article-body">
        <p class="content-text">{{ article.content }}</p>
      </article>

      <hr class="divider" />

      <section class="comment-section">
  <div class="comment-header">
    <h3>댓글 <span class="comment-count">{{ article.comments?.length || 0 }}</span></h3>
  </div>

  <div v-if="authStore.isAuthenticated" class="comment-form">
    <textarea 
      v-model="newComment" 
      placeholder="비방이나 욕설 없는 따뜻한 댓글을 남겨주세요."
      rows="3"
    ></textarea>
    <div class="comment-form-footer">
      <button 
        @click="submitComment" 
        :disabled="!newComment.trim()" 
        class="btn-comment-submit"
      >댓글 등록</button>
    </div>
  </div>
  <div v-else class="login-prompt">
    <p>댓글을 작성하려면 <router-link :to="{ name: 'Login' }">로그인</router-link>이 필요합니다.</p>
  </div>

  <div class="comment-list">
    <div v-if="article.comments?.length === 0" class="no-comments">
      첫 번째 댓글을 남겨보세요!
    </div>
    <div 
      v-for="comment in article.comments" 
      :key="comment.id" 
      class="comment-item"
    >
      <img :src="comment.user_avatar || '/default-avatar.png'" class="comment-avatar" />
      <div class="comment-content-area">
        <div class="comment-info">
          <span class="comment-author">{{ comment.user_nickname }}</span>
          <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
        </div>
        <p class="comment-text">{{ comment.content }}</p>
      </div>
      <button 
        v-if="authStore.user?.pk === comment.user" 
        @click="deleteComment(comment.id)" 
        class="btn-comment-delete"
      >삭제</button>
    </div>
  </div>
</section>
      
      <div class="list-btn-area">
        <button @click="$router.push({ name: 'community' })" class="btn-list">목록으로 돌아가기</button>
      </div>
    </div>
  </div>
  
  <div v-else-if="loading" class="loading-state">
    <div class="spinner"></div>
    <p>데이터를 불러오고 있습니다...</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import { useAuthStore } from '@/stores/auth';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const article = ref(null);
const loading = ref(true);
const newComment = ref('');

// [계산된 속성] 작성자 본인 여부 확인 (PK 비교)
const isAuthor = computed(() => {
  return authStore.user && article.value && authStore.user.pk === article.value.user;
});

const fetchArticleDetail = async () => {
  const articleId = route.params.id;
  try {
    const response = await axios.get(`http://localhost:8000/community/articles/${articleId}/`);
    article.value = response.data;
  } catch (error) {
    console.error('상세 정보 로드 실패:', error);
    alert('게시글을 불러올 수 없습니다.');
    router.push({ name: 'community' });
  } finally {
    loading.value = false;
  }
};

const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleString('ko-KR', {
    year: 'numeric', month: 'long', day: 'numeric',
    hour: '2-digit', minute: '2-digit'
  });
};

const goToProfile = (userId) => {
  console.log(`${userId}번 유저 프로필로 이동`);
};

// 게시글 삭제 로직
const deleteArticle = async () => {
  if (!confirm('정말 이 게시글을 삭제하시겠습니까?')) return;
  
  try {
    await axios.delete(`http://localhost:8000/community/articles/${article.value.id}/`, {
      headers: { Authorization: `Token ${authStore.token}` },
      withCredentials: true
    });
    alert('성공적으로 삭제되었습니다.');
    router.push({ name: 'community' });
  } catch (error) {
    console.error('삭제 에러:', error);
    alert('삭제에 실패했습니다.');
  }
};

const editArticle = () => {
  // router.push({ name: 'ArticleUpdate', params: { id: article.value.id } });
  alert('수정 기능 준비 중입니다.');
};

// 댓글 등록 로직
const submitComment = async () => {
  if (!newComment.value.trim()) return;

  try {
    const response = await axios.post('http://localhost:8000/community/comments/', {
      article: article.value.id, // 부모 게시글 ID
      content: newComment.value
    }, {
      headers: { Authorization: `Token ${authStore.token}` },
      withCredentials: true
    });

    // 작성 성공 후 목록 갱신 (다시 불러오기)
    await fetchArticleDetail();
    newComment.value = ''; // 입력창 초기화
  } catch (error) {
    console.error('댓글 등록 에러:', error);
    alert('댓글 등록에 실패했습니다.');
  }
};

// 댓글 삭제 로직
const deleteComment = async (commentId) => {
  if (!confirm('댓글을 삭제하시겠습니까?')) return;

  try {
    await axios.delete(`http://localhost:8000/community/comments/${commentId}/`, {
      headers: { Authorization: `Token ${authStore.token}` },
      withCredentials: true
    });
    await fetchArticleDetail(); // 목록 갱신
  } catch (error) {
    alert('댓글 삭제 실패');
  }
};

onMounted(fetchArticleDetail);
</script>

<style scoped>
.article-detail-container {
  max-width: 900px;
  margin: 0 auto;
  background: white;
  min-height: 100vh;
  box-shadow: 0 0 20px rgba(0,0,0,0.05);
}

/* 상단 게임 배너 */
.game-banner {
  position: relative;
  height: 350px;
  overflow: hidden;
}

.banner-bg {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: brightness(0.5);
}

.banner-content {
  position: absolute;
  bottom: 40px;
  left: 40px;
  color: white;
  text-align: left;
}

.badge {
  background: #42b883;
  padding: 5px 12px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 1px;
}

.game-title {
  font-size: 2.8rem;
  font-weight: 800;
  margin: 15px 0 0 0;
  text-shadow: 0 4px 10px rgba(0,0,0,0.3);
}

/* 본문 레이아웃 */
.detail-content-wrapper {
  padding: 50px;
  text-align: left;
}

.article-header {
  margin-bottom: 30px;
}

.article-title {
  font-size: 2rem;
  color: #1e293b;
  margin-bottom: 25px;
  font-weight: 800;
}

.header-meta-area {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 작성자 정보 */
.author-box {
  display: flex;
  align-items: center;
  gap: 15px;
  cursor: pointer;
}

.author-avatar {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  border: 2px solid #e2e8f0;
}

.author-nickname {
  display: block;
  font-weight: 700;
  font-size: 1.1rem;
  color: #334155;
}

.created-at {
  font-size: 0.85rem;
  color: #94a3b8;
}

/* [추가] 수정/삭제 버튼 스타일 */
.author-actions {
  display: flex;
  gap: 10px;
}

.btn-edit, .btn-delete {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #e2e8f0;
}

.btn-edit {
  background: white;
  color: #64748b;
}

.btn-edit:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
}

.btn-delete {
  background: #fff1f2;
  color: #e11d48;
  border-color: #fecdd3;
}

.btn-delete:hover {
  background: #ffe4e6;
}

/* 게시글 본문 */
.article-body {
  padding: 30px 0;
}

.content-text {
  line-height: 2;
  font-size: 1.15rem;
  color: #334155;
  white-space: pre-wrap;
}

.divider {
  border: 0;
  border-top: 1px solid #f1f5f9;
  margin: 30px 0;
}

/* 하단 목록 버튼 */
.list-btn-area {
  margin-top: 60px;
  text-align: center;
}

.btn-list {
  padding: 14px 40px;
  background: #334155;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.2s;
}

.btn-list:hover {
  background: #1e293b;
}

/* 로딩 상태 */
.loading-state {
  padding: 100px 0;
  text-align: center;
  color: #64748b;
}

/* 댓글 섹션 스타일 */
.comment-section {
  margin-top: 40px;
}

.comment-header h3 {
  font-size: 1.3rem;
  color: #1e293b;
  margin-bottom: 20px;
}

.comment-count {
  color: #42b883;
}

/* 댓글 입력창 */
.comment-form {
  background: #f8fafc;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 30px;
}

.comment-form textarea {
  width: 100%;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 12px;
  resize: none;
  font-family: inherit;
}

.comment-form-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 10px;
}

.btn-comment-submit {
  background: #42b883;
  color: white;
  border: none;
  padding: 8px 20px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}

/* 댓글 리스트 */
.comment-item {
  display: flex;
  gap: 15px;
  padding: 20px 0;
  border-bottom: 1px solid #f1f5f9;
  position: relative;
}

.comment-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.comment-content-area {
  flex: 1;
}

.comment-info {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-bottom: 5px;
}

.comment-author {
  font-weight: 700;
  font-size: 0.95rem;
  color: #334155;
}

.comment-date {
  font-size: 0.8rem;
  color: #94a3b8;
}

.comment-text {
  color: #475569;
  line-height: 1.5;
  margin: 0;
}

.btn-comment-delete {
  font-size: 0.8rem;
  color: #94a3b8;
  background: none;
  border: none;
  cursor: pointer;
}

.btn-comment-delete:hover {
  color: #e11d48;
  text-decoration: underline;
}

.login-prompt {
  padding: 20px;
  background: #f1f5f9;
  border-radius: 8px;
  text-align: center;
  color: #64748b;
}

.no-comments {
  padding: 40px 0;
  text-align: center;
  color: #94a3b8;
  font-style: italic;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #42b883;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>