import api from './index'

export function getAlbums() {
  return api.get('/albums/')
}

export function getAlbum(id) {
  return api.get(`/albums/${id}/`)
}

export function getAlbumPhotos(id, page = 1) {
  return api.get(`/albums/${id}/photos/`, { params: { page } })
}

export function createAlbum(data) {
  return api.post('/albums/', data)
}

export function updateAlbum(id, data) {
  return api.patch(`/albums/${id}/`, data)
}

export function deleteAlbum(id) {
  return api.delete(`/albums/${id}/`)
}
