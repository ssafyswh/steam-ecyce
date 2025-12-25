<!-- App.vue -->
<template>
  <div class="layout-wrapper">
    <header class="navbar">
      <div class="navbar-container">

        <div class="nav-left">
          <router-link to="/" class="logo">
            <span class="logo-steam">Steam</span>
            <span class="logo-ecyce">Ecyce</span>
          </router-link>

          <!-- 네비게이션 메뉴 추가 -->
          <nav class="nav-menu">
            <!-- <router-link to="/gameinfo" class="nav-link">게임 정보</router-link> -->
            <router-link to="/gametotal" class="nav-link">게임정보</router-link>
            <router-link to="/community" class="nav-link">커뮤니티</router-link>
            <router-link to="/worldcup" class="nav-link">월드컵</router-link>
            <router-link v-if="authStore.isAuthenticated" to="/library" class="nav-link">
              라이브러리
            </router-link>
          </nav>
        </div>

        <!-- 오른쪽 영역: 유저 액션 (기존 유지) -->
        <div class="nav-right">
          <!-- 조건을 'isAuthenticated' 하나만 봄 -->
          <div v-if="authStore.isAuthenticated" class="user-actions">
            <img v-if="authStore.user && authStore.user.avatar" :src="authStore.user.avatar" alt="User Avatar"
              class="user-avatar" />

            <span class="welcome-text">
              <router-link to="/mypage" class="nickname-box">
                <b v-if="authStore.user">{{ authStore.user.nickname }}</b>
                <span v-else>...</span>
              </router-link>
              <span class="suffix-text">님</span>
            </span>

            <button @click="handleLogout" class="btn btn-outline logout-btn">로그아웃</button>
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
/* Reset & Global Base */
html {
  scrollbar-gutter: stable;
}

body {
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  background-color: #ffffff;
  color: #333333;
}

/* 레이아웃 */
.layout-wrapper {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main-content {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
  box-sizing: border-box;
}

/* navbar */
.navbar {
  width: 100%;
  height: 60px;
  background-color: #ffffff;
  border-bottom: 1px solid #eaeaea;
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
  justify-content: space-between;
  align-items: center;
}

.nav-left, .nav-right, .user-actions {
  display: flex;
  align-items: center;
}

.nav-left { gap: 32px; }
.nav-right { gap: 16px; }
.user-actions { gap: 12px; }

/* 사이트 로고 */
.logo {
  display: flex;
  align-items: center;
  gap: 5px;
  text-decoration: none;
  transition: opacity 0.2s;
}

.logo:hover {
  opacity: 0.8;
}

.logo-steam {
  color: #171a21;
  font-weight: 900;
  font-size: 1.4rem;
  letter-spacing: -1px;
  text-shadow: 1px 1px 0px #dcdcdc;
}

.logo-ecyce {
  color: #66c0f4;
  font-weight: 400;
  font-size: 1.4rem;
  letter-spacing: -1px;
}

/* navbar 메뉴 */
.nav-menu {
  display: flex;
  gap: 20px;
}

.nav-link {
  text-decoration: none;
  color: #666;
  font-weight: 500;
  font-size: 0.95rem;
  transition: color 0.2s;
}

.nav-link:hover,
.router-link-active.nav-link {
  color: #42b883;
}

.router-link-active.nav-link {
  font-weight: 600;
}

/* 사용자 정보 */
.welcome-text {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 0.95rem;
  color: #4a4a4a;
}

.nickname-box {
  display: inline-block;
  background-color: transparent;
  border: none;
  padding: 0;
  color: #171a21 !important;
  font-weight: 700;
  text-decoration: none;
  transition: color 0.2s ease;
  cursor: pointer;
}

.nickname-box:hover {
  color: #66c0f4 !important;
  background-color: transparent;
  box-shadow: none;
}

.suffix-text {
  font-weight: 500;
  color: #333333; /* '님' 글자색을 더 진하게 설정 */
  margin-left: 1px;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
  object-fit: cover;
}

/* 버튼 */
.btn {
  padding: 8px 16px;
  font-size: 0.9rem;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
  display: inline-block;
}

.btn-primary {
  background-color: #42b883;
  color: white;
}

.btn-primary:hover {
  background-color: #3aa876;
}

.logout-btn {
  margin-left: 15px;
  padding: 5px 12px;
  font-size: 0.85rem;
  background-color: transparent;
  border: 1px solid #eaeaea;
  color: #666;
}

.logout-btn:hover {
  background-color: #f5f5f5;
  color: #333;
}
</style>