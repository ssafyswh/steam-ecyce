// router/index.js
import { createRouter, createWebHistory } from 'vue-router'

import MainView from '@/views/MainView.vue'
import LoginView from '@/views/LoginView.vue'
import SteamCallback from '@/views/SteamCallback.vue'
import GameDetailView from '@/views/GameDetailView.vue'
import GameTotalView from '@/views/GameTotalView.vue'
import SearchResultsView from '@/views/SearchResultsView.vue'
import LibraryView from '@/views/LibraryView.vue'
import MyPageView from '@/views/MyPageView.vue'
import RecommendView from '@/views/RecommendView.vue'
import WorldcupView from '@/views/WorldcupView.vue'
import CommunityView from '@/views/CommunityView.vue'
import ArticleCreate from '@/views/ArticleCreate.vue'
import ArticleDetail from '@/views/ArticleDetail.vue'
import ArticleUpdate from '@/views/ArticleUpdate.vue'
import UserRecommendCreate from '@/views/UserRecommendCreate.vue'
import UserRecommendDetail from '@/views/UserRecommendDetail.vue'

const routes = [
  // 메인 및 인증
  { path: '/', name: 'main', component: MainView },
  { path: '/login', name: 'login', component: LoginView },
  { path: '/auth/callback', name: 'SteamCallback', component: SteamCallback },

  // 게임 관련
  { path: '/gametotal', name: 'GameTotalView', component: GameTotalView },
  { path: '/game/:id', name: 'GameDetail', component: GameDetailView, props: true },
  { path: '/search', name: 'search-results', component: SearchResultsView },
  { path: '/library', name: 'library', component: LibraryView },

  // 사용자 특화 기능
  { path: '/mypage', name: 'mypage', component: MyPageView },
  { path: '/recommend', name: 'recommend', component: RecommendView },
  { path: '/worldcup', name: 'worldcup', component: WorldcupView },

  // 커뮤니티 (일반 게시글)
  { path: '/community', name: 'community', component: CommunityView },
  { path: '/community/create', name: 'ArticleCreate', component: ArticleCreate },
  { path: '/community/:id', name: 'ArticleDetail', component: ArticleDetail, props: true },
  { path: '/community/update/:id', name: 'ArticleUpdate', component: ArticleUpdate },

  // 커뮤니티 (유저 리뷰/추천)
  { path: '/community/review/:gameId/create', name: 'UserRecommendCreate', component: UserRecommendCreate, props: true },
  { path: '/community/review/:reviewId', name: 'UserRecommendDetail', component: UserRecommendDetail, props: true },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router