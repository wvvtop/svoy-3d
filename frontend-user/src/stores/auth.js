// src/stores/auth.js
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authApi } from '@/api/auth'
import { getErrorMessage } from '@/utils/getErrorMessage'


export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || null)
  const userEmail = ref(null)
  const isLoading = ref(false)
  const error = ref(null)

  const register = async (email, password) => {
    isLoading.value = true
    error.value = null
    try {
      const response = await authApi.register({ email, password })
      token.value = response.data.access_token
      localStorage.setItem('token', token.value)
      userEmail.value = email
      return true
    } catch (err) {

      error.value = err.response?.data?.error || 'Ошибка регистрации'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const login = async (email, password) => {
    isLoading.value = true
    error.value = null
    try {
      const response = await authApi.login({ email, password })
      token.value = response.data.access_token
      localStorage.setItem('token', token.value)
      userEmail.value = email
      return true
    } catch (err) {
      console.log(err.response?.data)
      error.value = getErrorMessage(err, 'Неверный email или пароль')
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const logout = () => {
    token.value = null
    userEmail.value = null
    localStorage.removeItem('token')
    window.location.href = '/login'
  }

  const initializeAuth = () => {
    const savedToken = localStorage.getItem('token')

    if (savedToken) {
      token.value = savedToken

      try {
        const payload = JSON.parse(atob(savedToken.split('.')[1]))
        userEmail.value = payload.sub || payload.email
      } catch (e) {
        console.log('Не удалось получить email' + e)
        userEmail.value = null
      }
    }
  }

  const isAuthenticated = () => !!token.value

  return {
    token,
    userEmail,
    isLoading,
    error,
    register,
    login,
    logout,
    isAuthenticated,
    initializeAuth,
  }
})
