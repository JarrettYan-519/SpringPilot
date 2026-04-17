import client from './client'

export const applicationsApi = {
  list: (statusFilter = null) => {
    const params = statusFilter ? { status_filter: statusFilter } : {}
    return client.get('/applications', { params })
  },
  get: (id) => client.get(`/applications/${id}`),
  create: (payload) => client.post('/applications', payload),
  update: (id, payload) => client.patch(`/applications/${id}`, payload),
  remove: (id) => client.delete(`/applications/${id}`),
  updateStatus: (id, newStatus, note = null) =>
    client.post(`/applications/${id}/status`, { new_status: newStatus, note }),
}
