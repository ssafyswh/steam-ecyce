// router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import SteamCallback from '../views/SteamCallback.vue'
// import ProfileView from '@/views/ProfileView.vue'
import RecommendView from '@/views/RecommendView.vue'
import GameDetailView from '@/views/GameDetailView.vue'
import MainView from '@/views/MainView.vue'
import SearchResultsView from '@/views/SearchResultsView.vue'
import GameInfoView from '@/views/GameInfoView.vue'
import WorldcupView from '@/views/WorldcupView.vue'
import CommunityView from '@/views/CommunityView.vue'
import ArticleCreate from '@/views/ArticleCreate.vue'
import ArticleDetail from '@/views/ArticleDetail.vue'
import ArticleUpdate from '@/views/ArticleUpdate.vue'
import LibraryView from '@/views/LibraryView.vue' // 기존 ProfileView의 이름을 변경했다고 가정
import MyPageView from '@/views/MyPageView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/auth/callback',
      name: 'SteamCallback',
      component: SteamCallback
    },
    {
      path: '/game/:id',
      name: 'GameDetail',
      component: GameDetailView,
      props: true
    },
    // {
    //   path: '/profile',
    //   name: 'profile',
    //   component: ProfileView,
    // },
    {
      path: '/library', // 라이브러리 전용 경로
      name: 'library',
      component: LibraryView,
    },
    {
      path: '/mypage',  // 마이페이지(AI/최애게임) 전용 경로
      name: 'mypage',
      component: MyPageView,
    },
    {
      path: '/recommend',
      name: 'recommend',
      component: RecommendView
    },
    {
      path: '/gameinfo',
      name: 'gameinfo',
      component: GameInfoView
    },
    {
      path: '/worldcup',
      name: 'worldcup',
      component: WorldcupView
    },
    {
      path: '/search',
      name: 'search-results',
      component: SearchResultsView
    },
    {
      path: '/community',
      name: 'community',
      component: CommunityView
    },
    {
      path: '/community/create',
      name: 'ArticleCreate',
      component: ArticleCreate
    },
    {
      path: '/community/:id',
      name: 'ArticleDetail',
      component: ArticleDetail,
      props: true
    },
    {
      path: '/community/update/:id',
      name: 'ArticleUpdate',
      component: ArticleUpdate,
    },
    {
      path: '',
      name: 'main',
      component: MainView
    },
  ],
})

export default router
