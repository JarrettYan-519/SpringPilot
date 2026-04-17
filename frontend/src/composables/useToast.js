import { useNotificationsStore } from '@/stores/notifications'

export function useToast() {
  const store = useNotificationsStore()
  return {
    success: (message, title = '') => store.push({ variant: 'success', title, message }),
    error: (message, title = '出错了') => store.push({ variant: 'error', title, message, duration: 6000 }),
    warning: (message, title = '') => store.push({ variant: 'warning', title, message }),
    info: (message, title = '') => store.push({ variant: 'info', title, message }),
  }
}
