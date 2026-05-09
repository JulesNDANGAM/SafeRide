const BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

async function jsonFetch(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
  })
  const text = await res.text()
  const data = text ? (() => { try { return JSON.parse(text) } catch { return {} } })() : {}
  if (!res.ok) throw new Error(data.detail || `Request failed (${res.status})`)
  return data
}

function authHeaders(token) {
  return token ? { Authorization: `Bearer ${token}` } : {}
}

export const api = {
  cities: () => jsonFetch('/cities'),
  drivers: (city) => jsonFetch(`/drivers?city=${encodeURIComponent(city)}`),
  explainDriver: (driverId, city) =>
    jsonFetch(`/drivers/${driverId}/explain?city=${encodeURIComponent(city)}`, { method: 'POST' }),
  aiStatus: () => jsonFetch('/ai/status'),
  requestRide: (payload) => jsonFetch('/rides/request', { method: 'POST', body: JSON.stringify(payload) }),
  startRide: (payload) => jsonFetch('/rides/start', { method: 'POST', body: JSON.stringify(payload) }),
  monitor: (rideId, payload) => jsonFetch(`/rides/${rideId}/monitor`, { method: 'POST', body: JSON.stringify(payload) }),
  complete: (rideId) => jsonFetch(`/rides/${rideId}/complete`, { method: 'POST' }),

  // Subscriptions (public)
  plans: () => jsonFetch('/subscriptions/plans'),
  createSubscription: (payload) =>
    jsonFetch('/subscriptions', { method: 'POST', body: JSON.stringify(payload) }),
  getSubscription: (id) => jsonFetch(`/subscriptions/${id}`),
  simulatePayment: (id) =>
    jsonFetch(`/subscriptions/${id}/simulate-payment`, { method: 'POST' }),

  // Admin (protected)
  admin: {
    login: (token) => jsonFetch('/admin/login', { headers: authHeaders(token) }),
    drivers: (token) => jsonFetch('/admin/drivers', { headers: authHeaders(token) }),
    createDriver: (token, payload) =>
      jsonFetch('/admin/drivers', { method: 'POST', headers: authHeaders(token), body: JSON.stringify(payload) }),
    updateDriver: (token, id, payload) =>
      jsonFetch(`/admin/drivers/${id}`, { method: 'PUT', headers: authHeaders(token), body: JSON.stringify(payload) }),
    deleteDriver: (token, id) =>
      jsonFetch(`/admin/drivers/${id}`, { method: 'DELETE', headers: authHeaders(token) }),
    rides: (token) => jsonFetch('/admin/rides', { headers: authHeaders(token) }),
    subscriptions: (token) => jsonFetch('/admin/subscriptions', { headers: authHeaders(token) }),
    cancelSubscription: (token, id) =>
      jsonFetch(`/admin/subscriptions/${id}/cancel`, { method: 'POST', headers: authHeaders(token) }),
    stats: (token) => jsonFetch('/admin/stats', { headers: authHeaders(token) }),
  },
}
