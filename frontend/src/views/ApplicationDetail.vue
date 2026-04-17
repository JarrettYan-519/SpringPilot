<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { applicationsApi } from '@/api/applications'
import { aiApi } from '@/api/ai'
import { useSettingsStore } from '@/stores/settings'
import { useAsync } from '@/composables/useAsync'
import { useToast } from '@/composables/useToast'
import AppPageHeader from '@/components/ui/AppPageHeader.vue'
import AppCard from '@/components/ui/AppCard.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppTextarea from '@/components/ui/AppTextarea.vue'
import AppSelect from '@/components/ui/AppSelect.vue'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import StatusBadge from '@/components/StatusBadge.vue'

const route = useRoute()
const router = useRouter()
const toast = useToast()
const settings = useSettingsStore()
const { loading, run } = useAsync()

const appId = computed(() => Number(route.params.id))
const app = ref(null)
const questions = ref([])
const questionsLoading = ref(false)

const STATUS_FLOW = [
  { value: 'Pending', label: '待处理' },
  { value: 'Applied', label: '已投递' },
  { value: 'Written Test', label: '笔试' },
  { value: 'Interviewing', label: '面试中' },
  { value: 'Offer', label: 'Offer' },
  { value: 'Rejected', label: '已拒绝' },
]

const editForm = ref({ company: '', position: '', description: '', channel: '' })
const editMode = ref(false)

onMounted(() => loadApp())

async function loadApp() {
  await run(async () => {
    app.value = await applicationsApi.get(appId.value)
    editForm.value = {
      company: app.value.company,
      position: app.value.position,
      description: app.value.description || '',
      channel: app.value.channel || '',
    }
  })
}

async function saveEdit() {
  await run(async () => {
    app.value = await applicationsApi.update(appId.value, editForm.value)
    editMode.value = false
    toast.success('已保存')
  })
}

async function changeStatus(newStatus) {
  await run(async () => {
    app.value = await applicationsApi.updateStatus(appId.value, newStatus)
    toast.success(`状态已更新为 ${newStatus}`)
  })
}

async function generateQuestions() {
  if (!settings.hasAnyLlmKey) {
    toast.error('请先在设置页面配置 AI 模型')
    return
  }
  questionsLoading.value = true
  try {
    const res = await aiApi.generateQuestions(app.value.position, app.value.description || '')
    questions.value = res.questions || []
  } catch (e) {
    toast.error(e.message)
  } finally {
    questionsLoading.value = false
  }
}

function formatDate(dt) {
  return dt ? new Date(dt).toLocaleString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) : ''
}

function goBack() {
  router.push({ name: 'applications' })
}
</script>

<template>
  <div>
    <div v-if="loading" class="loading-state"><AppSpinner :size="32" /></div>
    <template v-else-if="app">
      <AppPageHeader :title="`${app.company} — ${app.position}`">
        <template #actions>
          <AppButton variant="ghost" @click="goBack">← 返回列表</AppButton>
        </template>
      </AppPageHeader>

      <!-- Status + quick actions -->
      <AppCard>
        <div class="status-bar">
          <div class="status-flow">
            <div v-for="s in STATUS_FLOW" :key="s.value" class="status-step" :class="{ 'status-step--done': app.status === s.value, 'status-step--past': STATUS_FLOW.findIndex(x => x.value === app.status) > STATUS_FLOW.findIndex(x => x.value === s.value) }">
              <div class="step-dot" />
              <span class="step-label">{{ s.label }}</span>
            </div>
          </div>
          <AppSelect
            :model-value="app.status"
            :options="STATUS_FLOW"
            @update:model-value="changeStatus"
          />
        </div>
      </AppCard>

      <div class="detail-grid">
        <!-- Info card -->
        <AppCard title="投递信息">
          <template #actions>
            <AppButton size="sm" variant="ghost" @click="editMode = !editMode">{{ editMode ? '取消' : '编辑' }}</AppButton>
          </template>
          <template v-if="editMode">
            <div class="form-stack">
              <AppInput v-model="editForm.company" label="公司" />
              <AppInput v-model="editForm.position" label="职位" />
              <AppInput v-model="editForm.channel" label="渠道" />
              <AppTextarea v-model="editForm.description" label="备注" :rows="3" />
              <div class="form-actions">
                <AppButton :loading="loading" @click="saveEdit">保存</AppButton>
              </div>
            </div>
          </template>
          <template v-else>
            <div class="info-grid">
              <div class="info-item"><span class="info-label text-subtle">公司</span><span>{{ app.company }}</span></div>
              <div class="info-item"><span class="info-label text-subtle">职位</span><span>{{ app.position }}</span></div>
              <div class="info-item"><span class="info-label text-subtle">渠道</span><span>{{ app.channel || '-' }}</span></div>
              <div class="info-item"><span class="info-label text-subtle">创建时间</span><span>{{ formatDate(app.created_at) }}</span></div>
              <div v-if="app.description" class="info-item wide"><span class="info-label text-subtle">备注</span><span>{{ app.description }}</span></div>
            </div>
          </template>
        </AppCard>

        <!-- Status timeline -->
        <AppCard title="状态变更记录">
          <div v-if="app.status_logs.length === 0" class="text-muted" style="font-size: var(--text-sm)">暂无变更记录</div>
          <div v-else class="timeline">
            <div v-for="(log, i) in [...app.status_logs].reverse()" :key="log.id" class="timeline-item">
              <div class="timeline-line" :class="{ 'timeline-line--first': i === 0 }" />
              <div class="timeline-dot" :class="{ 'timeline-dot--first': i === 0 }" />
              <div class="timeline-content">
                <div class="timeline-badge">
                  <StatusBadge :status="log.old_status || '新建'" />
                  <span class="timeline-arrow">→</span>
                  <StatusBadge :status="log.new_status" />
                </div>
                <div class="timeline-meta">
                  <span class="text-subtle">{{ formatDate(log.created_at) }}</span>
                  <span v-if="log.note" class="text-muted">{{ log.note }}</span>
                </div>
              </div>
            </div>
          </div>
        </AppCard>
      </div>

      <!-- AI Questions -->
      <AppCard title="AI 面试题生成" subtitle="基于该职位的 JD 生成针对性面试题" style="margin-top: var(--space-4)">
        <template #actions>
          <AppButton size="sm" :loading="questionsLoading" @click="generateQuestions">生成题目</AppButton>
        </template>
        <div v-if="questionsLoading" class="loading-state"><AppSpinner :size="24" /></div>
        <div v-else-if="questions.length" class="question-list">
          <div v-for="(q, i) in questions" :key="i" class="question-item">
            <span class="q-num">{{ i + 1 }}</span>
            <span>{{ q }}</span>
          </div>
        </div>
        <div v-else class="text-muted" style="font-size: var(--text-sm)">点击右上角生成面试题</div>
      </AppCard>
    </template>
  </div>
</template>

<style scoped>
.loading-state { display: flex; justify-content: center; padding: var(--space-7); }
.detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); margin-top: var(--space-4); }
.status-bar {
  display: flex; align-items: center; justify-content: space-between; gap: var(--space-4);
  padding: var(--space-2) 0;
}
.status-flow { display: flex; gap: var(--space-4); }
.status-step { display: flex; flex-direction: column; align-items: center; gap: 4px; }
.step-dot {
  width: 10px; height: 10px; border-radius: 50%;
  background: rgba(24,24,27,0.12); transition: background var(--duration-fast) var(--ease-out);
}
.status-step--past .step-dot { background: var(--gradient-primary); opacity: 0.5; }
.status-step--done .step-dot { background: var(--gradient-primary); box-shadow: 0 0 0 4px rgba(139, 92, 246, 0.2); }
.step-label { font-size: 11px; color: var(--color-text-muted); white-space: nowrap; }
.status-step--done .step-label { color: var(--color-text); font-weight: 600; }
.info-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--space-3); }
.info-item { display: flex; flex-direction: column; gap: 2px; }
.info-item.wide { grid-column: span 2; }
.info-label { font-size: var(--text-xs); }
.form-stack { display: flex; flex-direction: column; gap: var(--space-3); }
.form-actions { display: flex; justify-content: flex-end; }
.timeline { display: flex; flex-direction: column; }
.timeline-item { display: flex; gap: var(--space-3); position: relative; padding-bottom: var(--space-4); }
.timeline-item:last-child { padding-bottom: 0; }
.timeline-line {
  position: absolute; left: 5px; top: 16px; bottom: 0; width: 2px;
  background: rgba(24,24,27,0.08);
}
.timeline-item:last-child .timeline-line { display: none; }
.timeline-dot {
  width: 12px; height: 12px; border-radius: 50%;
  background: rgba(24,24,27,0.12); flex-shrink: 0; margin-top: 4px;
}
.timeline-dot--first { background: var(--gradient-primary); }
.timeline-content { flex: 1; }
.timeline-badge { display: flex; align-items: center; gap: var(--space-2); }
.timeline-arrow { color: var(--color-text-subtle); }
.timeline-meta { display: flex; gap: var(--space-3); margin-top: 4px; font-size: var(--text-xs); }
.question-list { display: flex; flex-direction: column; gap: var(--space-2); }
.question-item {
  display: flex; align-items: flex-start; gap: var(--space-3);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  background: rgba(24,24,27,0.02);
  font-size: var(--text-sm);
  line-height: var(--leading-relaxed);
}
.q-num {
  flex-shrink: 0;
  width: 22px; height: 22px;
  border-radius: 50%;
  background: var(--gradient-primary-soft);
  color: var(--color-primary);
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 600;
}
</style>
