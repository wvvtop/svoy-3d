// src/stores/auth.js
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { authApi } from '@/api/auth'
import { getErrorMessage } from '@/utils/getErrorMessage'

function decodeJwt(token) {
  if (!token) return null
  try {
    return JSON.parse(atob(token.split('.')[1]))
  } catch {
    return null
  }
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || null)
  const isLoading = ref(false)
  const error = ref(null)

  // Источник на будущее, когда бэк начнёт отдавать полный профиль
  // (GET /auth/me или user в ответе login/register).
  // Пока null — userId берётся из JWT.
  const user = ref(null)

  const jwtPayload = computed(() => decodeJwt(token.value))

  // Единая точка чтения id:
  //   1) user.id, если появится (после переделки бэка)
  //   2) sub из JWT — сейчас это id пользователя
  const userId = computed(() => {
    if (user.value?.id != null) {
      const id = Number(user.value.id)
      return Number.isFinite(id) ? id : null
    }
    const id = Number(jwtPayload.value?.sub)
    return Number.isFinite(id) ? id : null
  })

  const userEmail = computed(() => {
    if (user.value?.email) return user.value.email
    const email = jwtPayload.value?.email
    return typeof email === 'string' ? email : null
  })

  const register = async (email, password) => {
    isLoading.value = true
    error.value = null
    try {
      const response = await authApi.register({ email, password })
      token.value = response.data.access_token
      localStorage.setItem('token', token.value)
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
      return true
    } catch (err) {
      console.log(err.response?.data)
      error.value = getErrorMessage(err, 'Неверный email или пароль')
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const clearAuth = () => {
    token.value = null
    user.value = null
    error.value = null
    localStorage.removeItem('token')
  }

  const logout = () => {
    clearAuth()
    window.location.href = '/login'
  }

  const initializeAuth = () => {
    ////const savedToken = localStorage.getItem('token')
    ////if (!savedToken) return

    ////token.value = savedToken

    // Email есть в JWT только если бэк его туда положит.
    // Сейчас в payload только sub (id) — userEmail восстанавливать не из чего,
    // поэтому молча пропускаем.
    // const payload = decodeJwt(savedToken)
    // //if (payload?.email) {
    // //  userEmail.value = payload.email
    // //}

    // Когда появится /auth/me — раскомментировать:
    // initializeAuth станет async, а в main.js — await initializeAuth().
    // try {
    //   user.value = await authApi.me()
    //   if (user.value?.email) userEmail.value = user.value.email
    // } catch { /* ignore */ }
  }

  const isAuthenticated = computed(() => !!token.value)

  return {
    token,
    userEmail,
    user,          // новый: пригодится, когда бэк начнёт отдавать профиль
    userId,        // новый: computed
    isLoading,
    error,
    register,
    login,
    logout,
    isAuthenticated,
    initializeAuth,
    clearAuth,
  }
})
