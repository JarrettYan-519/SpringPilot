import { ref } from 'vue'
import { useToast } from './useToast'

/**
 * Wraps an async operation with loading + error state and automatic error toast.
 * Usage:
 *   const { loading, error, run } = useAsync()
 *   await run(() => applicationsApi.list())
 */
export function useAsync({ silent = false } = {}) {
  const loading = ref(false)
  const error = ref(null)
  const toast = useToast()

  async function run(fn) {
    loading.value = true
    error.value = null
    try {
      return await fn()
    } catch (err) {
      error.value = err
      if (!silent) toast.error(err.message || '请求失败')
      throw err
    } finally {
      loading.value = false
    }
  }

  return { loading, error, run }
}
