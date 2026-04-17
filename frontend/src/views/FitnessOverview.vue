<script setup>
import { ref, computed, onMounted } from 'vue'
import { weightApi, dietApi, trainingApi } from '@/api/fitness'
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
import AppModal from '@/components/ui/AppModal.vue'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import AppEmptyState from '@/components/ui/AppEmptyState.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import WeightChart from '@/components/WeightChart.vue'
import CalorieChart from '@/components/CalorieChart.vue'
import TrainingHeatmap from '@/components/TrainingHeatmap.vue'

const settings = useSettingsStore()
const toast = useToast()
const { loading, run } = useAsync()

const weightRecords = ref([])
const dietLogs = ref([])
const trainingLogs = ref([])

const showWeightModal = ref(false)
const showDietModal = ref(false)
const showTrainingModal = ref(false)

const weightForm = ref({ weight_kg: '', note: '' })
const dietForm = ref({ meal_type: 'breakfast', content: '', calories: '' })
const trainingForm = ref({ training_type: 'strength', content: '', duration_minutes: '' })

const estimatingCalories = ref(false)

const MEAL_OPTIONS = [
  { value: 'breakfast', label: '早餐' },
  { value: 'lunch', label: '午餐' },
  { value: 'dinner', label: '晚餐' },
  { value: 'snack', label: '加餐' },
]
const TRAINING_TYPE_OPTIONS = [
  { value: 'strength', label: '力量训练' },
  { value: 'cardio', label: '有氧' },
  { value: 'stretching', label: '拉伸' },
]

// Stats
const currentWeight = computed(() => {
  if (!weightRecords.value.length) return '-'
  return weightRecords.value[0].weight_kg
})
const todayStr = new Date().toISOString().slice(0, 10)
const todayCalories = computed(() => {
  return dietLogs.value
    .filter(l => l.recorded_at.slice(0, 10) === todayStr)
    .reduce((sum, l) => sum + (l.calories || 0), 0)
})
const weeklyTraining = computed(() => {
  const weekAgo = new Date(Date.now() - 7 * 86400000)
  return trainingLogs.value.filter(t => new Date(t.recorded_at) >= weekAgo).length
})
const todayDietLogs = computed(() =>
  dietLogs.value.filter(l => l.recorded_at.slice(0, 10) === todayStr)
)

const stats = computed(() => [
  { label: '当前体重', value: currentWeight.value === '-' ? '-' : `${currentWeight.value} kg`, gradient: 'var(--gradient-primary)' },
  { label: '今日热量', value: `${todayCalories.value} kcal`, gradient: 'var(--gradient-warning)' },
  { label: '本周训练', value: `${weeklyTraining.value} 次`, gradient: 'var(--gradient-success)' },
])

onMounted(() => loadData())

async function loadData() {
  await run(async () => {
    const [w, d, t] = await Promise.all([
      weightApi.list(90),
      dietApi.list(),
      trainingApi.list(30),
    ])
    weightRecords.value = w
    dietLogs.value = d
    trainingLogs.value = t
  })
}

async function addWeight() {
  await run(async () => {
    const record = await weightApi.create({
      weight_kg: Number(weightForm.value.weight_kg),
      note: weightForm.value.note || null,
    })
    weightRecords.value.unshift(record)
    showWeightModal.value = false
    weightForm.value = { weight_kg: '', note: '' }
    toast.success('体重已记录')
  })
}

async function addDiet() {
  await run(async () => {
    const record = await dietApi.create({
      meal_type: dietForm.value.meal_type,
      content: dietForm.value.content,
      calories: dietForm.value.calories ? Number(dietForm.value.calories) : null,
    })
    dietLogs.value.unshift(record)
    showDietModal.value = false
    dietForm.value = { meal_type: 'breakfast', content: '', calories: '' }
    toast.success('饮食已记录')
  })
}

async function estimateCalories() {
  if (!dietForm.value.content.trim()) return
  if (!settings.hasAnyLlmKey) {
    toast.error('请先在设置页面配置 AI 模型')
    return
  }
  estimatingCalories.value = true
  try {
    const res = await aiApi.estimateCalories(dietForm.value.content)
    dietForm.value.calories = String(res.calories)
    toast.success(`AI 估算: ${res.calories} kcal`)
  } catch (e) {
    toast.error(e.message)
  } finally {
    estimatingCalories.value = false
  }
}

async function addTraining() {
  await run(async () => {
    const record = await trainingApi.create({
      training_type: trainingForm.value.training_type,
      content: trainingForm.value.content,
      duration_minutes: trainingForm.value.duration_minutes ? Number(trainingForm.value.duration_minutes) : null,
    })
    trainingLogs.value.unshift(record)
    showTrainingModal.value = false
    trainingForm.value = { training_type: 'strength', content: '', duration_minutes: '' }
    toast.success('训练已记录')
  })
}

async function toggleTrainingComplete(log) {
  await run(async () => {
    const updated = await trainingApi.update(log.id, { completed: !log.completed })
    const idx = trainingLogs.value.findIndex(t => t.id === updated.id)
    if (idx !== -1) trainingLogs.value[idx] = updated
  })
}

function mealTypeLabel(type) {
  return MEAL_OPTIONS.find(m => m.value === type)?.label || type
}

function trainingTypeLabel(type) {
  return TRAINING_TYPE_OPTIONS.find(t => t.value === type)?.label || type
}
</script>

<template>
  <div>
    <AppPageHeader title="数据概览" subtitle="体重、饮食与训练数据一览" />

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

      <!-- Weight + Diet charts -->
      <div class="charts-row">
        <AppCard title="体重趋势" subtitle="近 90 天">
          <template #actions>
            <AppButton size="sm" @click="showWeightModal = true">+ 记录体重</AppButton>
          </template>
          <WeightChart :records="weightRecords" />
        </AppCard>
        <AppCard title="热量摄入" subtitle="近 7 天">
          <template #actions>
            <AppButton size="sm" @click="showDietModal = true">+ 记录饮食</AppButton>
          </template>
          <CalorieChart :logs="dietLogs" />
        </AppCard>
      </div>

      <div class="bottom-row">
        <!-- Today's diet -->
        <AppCard title="今日饮食">
          <div v-if="todayDietLogs.length === 0" class="text-muted" style="font-size: var(--text-sm)">今天还没有记录</div>
          <div v-else class="diet-list">
            <div v-for="log in todayDietLogs" :key="log.id" class="diet-item">
              <AppBadge :variant="log.meal_type === 'snack' ? 'neutral' : 'primary'" soft>{{ mealTypeLabel(log.meal_type) }}</AppBadge>
              <span class="diet-content">{{ log.content }}</span>
              <span class="diet-cal text-subtle">{{ log.calories ? `${log.calories} kcal` : '-' }}</span>
            </div>
          </div>
        </AppCard>

        <!-- Training -->
        <AppCard title="训练记录">
          <template #actions>
            <AppButton size="sm" @click="showTrainingModal = true">+ 记录训练</AppButton>
          </template>
          <TrainingHeatmap :logs="trainingLogs" />
          <div class="training-list">
            <div v-for="log in trainingLogs.slice(0, 5)" :key="log.id" class="training-item" @click="toggleTrainingComplete(log)">
              <div class="training-check" :class="{ 'training-check--done': log.completed }">✓</div>
              <div class="training-info">
                <span class="training-type">{{ trainingTypeLabel(log.training_type) }}</span>
                <span class="training-content text-muted">{{ log.content }}</span>
              </div>
              <span v-if="log.duration_minutes" class="text-subtle">{{ log.duration_minutes }}分钟</span>
            </div>
          </div>
        </AppCard>
      </div>
    </template>

    <!-- Weight modal -->
    <AppModal :open="showWeightModal" title="记录体重" size="sm" @close="showWeightModal = false">
      <div class="form-stack">
        <AppInput v-model="weightForm.weight_kg" label="体重 (kg)" type="number" placeholder="75.5" required />
        <AppInput v-model="weightForm.note" label="备注（可选）" placeholder="早晨空腹" />
      </div>
      <template #footer>
        <AppButton variant="ghost" @click="showWeightModal = false">取消</AppButton>
        <AppButton :loading="loading" :disabled="!weightForm.weight_kg" @click="addWeight">保存</AppButton>
      </template>
    </AppModal>

    <!-- Diet modal -->
    <AppModal :open="showDietModal" title="记录饮食" size="sm" @close="showDietModal = false">
      <div class="form-stack">
        <AppSelect v-model="dietForm.meal_type" label="餐次" :options="MEAL_OPTIONS" />
        <AppTextarea v-model="dietForm.content" label="内容" :rows="2" placeholder="鸡胸肉、糙米饭、蔬菜沙拉" required />
        <div class="calorie-row">
          <AppInput v-model="dietForm.calories" label="热量 (kcal)" type="number" placeholder="手动输入或 AI 估算" />
          <AppButton size="sm" variant="ghost" :loading="estimatingCalories" @click="estimateCalories">AI 估算</AppButton>
        </div>
      </div>
      <template #footer>
        <AppButton variant="ghost" @click="showDietModal = false">取消</AppButton>
        <AppButton :loading="loading" :disabled="!dietForm.content" @click="addDiet">保存</AppButton>
      </template>
    </AppModal>

    <!-- Training modal -->
    <AppModal :open="showTrainingModal" title="记录训练" size="sm" @close="showTrainingModal = false">
      <div class="form-stack">
        <AppSelect v-model="trainingForm.training_type" label="类型" :options="TRAINING_TYPE_OPTIONS" />
        <AppTextarea v-model="trainingForm.content" label="内容" :rows="2" placeholder="卧推 3x8, 深蹲 3x10" required />
        <AppInput v-model="trainingForm.duration_minutes" label="时长（分钟）" type="number" placeholder="60" />
      </div>
      <template #footer>
        <AppButton variant="ghost" @click="showTrainingModal = false">取消</AppButton>
        <AppButton :loading="loading" :disabled="!trainingForm.content" @click="addTraining">保存</AppButton>
      </template>
    </AppModal>
  </div>
</template>

<style scoped>
.loading-state { display: flex; justify-content: center; padding: var(--space-7); }
.stats-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-4); margin-bottom: var(--space-5); }
.stat-card {
  background: var(--color-surface); border: 1px solid var(--color-border);
  border-radius: var(--radius-lg); padding: var(--space-4) var(--space-5);
  box-shadow: var(--shadow-sm);
}
.stat-value-row { display: flex; align-items: baseline; gap: var(--space-2); }
.stat-value { font-size: var(--text-2xl); font-weight: 700; letter-spacing: -0.02em; }
.stat-dot { width: 8px; height: 8px; border-radius: 50%; margin-left: auto; }
.stat-label { font-size: var(--text-sm); color: var(--color-text-muted); margin-top: 4px; }
.charts-row { display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--space-4); margin-bottom: var(--space-4); }
.bottom-row { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); }
.form-stack { display: flex; flex-direction: column; gap: var(--space-3); }
.calorie-row { display: flex; gap: var(--space-2); align-items: flex-end; }
.calorie-row > :first-child { flex: 1; }

.diet-list { display: flex; flex-direction: column; gap: var(--space-2); }
.diet-item {
  display: flex; align-items: center; gap: var(--space-3);
  padding: var(--space-2) 0; border-bottom: 1px solid var(--color-border);
  font-size: var(--text-sm);
}
.diet-item:last-child { border-bottom: none; }
.diet-content { flex: 1; }
.diet-cal { font-size: var(--text-xs); white-space: nowrap; }

.training-list { display: flex; flex-direction: column; gap: var(--space-2); margin-top: var(--space-4); }
.training-item {
  display: flex; align-items: center; gap: var(--space-3);
  padding: var(--space-2) var(--space-3); border-radius: var(--radius-md);
  cursor: pointer; transition: background var(--duration-fast) var(--ease-out);
  font-size: var(--text-sm);
}
.training-item:hover { background: rgba(24,24,27,0.03); }
.training-check {
  width: 20px; height: 20px; border-radius: 5px;
  border: 1.5px solid var(--color-border-strong);
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 11px; color: transparent; flex-shrink: 0;
  transition: all var(--duration-fast) var(--ease-out);
}
.training-check--done {
  background: var(--gradient-success); border-color: transparent; color: #fff;
}
.training-info { flex: 1; }
.training-type { font-weight: 500; }
.training-content { margin-left: var(--space-2); }
</style>
