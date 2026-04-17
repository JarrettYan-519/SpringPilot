import { defineStore } from 'pinia'
import { ref } from 'vue'

let nextId = 0

export const useNotificationsStore = defineStore('notifications', () => {
  const items = ref([])

  function push({ variant = 'info', title = '', message, duration = 4000 }) {
    const id = ++nextId
    items.value.push({ id, variant, title, message })
    if (duration > 0) {
      setTimeout(() => dismiss(id), duration)
    }
    return id
  }

  function dismiss(id) {
    const index = items.value.findIndex(t => t.id === id)
    if (index !== -1) items.value.splice(index, 1)
  }

  function clear() {
    items.value = []
  }

  return { items, push, dismiss, clear }
})
