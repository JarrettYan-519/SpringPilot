import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import client from '@/api/client'

export const useSettingsStore = defineStore('settings', () => {
  const configs = ref({})

  async function loadAll() {
    const data = await client.get('/settings')
    configs.value = data.configs
  }

  async function set(key, value) {
    await client.put(`/settings/${key}`, { value })
    configs.value[key] = value
  }

  const heightCm = computed(() => configs.value['height_cm'] ? Number(configs.value['height_cm']) : null)
  const targetWeightKg = computed(() => configs.value['target_weight_kg'] ? Number(configs.value['target_weight_kg']) : null)

  return { configs, loadAll, set, heightCm, targetWeightKg }
})
