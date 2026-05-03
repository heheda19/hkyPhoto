import api from './index'

export function login(username, password) {
  return api.post('/auth/login/', { username, password })
}
