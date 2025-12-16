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
    await authStore.verifySteamLogin(steamData);

    console.log("로그인 성공! 메인으로 이동합니다.");
    router.push('/');

  } catch (error) {
    console.error("로그인 실패:", error);
    alert("로그인 처리 중 오류가 발생했습니다.");
    router.push('/');
  }
});
</script>