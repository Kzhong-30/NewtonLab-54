import { createRouter, createWebHistory } from 'vue-router'
import { ElMessage } from 'element-plus'

import { useUserStore } from '@/store'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { title: '首页' }
  },
  {
    path: '/scripts',
    name: 'Scripts',
    component: () => import('@/views/ScriptList.vue'),
    meta: { title: '剧本库' }
  },
  {
    path: '/scripts/:id',
    name: 'ScriptDetail',
    component: () => import('@/views/ScriptDetail.vue'),
    meta: { title: '剧本详情' }
  },
  {
    path: '/games',
    name: 'Games',
    component: () => import('@/views/GameList.vue'),
    meta: { title: '组局' }
  },
  {
    path: '/games/create',
    name: 'GameCreate',
    component: () => import('@/views/GameCreate.vue'),
    meta: { title: '发布组局', requiresAuth: true }
  },
  {
    path: '/games/:id',
    name: 'GameDetail',
    component: () => import('@/views/GameDetail.vue'),
    meta: { title: '组局详情' }
  },
  {
    path: '/community',
    name: 'Community',
    component: () => import('@/views/Community.vue'),
    meta: { title: '社区' }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile.vue'),
    meta: { title: '个人中心', requiresAuth: true }
  },
  {
    path: '/dm-admin',
    name: 'DMAdmin',
    component: () => import('@/views/DMAdmin.vue'),
    meta: { title: 'DM管理中心', requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { title: '注册' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    return { top: 0 }
  }
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  if (to.meta.title) document.title = `${to.meta.title} - 剧本杀`
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    next({ path: '/login', query: { redirect: to.fullPath } })
  } else {
    next()
  }
})

export default router
