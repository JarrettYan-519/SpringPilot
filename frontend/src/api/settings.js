import client from './client'

export const settingsApi = {
  getAll: () => client.get('/settings'),
  get: (key) => client.get(`/settings/${key}`),
  set: (key, value) => client.put(`/settings/${key}`, { value }),
}
