import api from './index'

export function getLocations() {
  return api.get('/locations/')
}

export function getLocationPhotos(id, page = 1) {
  return api.get(`/locations/${id}/photos/`, { params: { page } })
}
