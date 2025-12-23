<!-- App.vue -->
<template>
  <div class="layout-wrapper">
    <header class="navbar">
      <div class="navbar-container">
        
        <div class="nav-left">
          <router-link to="/" class="logo">Steam Ecyce</router-link>

          <!-- 네비게이션 메뉴 추가 -->
          <nav class="nav-menu">
            <router-link to="/community" class="nav-link">커뮤니티</router-link>
            <router-link to="/gameinfo" class="nav-link">게임 정보</router-link>
            <router-link to="/worldcup" class="nav-link">월드컵</router-link>
          </nav>
        </div>

        <!-- 오른쪽 영역: 유저 액션 (기존 유지) -->
        <div class="nav-right">
          <!-- 조건을 'isAuthenticated' 하나만 봄 -->
          <div v-if="authStore.isAuthenticated" class="user-actions">

            <!-- 아바타 이미지 -->
            <img 
              v-if="authStore.user && authStore.user.avatar" 
              :src="authStore.user.avatar" 
              alt="User Avatar" 
              class="user-avatar"
            />
            
            <!-- 닉네임 부분 -->
            <span class="welcome-msg">
              <b v-if="authStore.user">{{ authStore.user.nickname }}</b>
              <span v-else>...</span>
              님
            </span>

            <button class="btn btn-primary" @click="goToProfile">내 라이브러리</button>
            <button class="btn btn-text" @click="handleLogout">로그아웃</button>
          </div>

          <!-- 로그아웃 상태 -->
          <div v-else>
            <button class="btn btn-primary" @click="handleSteamLogin">
              스팀 로그인
            </button>
          </div>
        </div>
      </div>
    </header>

    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';
import axios from 'axios';

const authStore = useAuthStore();
const router = useRouter();

onMounted(() => {
  authStore.initialize();
});

const handleLogout = () => {
  authStore.logout();
  router.push('/');
};

const goToProfile = () => {
  router.push('/profile');
};

const handleSteamLogin = async () => {
  try {
    const response = await axios.get('http://localhost:8000/api/auth/steam/url/');
    if (response.data.url) {
      const width = 800;
      const height = 600;
      const left = window.screenX + (window.outerWidth - width) / 2;
      const top = window.screenY + (window.outerHeight - height) / 2;

      window.open(
        response.data.url,
        'SteamLogin',
        `width=${width},height=${height},left=${left},top=${top},resizable=yes,scrollbars=yes`
      );

      window.addEventListener('message', async function onMessage(event) {
        if (event.origin !== window.location.origin) return;
        if (event.data === 'steam-login-success') {
          window.removeEventListener('message', onMessage);
          await authStore.initialize(); 
        }
      });
    }
  } catch (error) {
    console.error("로그인 시작 실패:", error);
  }
};
</script>

<style>
/* 전역 스타일 초기화 */
body {
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  background-color: #ffffff;
  color: #333333;
}

.layout-wrapper {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.navbar {
  width: 100%;
  height: 60px;
  border-bottom: 1px solid #eaeaea;
  background-color: #ffffff;
  display: flex;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 1000;
}

.navbar-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  justify-content: space-between; /* 양 끝 정렬 */
  align-items: center;
}

/* [추가] 왼쪽 영역 (로고 + 메뉴) 그룹화 */
.nav-left {
  display: flex;
  align-items: center;
  gap: 32px; /* 로고와 메뉴 사이 간격 */
}

/* 로고 스타일 */
.logo {
  font-size: 1.25rem;
  font-weight: 700;
  color: #333;
  text-decoration: none;
  letter-spacing: -0.5px;
}

/* [추가] 네비게이션 메뉴 스타일 */
.nav-menu {
  display: flex;
  gap: 20px; /* 메뉴 아이템 간 간격 */
}

/* [추가] 개별 메뉴 링크 스타일 */
.nav-link {
  text-decoration: none;
  color: #666;
  font-weight: 500;
  font-size: 0.95rem;
  transition: color 0.2s;
}

.nav-link:hover {
  color: #42b883; /* 호버 시 색상 변경 (Primary Color) */
}

/* (선택사항) 현재 활성화된 라우트 스타일 */
.router-link-active.nav-link {
  color: #42b883;
  font-weight: 600;
}

/* 우측 메뉴 영역 */
.nav-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.welcome-msg {
  font-size: 0.95rem;
  color: #555;
  margin-right: 8px;
}

.btn {
  padding: 8px 16px;
  font-size: 0.9rem;
  border-radius: 6px;
  cursor: pointer;
  text-decoration: none;
  transition: background-color 0.2s;
  border: none;
  font-weight: 500;
  display: inline-block;
}

.btn-primary {
  background-color: #42b883;
  color: white;
}

.btn-primary:hover {
  background-color: #3aa876;
}

.btn-text {
  background-color: transparent;
  color: #666;
}

.btn-text:hover {
  background-color: #f5f5f5;
  color: #333;
}

.user-avatar {
  width: 32px;      
  height: 32px;     
  border-radius: 50%; 
  object-fit: cover;  
  border: 1px solid #e0e0e0; 
  margin-right: -4px; 
}

.main-content {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
  box-sizing: border-box;
}

html {
  scrollbar-gutter: stable;
}
</style>