import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { settingsApi } from '@/api/settings'

export const LLM_PROVIDERS = ['openai', 'deepseek', 'claude', 'glm']
export const LLM_SCENARIOS = [
  { value: 'default', label: '默认（日常使用）' },
  { value: 'jd_analysis', label: 'JD 分析' },
  { value: 'interview_gen', label: '面试题生成' },
  { value: 'mock_interview', label: '模拟面试' },
  { value: 'diet', label: '饮食估算' },
]

export const useSettingsStore = defineStore('settings', () => {
  const configs = ref({})
  const loaded = ref(false)

  async function loadAll() {
    const data = await settingsApi.getAll()
    configs.value = data.configs || {}
    loaded.value = true
  }

  async function set(key, value) {
    await settingsApi.set(key, value)
    configs.value = { ...configs.value, [key]: value }
  }

  async function setMany(entries) {
    for (const [key, value] of entries) {
      await settingsApi.set(key, value)
    }
    configs.value = { ...configs.value, ...Object.fromEntries(entries) }
  }

  function get(key, fallback = '') {
    const v = configs.value[key]
    return v === undefined || v === null ? fallback : v
  }

  // LLM helpers
  function llmApiKey(provider) { return get(`llm_api_key_${provider}`) }
  function llmBaseUrl(provider) { return get(`llm_base_url_${provider}`) }
  function llmModel(provider)   { return get(`llm_model_${provider}`) }
  function llmProviderFor(scenario) { return get(`llm_provider_${scenario}`) }

  const hasAnyLlmKey = computed(() =>
    LLM_PROVIDERS.some(p => !!configs.value[`llm_api_key_${p}`])
  )

  // Profile helpers
  const heightCm       = computed(() => Number(get('height_cm'))       || null)
  const targetWeightKg = computed(() => Number(get('target_weight_kg'))|| null)
  const tdeeBase       = computed(() => Number(get('tdee_base'))       || null)

  return {
    configs, loaded,
    loadAll, set, setMany, get,
    llmApiKey, llmBaseUrl, llmModel, llmProviderFor,
    hasAnyLlmKey,
    heightCm, targetWeightKg, tdeeBase,
  }
})
