<!-- LoginView.vue -->
<template>
  <div class="login-container">
    <h2>로그인</h2>
    <p>아래 버튼을 눌러 스팀 계정으로 로그인하세요.</p>
    
    <button @click="handleSteamLogin" class="steam-btn">
      <img src="https://community.akamai.steamstatic.com/public/images/signinthroughsteam/sits_01.png" alt="Steam Login">
    </button>
  </div>
</template>

<script setup>
import axios from 'axios';

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

<style scoped>
.login-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 80vh;
  text-align: center;
}
.steam-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  margin-top: 20px;
}
.steam-btn:hover {
  opacity: 0.8;
}
</style>