<!-- App.vue -->
<template>
  <div class="layout-wrapper">
    <!-- 1. 상단 네비게이션 바 -->
    <header class="navbar">
      <div class="navbar-container">
        <!-- 로고 (왼쪽) -->
        <router-link to="/" class="logo">
          Steam Ecyce
        </router-link>

        <!-- 메뉴 영역 (오른쪽) -->
        <div class="nav-right">
          <!-- 로그인 상태일 때 -->
          <div v-if="authStore.isAuthenticated && authStore.user" class="user-actions">
            <span class="welcome-msg">
              <b>{{ authStore.user.nickname }}</b>님
            </span>
            <button class="btn btn-primary" @click="goToProfile">내 라이브러리</button>
            <button class="btn btn-text" @click="handleLogout">로그아웃</button>
          </div>

          <!-- 로그아웃 상태일 때 (여기 수정됨) -->
          <div v-else>
            <!-- router-link 대신 button으로 변경하고 클릭 이벤트 연결 -->
            <button class="btn btn-primary" @click="handleSteamLogin">
              스팀 로그인
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- 2. 메인 컨텐츠 영역 -->
    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';
import axios from 'axios'; // axios 추가

const authStore = useAuthStore();
const router = useRouter();

onMounted(() => {
  authStore.initialize();
});

const handleLogout = () => {
  authStore.logout();
  router.push('/');
};

// 프로필 페이지로 이동
const goToProfile = () => {
  router.push('/profile');
};

// 스팀 로그인 로직
const handleSteamLogin = async () => {
  try {
    // Django에게 스팀 로그인 URL 요청
    const response = await axios.get('http://localhost:8000/api/auth/steam/url/');
    
    // 받아온 주소로 브라우저 이동 (스팀 사이트로 이동됨)
    if (response.data.url) {
      window.location.href = response.data.url;
    }
  } catch (error) {
    console.error("스팀 로그인 주소 가져오기 실패:", error);
    alert("서버와 연결 불가능!! 백엔드가 켜져 있는지 확인해주세요.");
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

/* 레이아웃 */
.layout-wrapper {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* 네비게이션 바 스타일 */
.navbar {
  width: 100%;
  height: 60px;
  border-bottom: 1px solid #eaeaea; /* 하단에 얇은 회색 선 */
  background-color: #ffffff;
  display: flex;
  align-items: center;
  position: sticky; /* 스크롤 내려도 상단 고정 */
  top: 0;
  z-index: 1000;
}

.navbar-container {
  width: 100%;
  max-width: 1200px; /* 컨텐츠 최대 너비 제한 */
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  justify-content: space-between; /* 로고와 메뉴 양 끝 배치 */
  align-items: center;
}

/* 로고 스타일 */
.logo {
  font-size: 1.25rem;
  font-weight: 700;
  color: #333;
  text-decoration: none;
  letter-spacing: -0.5px;
}

/* 우측 메뉴 영역 */
.nav-right {
  display: flex;
  align-items: center;
  gap: 16px; /* 요소 사이 간격 */
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

/* 버튼 공통 스타일 (플랫하고 깔끔하게) */
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

/* 주요 버튼 (Vue Green) */
.btn-primary {
  background-color: #42b883;
  color: white;
}

.btn-primary:hover {
  background-color: #3aa876;
}

/* 텍스트 버튼 (로그아웃 등 - 배경 없음) */
.btn-text {
  background-color: transparent;
  color: #666;
}

.btn-text:hover {
  background-color: #f5f5f5;
  color: #333;
}

/* 메인 컨텐츠 영역 */
.main-content {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
  box-sizing: border-box;
}
</style>