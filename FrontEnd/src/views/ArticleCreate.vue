<!-- ArticleCreate.vue -->
<template>
  <div class="create-article">
    <h1>게시글 작성</h1>
    <form @submit.prevent="submitForm">
      
      <!-- 제목 -->
      <div class="form-group">
        <label for="title">제목</label>
        <input 
          type="text" 
          id="title" 
          v-model="title" 
          required 
          placeholder="제목을 입력하세요"
        />
      </div>

      <!-- 게임 선택 (선택 사항) -->
      <div class="form-group">
        <label for="game">게임 ID (예시)</label>
        <input 
          type="number" 
          id="game" 
          v-model="gameId" 
          placeholder="게임 ID 입력 (선택)"
        />
      </div>

      <!-- 내용 -->
      <div class="form-group">
        <label for="content">내용</label>
        <textarea 
          id="content" 
          v-model="content" 
          required 
          rows="5"
        ></textarea>
      </div>

      <!-- 이미지 업로드 (다중 선택 가능) -->
      <div class="form-group">
        <label for="images">이미지 첨부</label>
        <input 
          type="file" 
          id="images" 
          ref="fileInput" 
          multiple 
          @change="handleFileUpload" 
          accept="image/*"
        />
      </div>

      <!-- 미리보기 (선택 사항) -->
      <div v-if="previewImages.length" class="preview-container">
        <div v-for="(src, index) in previewImages" :key="index" class="preview-item">
          <img :src="src" alt="preview" />
        </div>
      </div>

      <button type="submit">작성하기</button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

// 상태 변수들
const title = ref('');
const content = ref('');
const gameId = ref(null); // 필요 없다면 생략 가능
const files = ref([]); // 실제 파일 객체 저장
const previewImages = ref([]); // 미리보기 URL 저장
const authStore = useAuthStore();


const router = useRouter();
const fileInput = ref(null);

// 파일 선택 시 처리
const handleFileUpload = (event) => {
  const selectedFiles = Array.from(event.target.files);
  files.value = selectedFiles;

  // 미리보기 생성
  previewImages.value = selectedFiles.map((file) => URL.createObjectURL(file));
};

// ArticleCreate.vue 내부 submitForm 함수 수정

const submitForm = async () => {
  // 쿠키 인증을 사용하므로 토큰 존재 여부 확인은 authStore의 상태로만 체크하면 됩니다.
  if (!authStore.isAuthenticated) {
    alert('로그인이 필요합니다.');
    return;
  }

  const formData = new FormData();
  formData.append('title', title.value);
  
  // 보내는 키값('article')이 모델/시리얼라이저 필드명과 일치하는지 꼭 확인하세요
  console.log(content.value)
  formData.append('article', content.value); 
  // 만약 모델 필드명이 article이라면 기존대로 'article' 유지: formData.append('article', content.value);

  if (gameId.value) {
    formData.append('game_id', gameId.value);
  }

  files.value.forEach((file) => {
    formData.append('images', file);
  });

  try {
    // 헤더에 Token을 직접 넣지 않고, 쿠키를 포함시켜 보냅니다.
    const response = await axios.post('http://localhost:8000/community/articles/', formData, {
      withCredentials: true, // 이게 있어야 브라우저가 쿠키(access_token)를 같이 보냅니다.
      headers: {
        'Content-Type': 'multipart/form-data', // 파일 업로드 시 명시 권장 (axios가 자동설정하기도 함)
      }
    });

    console.log('성공:', response.data);
    alert('게시글이 작성되었습니다!');
    router.push({ name: 'community' }); // 뷰 이름 확인 필요

  } catch (error) {
    console.error('에러 상세:', error);
    const msg = error.response?.data ? JSON.stringify(error.response.data) : error.message;
    alert(`작성 실패: ${msg}`);
  }
};
</script>

<style scoped>
.form-group {
  margin-bottom: 15px;
}
.preview-container {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}
.preview-item img {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border-radius: 5px;
}
</style>