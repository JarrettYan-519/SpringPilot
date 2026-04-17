import client from './client'

export const studyTasksApi = {
  list: (completed = null) => {
    const params = completed === null ? {} : { completed }
    return client.get('/study-tasks', { params })
  },
  create: (payload) => client.post('/study-tasks', payload),
  update: (id, payload) => client.patch(`/study-tasks/${id}`, payload),
  remove: (id) => client.delete(`/study-tasks/${id}`),
}
