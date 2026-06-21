import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as apiLogin, register as apiRegister, getCurrentUser, logout as apiLogout } from '@/api'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || '')
  const isLoggedIn = computed(() => !!token.value)

  const setToken = (newToken) => {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  const clearToken = () => {
    token.value = ''
    localStorage.removeItem('token')
  }

  const login = async (credentials) => {
    try {
      const response = await apiLogin(credentials)
      setToken(response.data.access_token)
      await fetchUser()
      return response
    } catch (error) {
      throw error
    }
  }

  const register = async (userData) => {
    return await apiRegister(userData)
  }

  const fetchUser = async () => {
    if (!token.value) return
    try {
      const response = await getCurrentUser()
      user.value = response.data
    } catch (error) {
      clearToken()
      throw error
    }
  }

  const logout = () => {
    try { apiLogout() } catch (e) { console.error("Logout error:", e) }
    clearToken()
    user.value = null
  }

  const updateUser = (userData) => {
    user.value = { ...user.value, ...userData }
  }

  return { user, token, isLoggedIn, login, register, fetchUser, logout, updateUser, setToken, clearToken }
})
