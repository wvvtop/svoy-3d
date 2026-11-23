import HomePage from '@/home/HomePage.vue'
import LoginPage from '@/login/LoginPage.vue'
import OrdersPageLayout from '@/order/OrdersPageLayout.vue'
import OrderPage from '@/order/pages/OrderPage.vue'
import OrdersActivePage from '@/order/pages/OrdersActivePage.vue'
import OrdersRevisionPage from '@/order/pages/OrdersRevisionPage.vue'
import ProfilePage from '@/profile/ProfilePage.vue'
import { useAuthStore } from '@/stores/auth'
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginPage,
    meta: { requiresGuest: true },
  },
  {
    path: '/profile',
    name: 'profile',
    component: ProfilePage,
    meta: { requiresAuth: true },
  },
  {
    path: '/order/:id',
    name: 'Order',
    component: OrderPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/orders',
    component: OrdersPageLayout,
    children: [
      { path: '', name: 'active-orders', component: OrdersActivePage },
      { path: 'revision', name: 'revision-orders', component: OrdersRevisionPage },
    ]
  }
]


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: routes,
})


router.beforeEach((to, from) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return { name: 'Login' }
  }

  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    return { name: 'Home' }   // или '/' , или '/dashboard'
  }

  // ничего не вернули → навигация разрешена
})

export default router
