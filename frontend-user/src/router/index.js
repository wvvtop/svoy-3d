import HomePage from '@/home/HomePage.vue'
import OrdersListLayout from '@/layouts/OrdersListLayout.vue'
import LoginPage from '@/login/LoginPage.vue'
import CreateOrderPage from '@/order/CreateOrderPage.vue'
import OrderPage from '@/order/OrderPage.vue'
import OrdersActivePage from '@/order/OrdersActivePage.vue'
import OrdersBinPage from '@/order/OrdersBinPage.vue'
import OrdersCompletedPage from '@/order/OrdersCompletedPage.vue'
import OrdersPage from '@/order/OrdersPage.vue'
import ProfilePage from '@/profile/ProfilePage.vue'
import RegistrationPage from '@/registration/RegistrationPage.vue'
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
    path: '/registration',
    name: "Registration",
    component: RegistrationPage,
    meta: { requiresGuest: true }
  },
  {
    path: '/profile',
    name: "Profile",
    component: ProfilePage,
    meta: { requiresAuth: true }
  },
  {
    path: '/order/:slug',
    name: 'Order',
    component: OrderPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/orders/create',
    name: 'create-order',
    component: CreateOrderPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/orders',
    component: OrdersListLayout,
    children: [
      { path: '', name: 'orders', component: OrdersActivePage },
      { path: 'cart', name: 'orders-bin', component: OrdersBinPage},
      { path: 'completed', name: 'completed-orders', component: OrdersCompletedPage},
      // { path: 'cart',    name: 'cart',             component: CartPage },
      // { path: 'completed', name: 'completed-orders', component: CompletedOrdersPage },
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
