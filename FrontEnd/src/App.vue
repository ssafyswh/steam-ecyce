<!-- App.vue -->
<template>
  <div class="layout-wrapper">
    <header class="navbar">
      <div class="navbar-container">
        <router-link to="/" class="logo">Steam Ecyce</router-link>

        <div class="nav-right">
          <!-- 조건을 'isAuthenticated' 하나만 봄 -->
          <div v-if="authStore.isAuthenticated" class="user-actions">
            
            <!-- 닉네임 부분: user 데이터가 로딩되면 표시 -->
            <span class="welcome-msg">
              <b v-if="authStore.user">{{ authStore.user.nickname }}</b>
              <!-- 데이터 로딩 중일 때 닉네임 자리에 보여줄 것 (선택사항) -->
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
    // 1. Django에서 URL 받아오기
    const response = await axios.get('http://localhost:8000/api/auth/steam/url/');
    
    if (response.data.url) {
      // 2. 팝업 열기
      const width = 800;
      const height = 600;
      const left = window.screenX + (window.outerWidth - width) / 2;
      const top = window.screenY + (window.outerHeight - height) / 2;

      const popup = window.open(
        response.data.url,
        'SteamLogin',
        `width=${width},height=${height},left=${left},top=${top},resizable=yes,scrollbars=yes`
      );

      // 3. 팝업으로부터 메시지 수신 대기 (일회성 리스너)
      window.addEventListener('message', async function onMessage(event) {
        // 보안: 우리 사이트에서 온 메시지인지 확인 (포트번호까지 일치해야 함)
        if (event.origin !== window.location.origin) return;

        // 4. "로그인 성공" 메시지를 받으면
        if (event.data === 'steam-login-success') {
          console.log("팝업에서 로그인 성공 신호 수신!");
          
          // 이벤트 리스너 제거 (중복 실행 방지)
          window.removeEventListener('message', onMessage);
          
          // 유저 정보 갱신 (쿠키는 브라우저가 이미 공유하고 있음)
          await authStore.initialize(); 
          
          // 필요하다면 프로필 페이지로 이동
          // router.push('/profile'); 
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

html {
  /* 스크롤바가 있든 없든 공간을 확보하여 레이아웃 밀림 방지 */
  scrollbar-gutter: stable;
}
</style>