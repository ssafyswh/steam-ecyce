<!-- App.vue -->
<template>
  <div class="container">
    <h1>Steam Django App</h1>

    <div v-if="authStore.isAuthenticated && authStore.user">
      <h2>👋 안녕하세요, <span style="color: #42b883;">{{ authStore.user.nickname }}</span>님!</h2>
      <button class="check-btn" @click="checkUserInfo">내 정보 확인</button>
      <br><br>
      <button @click="handleLogout">로그아웃</button>
    </div>

    <div v-else>
      <p>로그인이 필요합니다.</p>
      <router-link to="/login">스팀 로그인 하러 가기</router-link>
    </div>

    <hr>
    <RouterView />
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';
import axios from 'axios'

const authStore = useAuthStore();
const router = useRouter();

// 앱 켜지자마자 토큰 확인하고 유저 정보 가져오기
onMounted(() => {
  authStore.initialize();
});

const handleLogout = () => {
  authStore.logout();
  router.push('/login');
};

// 내 정보 확인 함수
const checkUserInfo = async () => {
  try {
    const response = await axios.get('http://localhost:8000/api/auth/user/me/', {
      withCredentials: true 
    });

    console.log("API 응답 결과:", response.data);
    alert(`[성공] 서버에서 받은 steamId: ${response.data.username}`);
    
  } catch (error) {
    console.error("API 요청 실패:", error);
    alert("정보를 가져오는데 실패했습니다. (콘솔 확인)");
  }
};

</script>

<style>
.container { text-align: center; margin-top: 50px; font-family: sans-serif; }
button { padding: 8px 16px; cursor: pointer; background: #ff4d4f; color: white; border: none; border-radius: 4px; }
</style>