import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const auth = {
  login: (email, password) => {
    const formData = new FormData()
    formData.append('username', email)
    formData.append('password', password)
    return api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
  },
  register: (data) => api.post('/auth/register', data),
  me: () => api.get('/auth/me'),
}

export const dashboard = {
  getDashboard: () => api.get('/dashboard/'),
}

export const customers = {
  getAll: () => api.get('/customers/'),
  getById: (id) => api.get(`/customers/${id}`),
}

export const leaks = {
  getAll: (params) => api.get('/leaks/', { params }),
}

export const predictions = {
  getAll: () => api.get('/predictions/'),
  predictPayment: (customerId) => api.post(`/predictions/payment?customer_id=${customerId}`),
  predictChurn: (customerId) => api.post(`/predictions/churn?customer_id=${customerId}`),
  predictRefund: (customerId) => api.post(`/predictions/refund?customer_id=${customerId}`),
}

export const prevention = {
  getQueue: () => api.get('/prevention/'),
  createAction: (data) => api.post('/prevention/actions', data),
  getActions: (status) => api.get('/prevention/actions', { params: { status_filter: status } }),
}

export const recovery = {
  getStats: () => api.get('/recovery/'),
}

export const upload = {
  csv: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/upload/csv', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  demo: () => api.post('/upload/demo'),
}

export default api
