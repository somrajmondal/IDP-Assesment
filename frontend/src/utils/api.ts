import axios from 'axios'

export const api = axios.create({
  baseURL: '/api',
  timeout: 120000,
})

// Document Types
export const documentTypesApi = {
  list: () => api.get('/admin/document-types'),
  get: (id: number) => api.get(`/admin/document-types/${id}`),
  create: (data: any) => api.post('/admin/document-types', data),
  update: (id: number, data: any) => api.put(`/admin/document-types/${id}`, data),
  delete: (id: number) => api.delete(`/admin/document-types/${id}`),
  seed: () => api.post('/admin/seed'),
}

// Templates
export const templatesApi = {
  list: (documentTypeId?: number) => api.get('/templates/', { params: { document_type_id: documentTypeId } }),
  get: (id: number) => api.get(`/templates/${id}`),
  create: (data: any) => api.post('/templates/', data),
  update: (id: number, data: any) => api.put(`/templates/${id}`, data),
  delete: (id: number) => api.delete(`/templates/${id}`),
  getJson: (id: number) => api.get(`/templates/${id}/json-preview`),
  getAllJson: () => api.get('/templates/json-preview/all'),
  uploadSample: (id: number, file: File) => {
    const fd = new FormData()
    fd.append('file', file)
    return api.post(`/templates/${id}/upload-sample`, fd)
  },
  addEntity: (templateId: number, data: any) => api.post(`/templates/${templateId}/entities`, data),
  updateEntity: (entityId: number, data: any) => api.put(`/templates/entities/${entityId}`, data),
  deleteEntity: (entityId: number) => api.delete(`/templates/entities/${entityId}`),
}

// Folders
export const foldersApi = {
  list: () => api.get('/folders/'),
  get: (id: number) => api.get(`/folders/${id}`),
  create: (data: any) => api.post('/folders/', data),
  update: (id: number, data: any) => api.put(`/folders/${id}`, data),
  delete: (id: number) => api.delete(`/folders/${id}`),
  uploadFiles: (folderId: number, files: File[]) => {
    const fd = new FormData()
    files.forEach(f => fd.append('files', f))
    return api.post(`/folders/${folderId}/upload`, fd, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  downloadZip: (folderId: number) => `/api/folders/${folderId}/download-zip`,
}

// Process
export const processApi = {
  start: (data: any) => api.post('/process/', data),
  getResults: (folderId: number) => api.get(`/process/folder/${folderId}/results`),
  downloadJson: (folderId: number) => `/api/process/folder/${folderId}/download-json`,
}

// Documents
export const documentsApi = {
  get: (id: number) => api.get(`/documents/${id}`),
  getExtractions: (id: number) => api.get(`/documents/${id}/extractions`),
}
