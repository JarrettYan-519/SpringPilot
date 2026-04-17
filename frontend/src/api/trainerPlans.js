import client from './client'

export const trainerPlansApi = {
  list: () => client.get('/trainer-plans'),
  upload: (file, title, planDateRange = null) => {
    const form = new FormData()
    form.append('file', file)
    form.append('title', title)
    if (planDateRange) form.append('plan_date_range', planDateRange)
    return client.post('/trainer-plans', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  remove: (id) => client.delete(`/trainer-plans/${id}`),
}
