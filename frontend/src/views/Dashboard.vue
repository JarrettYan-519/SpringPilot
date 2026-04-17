<script setup>
import { ref, computed, onMounted } from 'vue'
import { applicationsApi } from '@/api/applications'
import { studyTasksApi } from '@/api/studyTasks'
import { weightApi, dietApi, trainingApi } from '@/api/fitness'
import { aiApi } from '@/api/ai'
import { useSettingsStore } from '@/stores/settings'
import AppPageHeader from '@/components/ui/AppPageHeader.vue'
import AppCard from '@/components/ui/AppCard.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppEmptyState from '@/components/ui/AppEmptyState.vue'
import WeightChart from '@/components/WeightChart.vue'
import CalorieChart from '@/components/CalorieChart.vue'

const settings = useSettingsStore()
const loading = ref(true)
const adviceLoading = ref(false)
const advice = ref('')

const applications = ref([])
const tasks = ref([])
const weightRecords = ref([])
const dietLogs = ref([])
const trainingLogs = ref([])

// Computed stats
const now = new Date()
const weekAgo = new Date(now.getTime() - 7 * 86400000)

const weeklyApps = computed(() =>
  applications.value.filter(a => new Date(a.created_at) >= weekAgo).length
)
const interviewing = computed(() =>
  applications.value.filter(a => a.status === 'Interviewing').length
)
const pendingTasks = computed(() =>
  tasks.value.filter(t => !t.completed).length
)
const weeklyTraining = computed(() =>
  trainingLogs.value.filter(t => new Date(t.recorded_at) >= weekAgo).length
)

// Stat card definitions
const stats = computed(() => [
  { label: '本周投递', value: weeklyApps.value, gradient: 'var(--gradient-primary)' },
  { label: '面试中', value: interviewing.value, gradient: 'var(--gradient-info)' },
  { label: '待办任务', value: pendingTasks.value, gradient: 'var(--gradient-warning)' },
  { label: '本周训练', value: weeklyTraining.value, gradient: 'var(--gradient-success)' },
])

onMounted(async () => {
  try {
    const [apps, t, w, d, tr] = await Promise.all([
      applicationsApi.list(),
      studyTasksApi.list(),
      weightApi.list(30),
      dietApi.list(),
      trainingApi.list(30),
    ])
    applications.value = apps
    tasks.value = t
    weightRecords.value = w
    dietLogs.value = d
    trainingLogs.value = tr
  } catch {
    // errors handled per-API by interceptor
  } finally {
    loading.value = false
  }
})

async function fetchAdvice() {
  if (!settings.hasAnyLlmKey) {
    advice.value = '请先在设置页面配置至少一个 AI 模型的 API Key。'
    return
  }
  adviceLoading.value = true
  try {
    const jobSummary = `投递${applications.value.length}家，面试中${interviewing.value}家，待办任务${pendingTasks.value}个。`
    const fitSummary = `近30天体重记录${weightRecords.value.length}条，训练${weeklyTraining.value}次/周。`
    const res = await aiApi.dailyAdvice(jobSummary, fitSummary)
    advice.value = res.advice
  } catch {
    advice.value = '获取建议失败，请检查 AI 模型配置。'
  } finally {
    adviceLoading.value = false
  }
}
</script>

<template>
  <div>
    <AppPageHeader title="首页" subtitle="求职 + 健身一站式概览" />

    <div v-if="loading" class="loading-state"><AppSpinner :size="32" /></div>

    <template v-else>
      <!-- Stat cards -->
      <div class="stats-row">
        <div v-for="s in stats" :key="s.label" class="stat-card">
          <div class="stat-value-row">
            <span class="stat-value">{{ s.value }}</span>
            <span class="stat-dot" :style="{ background: s.gradient }"></span>
          </div>
          <div class="stat-label">{{ s.label }}</div>
        </div>
      </div>

      <!-- Charts row -->
      <div class="charts-row">
        <AppCard title="体重趋势" subtitle="近 30 天">
          <WeightChart :records="weightRecords" />
        </AppCard>
        <AppCard title="热量摄入" subtitle="近 7 天">
          <CalorieChart :logs="dietLogs" />
        </AppCard>
      </div>

      <!-- AI Advice -->
      <AppCard title="AI 每日建议" subtitle="基于你的求职和健身数据">
        <template #actions>
          <AppButton size="sm" :loading="adviceLoading" @click="fetchAdvice">获取建议</AppButton>
        </template>
        <div v-if="advice" class="advice-text">{{ advice }}</div>
        <AppEmptyState v-else icon="◈" title="点击右上角获取今日建议" description="AI 会根据你的数据给出个性化建议" />
      </AppCard>
    </template>
  </div>
</template>

<style scoped>
.loading-state { display: flex; justify-content: center; padding: var(--space-7); }
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-4);
  margin-bottom: var(--space-5);
}
.stat-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-4) var(--space-5);
  box-shadow: var(--shadow-sm);
}
.stat-value-row { display: flex; align-items: baseline; gap: var(--space-2); }
.stat-value { font-size: var(--text-3xl); font-weight: 700; letter-spacing: -0.02em; }
.stat-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  margin-left: auto;
}
.stat-label { font-size: var(--text-sm); color: var(--color-text-muted); margin-top: 4px; }
.charts-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-4);
  margin-bottom: var(--space-5);
}
.advice-text {
  font-size: var(--text-base);
  line-height: var(--leading-relaxed);
  color: var(--color-text);
  white-space: pre-line;
  padding: var(--space-3) 0;
}
</style>
