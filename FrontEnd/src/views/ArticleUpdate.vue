<template>
  <div class="update-container" v-if="title !== null">
    <h1>우승 후기 수정하기</h1>
    <div class="game-info-preview">
      <img :src="gameImage" class="mini-game-img" />
      <p>대상 게임: <strong>{{ gameTitle }}</strong></p>
    </div>

    <form @submit.prevent="updateArticle" class="update-form">
      <div class="input-group">
        <label>제목</label>
        <input v-model="title" type="text" required />
      </div>

      <div class="input-group">
        <label>내용</label>
        <textarea v-model="content" rows="10" required></textarea>
      </div>

      <div class="actions">
        <button type="button" @click="$router.back()" class="btn-cancel">취소</button>
        <button type="submit" class="btn-submit">수정 완료</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import { useAuthStore } from '@/stores/auth';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const title = ref(null);
const content = ref('');
const gameTitle = ref('');
const gameImage = ref('');

// 1. 기존 데이터 불러오기
const fetchOriginalData = async () => {
  try {
    const response = await axios.get(`http://localhost:8000/community/articles/${route.params.id}/`);
    const data = response.data;
    
    const currentUserId = authStore.user?.id || authStore.user?.pk;
    const authorId = data.user;

    console.log('현재 로그인 유저 ID:', currentUserId);
    console.log('게시글 작성자 ID:', authorId);

    if (Number(currentUserId) !== Number(authorId)) {
      alert('수정 권한이 없습니다.');
      router.back();
      return;
    }

    title.value = data.title;
    content.value = data.content;
    gameTitle.value = data.game_title;
    gameImage.value = data.game_image;
  } catch (err) {
    console.error(err);
    alert('데이터를 불러오지 못했습니다.');
    router.back();
  }
};

// 2. 수정 요청 보내기 (PUT 또는 PATCH)
const updateArticle = async () => {
  try {
    await axios.patch(`http://localhost:8000/community/articles/${route.params.id}/`, {
      title: title.value,
      content: content.value
    }, {
      headers: { Authorization: `Token ${authStore.token}` }
    });
    
    alert('수정되었습니다.');
    router.push({ name: 'ArticleDetail', params: { id: route.params.id } });
  } catch (err) {
    alert('수정에 실패했습니다.');
  }
};

onMounted(fetchOriginalData);
</script>

<style scoped>
/* 기존 Create 스타일과 유사하게 유지하되 게임 정보 미리보기 추가 */
.update-container { max-width: 700px; margin: 40px auto; padding: 20px; }
.game-info-preview { display: flex; align-items: center; gap: 15px; background: #f8fafc; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
.mini-game-img { width: 100px; height: 60px; object-fit: cover; border-radius: 4px; }
.input-group { margin-bottom: 20px; display: flex; flex-direction: column; gap: 8px; text-align: left; }
input, textarea { padding: 12px; border: 1px solid #ddd; border-radius: 8px; }
.actions { display: flex; gap: 10px; justify-content: flex-end; }
.btn-submit { background: #42b883; color: white; border: none; padding: 10px 24px; border-radius: 6px; cursor: pointer; font-weight: bold; }
.btn-cancel { background: #eee; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; }
</style>