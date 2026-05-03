import api from './index'

export function getPhotos(params = {}) {
  return api.get('/photos/', { params })
}

export function getTimelinePhotos(page = 1) {
  return api.get('/photos/', { params: { ordering: '-taken_at', page } })
}

export function getPresignedUrl(filename, contentType) {
  return api.post('/photos/presigned_url/', { filename, content_type: contentType })
}

export function createPhoto(data) {
  return api.post('/photos/', data)
}

export function deletePhoto(id) {
  return api.delete(`/photos/${id}/`)
}
