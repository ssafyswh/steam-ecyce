<!-- App.vue -->
<template>
  <div class="container">
    <h1>Steam Django App</h1>

    <div v-if="authStore.isAuthenticated && authStore.user">
      <h2>👋 안녕하세요, <span style="color: #42b883;">{{ authStore.user.nickname }}</span>님!</h2>
      
      <button class="check-btn" @click="goToProfile">내 라이브러리 보러가기</button>
      
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

const authStore = useAuthStore();
const router = useRouter();

onMounted(() => {
  authStore.initialize();
});

const handleLogout = () => {
  authStore.logout();
  router.push('/login');
};

// 프로필 페이지로 이동
const goToProfile = () => {
  router.push('/profile');
};
</script>

<style>
.container { text-align: center; margin-top: 50px; font-family: sans-serif; }
button { padding: 8px 16px; cursor: pointer; background: #ff4d4f; color: white; border: none; border-radius: 4px; }
.check-btn { background-color: #42b883; margin-right: 10px; }
</style>