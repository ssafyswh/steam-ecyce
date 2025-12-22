<template>
  <div style="text-align: center; margin-top: 50px;">
    <h2>🔄 로그인 처리 중...</h2>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

onMounted(async () => {
  try {
    const steamData = route.query;
    
    // 스토어를 통해 백엔드 검증 요청
    await authStore.verifySteamLogin(steamData);

    console.log("로그인 성공!");

    // 팝업으로 열렸는지 확인 (window.opener가 있으면 팝업임)
    if (window.opener) {
      // postMessage(메시지, 타겟오리진) -> 보안을 위해 오리진 지정 필수
      window.opener.postMessage('steam-login-success', window.location.origin);
      
      // 팝업 닫기
      window.close();
    } else {
      // 팝업이 아니라 그냥 주소쳐서 들어왔거나 리다이렉트 된 경우 -> 메인으로 이동
      router.push('/');
    }

  } catch (error) {
    console.error("로그인 실패:", error);
    alert("로그인 처리 중 오류가 발생했습니다.");
    
    // 에러 발생 시에도 팝업이면 닫아주는 게 깔끔함
    if (window.opener) {
      window.close();
    } else {
      router.push('/');
    }
  }
});
</script>