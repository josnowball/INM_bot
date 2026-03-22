const API_BASE = '/api'

function getToken() {
  return localStorage.getItem('token')
}

function setTokens(access, refresh) {
  localStorage.setItem('token', access)
  localStorage.setItem('refresh_token', refresh)
}

function clearTokens() {
  localStorage.removeItem('token')
  localStorage.removeItem('refresh_token')
}

async function request(path, options = {}) {
  const token = getToken()
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  })

  if (res.status === 401) {
    clearTokens()
    window.location.href = '/login'
    throw new Error('Session expired')
  }

  const data = await res.json()
  if (!res.ok) {
    throw new Error(data.detail || 'Request failed')
  }
  return data
}

// Auth
export async function register(email, password, fullName) {
  const data = await request('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, password, full_name: fullName }),
  })
  setTokens(data.access_token, data.refresh_token)
  return data
}

export async function login(email, password) {
  const data = await request('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })
  setTokens(data.access_token, data.refresh_token)
  return data
}

export function logout() {
  clearTokens()
  window.location.href = '/'
}

export function isLoggedIn() {
  return !!getToken()
}

export async function getMe() {
  return request('/auth/me')
}

export async function verifyEmail(code) {
  return request('/auth/verify-email', {
    method: 'POST',
    body: JSON.stringify({ code }),
  })
}

export async function resendVerification() {
  return request('/auth/resend-verification', { method: 'POST' })
}

// Profile
export async function getProfile() {
  return request('/profile/')
}

export async function updateProfile(data) {
  return request('/profile/', {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

// Appointments
export async function getINMProcedures() {
  return request('/appointments/inm/procedures')
}

export async function getINMOffices() {
  return request('/appointments/inm/offices')
}

export async function getSolicitudFields(procedureType) {
  return request(`/appointments/inm/solicitud-fields/${procedureType}`)
}

export async function bookINM(data) {
  return request('/appointments/inm/book', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function getSREProcedures() {
  return request('/appointments/sre/procedures')
}

export async function getSREOffices() {
  return request('/appointments/sre/offices')
}

export async function bookSRE(data) {
  return request('/appointments/sre/book', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function getAppointments() {
  return request('/appointments/')
}

export async function getAppointment(id) {
  return request(`/appointments/${id}`)
}
