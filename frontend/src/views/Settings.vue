<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useSettingsStore, LLM_PROVIDERS, LLM_SCENARIOS } from '@/stores/settings'
import { useAsync } from '@/composables/useAsync'
import { useToast } from '@/composables/useToast'
import AppPageHeader from '@/components/ui/AppPageHeader.vue'
import AppCard from '@/components/ui/AppCard.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppSelect from '@/components/ui/AppSelect.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppTabs from '@/components/ui/AppTabs.vue'

const store = useSettingsStore()
const toast = useToast()
const { loading, run } = useAsync()

const providerMeta = {
  openai:   { label: 'OpenAI',   defaultModel: 'gpt-4o-mini',    defaultBase: '' },
  deepseek: { label: 'DeepSeek', defaultModel: 'deepseek-chat',  defaultBase: 'https://api.deepseek.com/v1' },
  claude:   { label: 'Claude',   defaultModel: 'claude-sonnet-4-6', defaultBase: '' },
  glm:      { label: '智谱 GLM', defaultModel: 'glm-4-flash',    defaultBase: '' },
}

const activeTab = ref('llm')
const tabs = [
  { value: 'llm',     label: 'AI 模型' },
  { value: 'routing', label: '场景路由' },
  { value: 'profile', label: '个人档案' },
  { value: 'mineru',  label: '文档解析' },
  { value: 'export',  label: '数据导出' },
]

// Editable form — mirrors store.configs but flushed on Save click per section
const form = reactive({
  llm: {
    openai:   { key: '', base: '', model: '' },
    deepseek: { key: '', base: '', model: '' },
    claude:   { key: '', base: '', model: '' },
    glm:      { key: '', base: '', model: '' },
  },
  routing: { default: '', jd_analysis: '', interview_gen: '', mock_interview: '', diet: '' },
  profile: { height_cm: '', target_weight_kg: '', tdee_base: '' },
  mineru_api_key: '',
})

function loadFormFromStore() {
  for (const p of LLM_PROVIDERS) {
    form.llm[p].key   = store.get(`llm_api_key_${p}`)
    form.llm[p].base  = store.get(`llm_base_url_${p}`)
    form.llm[p].model = store.get(`llm_model_${p}`)
  }
  for (const s of LLM_SCENARIOS) {
    form.routing[s.value] = store.get(`llm_provider_${s.value}`)
  }
  form.profile.height_cm        = store.get('height_cm')
  form.profile.target_weight_kg = store.get('target_weight_kg')
  form.profile.tdee_base        = store.get('tdee_base')
  form.mineru_api_key           = store.get('mineru_api_key')
}

onMounted(async () => {
  await run(() => store.loadAll())
  loadFormFromStore()
})

const providerOptions = computed(() => [
  { value: '', label: '（未指定）' },
  ...LLM_PROVIDERS.map(p => ({ value: p, label: providerMeta[p].label })),
])

async function saveLlmProvider(provider) {
  const p = form.llm[provider]
  await run(() => store.setMany([
    [`llm_api_key_${provider}`,  p.key],
    [`llm_base_url_${provider}`, p.base],
    [`llm_model_${provider}`,    p.model],
  ]))
  toast.success(`${providerMeta[provider].label} 配置已保存`)
}

async function saveRouting() {
  const entries = LLM_SCENARIOS.map(s => [`llm_provider_${s.value}`, form.routing[s.value]])
  await run(() => store.setMany(entries))
  toast.success('场景路由已保存')
}

async function saveProfile() {
  await run(() => store.setMany([
    ['height_cm',        form.profile.height_cm],
    ['target_weight_kg', form.profile.target_weight_kg],
    ['tdee_base',        form.profile.tdee_base],
  ]))
  toast.success('个人档案已保存')
}

async function saveMineru() {
  await run(() => store.set('mineru_api_key', form.mineru_api_key))
  toast.success('MinerU 配置已保存')
}

async function exportData() {
  await run(async () => {
    const [{ applicationsApi }, { studyTasksApi }, { weightApi, dietApi, trainingApi }, { trainerPlansApi }] = await Promise.all([
      import('@/api/applications'),
      import('@/api/studyTasks'),
      import('@/api/fitness'),
      import('@/api/trainerPlans'),
    ])
    const [applications, studyTasks, weight, diet, training, trainerPlans] = await Promise.all([
      applicationsApi.list(),
      studyTasksApi.list(),
      weightApi.list(9999),
      dietApi.list(),
      trainingApi.list(9999),
      trainerPlansApi.list(),
    ])
    const blob = new Blob(
      [JSON.stringify({ exported_at: new Date().toISOString(), applications, studyTasks, weight, diet, training, trainerPlans, settings: store.configs }, null, 2)],
      { type: 'application/json' },
    )
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `springpilot-backup-${new Date().toISOString().slice(0, 10)}.json`
    a.click()
    URL.revokeObjectURL(url)
    toast.success('数据已导出')
  })
}

function configuredBadge(provider) {
  return !!store.get(`llm_api_key_${provider}`)
}
</script>

<template>
  <div>
    <AppPageHeader title="设置" subtitle="配置 AI 模型、个人档案与数据管理" />

    <AppTabs v-model="activeTab" :tabs="tabs" />

    <div class="settings-body">
      <!-- LLM providers -->
      <div v-if="activeTab === 'llm'" class="settings-grid">
        <AppCard v-for="p in LLM_PROVIDERS" :key="p">
          <template #header>
            <div class="provider-head">
              <div>
                <div class="card-title">{{ providerMeta[p].label }}</div>
                <div class="card-subtitle">{{ providerMeta[p].defaultBase || '使用默认端点' }}</div>
              </div>
              <AppBadge :variant="configuredBadge(p) ? 'success' : 'neutral'">
                {{ configuredBadge(p) ? '已配置' : '未配置' }}
              </AppBadge>
            </div>
          </template>
          <div class="form-stack">
            <AppInput v-model="form.llm[p].key" label="API Key" type="password" placeholder="sk-..." />
            <AppInput v-model="form.llm[p].base" label="Base URL（可选）" :placeholder="providerMeta[p].defaultBase || '默认'" />
            <AppInput v-model="form.llm[p].model" label="模型名称" :placeholder="providerMeta[p].defaultModel" />
            <div class="form-actions">
              <AppButton :loading="loading" @click="saveLlmProvider(p)">保存</AppButton>
            </div>
          </div>
        </AppCard>
      </div>

      <!-- Scenario routing -->
      <AppCard v-else-if="activeTab === 'routing'" title="场景路由" subtitle="为不同场景指定使用哪个模型提供商">
        <div class="form-stack">
          <AppSelect
            v-for="s in LLM_SCENARIOS"
            :key="s.value"
            :label="s.label"
            :model-value="form.routing[s.value]"
            :options="providerOptions"
            @update:model-value="v => form.routing[s.value] = v"
          />
          <div class="form-actions">
            <AppButton :loading="loading" @click="saveRouting">保存路由</AppButton>
          </div>
        </div>
      </AppCard>

      <!-- Profile -->
      <AppCard v-else-if="activeTab === 'profile'" title="个人档案" subtitle="用于健身模块的 TDEE 计算和目标追踪">
        <div class="form-grid-2">
          <AppInput v-model="form.profile.height_cm"        label="身高 (cm)"    type="number" placeholder="178" />
          <AppInput v-model="form.profile.target_weight_kg" label="目标体重 (kg)" type="number" placeholder="70" />
          <AppInput v-model="form.profile.tdee_base"        label="基础代谢 (kcal/天)" type="number" placeholder="1800" hint="留空将由 AI 估算" />
        </div>
        <div class="form-actions">
          <AppButton :loading="loading" @click="saveProfile">保存档案</AppButton>
        </div>
      </AppCard>

      <!-- MinerU -->
      <AppCard v-else-if="activeTab === 'mineru'" title="MinerU 文档解析" subtitle="用于解析教练给的 PDF / DOCX 训练计划">
        <div class="form-stack">
          <AppInput v-model="form.mineru_api_key" label="MinerU API Key" type="password" placeholder="从 mineru.net 申请" />
          <p class="hint">仅解析 PDF / DOCX 时需要；上传 .md 文件不需要此 Key。</p>
          <div class="form-actions">
            <AppButton :loading="loading" @click="saveMineru">保存</AppButton>
          </div>
        </div>
      </AppCard>

      <!-- Export -->
      <AppCard v-else-if="activeTab === 'export'" title="数据导出" subtitle="将全部投递、任务、健身数据以 JSON 格式下载">
        <p class="hint">导出内容包含所有投递记录、学习任务、体重/饮食/训练日志、训练计划元数据和设置。不包含上传的原始文件。</p>
        <div class="form-actions">
          <AppButton :loading="loading" @click="exportData">下载备份 JSON</AppButton>
        </div>
      </AppCard>
    </div>
  </div>
</template>

<style scoped>
.settings-body { margin-top: var(--space-5); display: flex; flex-direction: column; gap: var(--space-4); }
.settings-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: var(--space-4); }
.provider-head { display: flex; align-items: center; justify-content: space-between; gap: var(--space-3); width: 100%; }
.card-title { font-size: var(--text-md); font-weight: 600; }
.card-subtitle { font-size: var(--text-xs); color: var(--color-text-muted); margin-top: 2px; }
.form-stack { display: flex; flex-direction: column; gap: var(--space-3); }
.form-grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--space-3); margin-bottom: var(--space-4); }
.form-actions { display: flex; justify-content: flex-end; gap: var(--space-2); margin-top: var(--space-2); }
.hint { font-size: var(--text-sm); color: var(--color-text-muted); line-height: var(--leading-relaxed); }
</style>
