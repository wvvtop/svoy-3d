// src/api/client.js
import router from '@/router'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const apiClient = axios.create({
  baseURL: '/api', // благодаря proxy в vite.config.js
  timeout: 10000,
  // headers: {
  //   'Content-Type': 'application/json',
  // },
})

// Request interceptor — добавляем Bearer токен автоматически
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token && token !== 'undefined') {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error),
)

// Response interceptor — обработка ошибок 401 (токен устарел)
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const status = error.response?.status
    const url = error.config?.url || ''
    const isAuthEndpoint =
      url.includes('/auth/login') || url.includes('/auth/register')
    if (status === 401 && !isAuthEndpoint) {
      const authStore = useAuthStore()
      authStore.clearAuth()
      router.push({ name: "Login" })
    }

    return Promise.reject(error)
  },
)

export default apiClient
