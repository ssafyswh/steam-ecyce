// router/indexedDB.js
import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue' 
import SteamCallback from '../views/SteamCallback.vue'
import ProfileView from '@/views/ProfileView.vue'
import RecommendView from '@/views/RecommendView.vue'
import GameDetailView from '@/views/GameDetailView.vue'
import MainView from '@/views/MainView.vue'
import SearchResultsView from '@/views/SearchResultsView.vue'

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
    {
      path: '/profile',
      name: 'profile',
      component: ProfileView,
    },
    {
      path: '/recommend',
      name: 'recommend',
      component: RecommendView
    },
    {
      path: '',
      name: 'main',
      component: MainView
    },
    {
      path: '/search',
      name: 'search-results',
      component: SearchResultsView
    },
  ],
})

export default router
