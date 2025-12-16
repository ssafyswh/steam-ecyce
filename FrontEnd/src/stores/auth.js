// stores/auth.js
import { defineStore } from 'pinia';
import axios from 'axios';
import { ref } from 'vue';

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null);
  const isAuthenticated = ref(false);

  // 앱 시작 시 실행
  const initialize = async () => {
    // 로컬 스토리지에 '로그인 표시'가 없으면 아예 요청을 안 보냄
    const flag = localStorage.getItem('isLoggedIn');
    if (!flag) {
      console.log("ℹ️ 로그인 이력이 없어 서버 요청을 건너뜁니다.");
      return; 
    }

    try {
      await fetchUser();
    } catch (e) {
      // 혹시라도 토큰이 만료됐다면 표시를 지워줌
      localStorage.removeItem('isLoggedIn');
    }
  };

  // 내 정보 가져오기
  const fetchUser = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/auth/user/me/');
      user.value = response.data;
      isAuthenticated.value = true;
      
      // 로그인 성공했으면 확실하게 표시 남기기
      localStorage.setItem('isLoggedIn', 'yes');
      
    } catch (error) {
      user.value = null;
      isAuthenticated.value = false;
      localStorage.removeItem('isLoggedIn');
      throw error;
    }
  };

  // 스팀 로그인 검증
  const verifySteamLogin = async (queryData) => {
    try {
      await axios.post('http://localhost:8000/api/auth/steam/verify/', queryData);
      
      // 로그인 성공 표시 남기기
      localStorage.setItem('isLoggedIn', 'yes');
      
      // 정보 가져오기
      await fetchUser();
      
    } catch (error) {
      console.error("❌ 스팀 로그인 검증 실패:", error);
      throw error;
    }
  };

  // 4. 로그아웃
  const logout = async () => {
    try {
      await axios.post('http://localhost:8000/api/auth/logout/');
    } catch (error) {
      console.error("로그아웃 에러:", error);
    } finally {
      user.value = null;
      isAuthenticated.value = false;
      
      localStorage.removeItem('isLoggedIn');
      
      location.reload(); 
    }
  };

  return { user, isAuthenticated, initialize, fetchUser, verifySteamLogin, logout };
});