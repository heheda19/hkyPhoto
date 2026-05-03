import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'home', component: () => import('@/views/HomeView.vue') },
  { path: '/albums', name: 'albums', component: () => import('@/views/AlbumListView.vue') },
  { path: '/albums/:id', name: 'album-detail', component: () => import('@/views/AlbumDetailView.vue') },
  { path: '/timeline', name: 'timeline', component: () => import('@/views/TimelineView.vue') },
  { path: '/locations', name: 'locations', component: () => import('@/views/LocationListView.vue') },
  { path: '/locations/:id', name: 'location-detail', component: () => import('@/views/LocationDetailView.vue') },
  { path: '/admin', name: 'admin', component: () => import('@/views/AdminView.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
