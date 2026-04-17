import client from './client'

export const weightApi = {
  list: (limit = 90) => client.get('/weight', { params: { limit } }),
  create: (payload) => client.post('/weight', payload),
  remove: (id) => client.delete(`/weight/${id}`),
}

export const dietApi = {
  list: (day = null) => {
    const params = day ? { day } : {}
    return client.get('/diet', { params })
  },
  create: (payload) => client.post('/diet', payload),
  remove: (id) => client.delete(`/diet/${id}`),
}

export const trainingApi = {
  list: (limit = 30) => client.get('/training', { params: { limit } }),
  create: (payload) => client.post('/training', payload),
  update: (id, payload) => client.patch(`/training/${id}`, payload),
  remove: (id) => client.delete(`/training/${id}`),
}
