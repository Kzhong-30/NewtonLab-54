import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      if (!window.location.pathname.startsWith('/login')) {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export const login = (data) => api.post('/auth/login', data)
export const register = (data) => api.post('/auth/register', data)
export const getCurrentUser = () => api.get('/auth/me')
export const logout = () => api.post('/auth/logout')

export const getScripts = (params) => api.get('/scripts', { params })
export const getScript = (id) => api.get(`/scripts/${id}`)
export const createScript = (data) => api.post('/scripts', data)
export const updateScript = (id, data) => api.put(`/scripts/${id}`, data)
export const deleteScript = (id) => api.delete(`/scripts/${id}`)

export const getGames = (params) => api.get('/games', { params })
export const getGame = (id) => api.get(`/games/${id}`)
export const createGame = (data) => api.post('/games', data)
export const joinGame = (id) => api.post(`/games/${id}/join`)
export const leaveGame = (id) => api.post(`/games/${id}/leave`)

export const getPosts = (params) => api.get('/posts', { params })
export const getPost = (id) => api.get(`/posts/${id}`)
export const createPost = (data) => api.post('/posts', data)
export const updatePost = (id, data) => api.put(`/posts/${id}`, data)
export const deletePost = (id) => api.delete(`/posts/${id}`)

export const getComments = (postId) => api.get(`/posts/${postId}/comments`)
export const createComment = (postId, data) => api.post(`/posts/${postId}/comments`, data)
export const deleteComment = (id) => api.delete(`/comments/${id}`)

export const updateProfile = (data) => api.put('/users/profile', data)
export const changePassword = (data) => api.post('/users/change-password', data)

export default api
