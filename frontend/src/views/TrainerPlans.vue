<script setup>
import { ref, onMounted } from 'vue'
import { trainerPlansApi } from '@/api/trainerPlans'
import { useAsync } from '@/composables/useAsync'
import { useToast } from '@/composables/useToast'
import AppPageHeader from '@/components/ui/AppPageHeader.vue'
import AppCard from '@/components/ui/AppCard.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppModal from '@/components/ui/AppModal.vue'
import AppConfirmDialog from '@/components/ui/AppConfirmDialog.vue'
import AppEmptyState from '@/components/ui/AppEmptyState.vue'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import AppBadge from '@/components/ui/AppBadge.vue'

const toast = useToast()
const { loading, run } = useAsync()

const plans = ref([])
const showUpload = ref(false)
const deleteTarget = ref(null)
const deleteLoading = ref(false)
const uploadLoading = ref(false)
const expandedPlan = ref(null)

const form = ref({ title: '', plan_date_range: '', file: null })

onMounted(() => load())

async function load() {
  await run(async () => {
    plans.value = await trainerPlansApi.list()
  })
}

function openUpload() {
  form.value = { title: '', plan_date_range: '', file: null }
  showUpload.value = true
}

function onFileChange(e) {
  form.value.file = e.target.files[0] || null
}

async function uploadPlan() {
  if (!form.value.file || !form.value.title.trim()) {
    toast.warning('请填写标题并选择文件')
    return
  }
  uploadLoading.value = true
  try {
    const plan = await trainerPlansApi.upload(
      form.value.file,
      form.value.title.trim(),
      form.value.plan_date_range || null,
    )
    plans.value.unshift(plan)
    showUpload.value = false
    toast.success('训练计划已上传并解析')
  } catch (e) {
    toast.error(e.message)
  } finally {
    uploadLoading.value = false
  }
}

async function confirmDelete() {
  deleteLoading.value = true
  try {
    await trainerPlansApi.remove(deleteTarget.value.id)
    plans.value = plans.value.filter(p => p.id !== deleteTarget.value.id)
    if (expandedPlan.value === deleteTarget.value?.id) expandedPlan.value = null
    deleteTarget.value = null
    toast.success('已删除')
  } catch (e) {
    toast.error(e.message)
  } finally {
    deleteLoading.value = false
  }
}

function toggleExpand(id) {
  expandedPlan.value = expandedPlan.value === id ? null : id
}

function formatDate(dt) {
  return dt ? new Date(dt).toLocaleDateString('zh-CN') : ''
}
</script>

<template>
  <div>
    <AppPageHeader title="训练计划" subtitle="上传教练提供的训练计划文档，自动解析内容">
      <template #actions>
        <AppButton @click="openUpload">+ 上传计划</AppButton>
      </template>
    </AppPageHeader>

    <div v-if="loading" class="loading-state"><AppSpinner :size="32" /></div>
    <AppEmptyState v-else-if="plans.length === 0" icon="◇" title="暂无训练计划" description="上传教练给的 PDF / DOCX / MD 文件">
      <template #action><AppButton @click="openUpload">上传计划</AppButton></template>
    </AppEmptyState>
    <div v-else class="plan-list">
      <AppCard v-for="plan in plans" :key="plan.id" class="plan-card">
        <div class="plan-header" @click="toggleExpand(plan.id)">
          <div class="plan-info">
            <div class="plan-title">{{ plan.title }}</div>
            <div class="plan-meta">
              <span v-if="plan.plan_date_range" class="text-muted">{{ plan.plan_date_range }}</span>
              <span class="text-subtle">{{ formatDate(plan.created_at) }}</span>
            </div>
          </div>
          <div class="plan-actions" @click.stop>
            <AppBadge v-if="plan.parsed_content" variant="success" soft>已解析</AppBadge>
            <AppBadge v-else variant="warning" soft>未解析</AppBadge>
            <AppButton size="sm" variant="ghost" @click="deleteTarget = plan">删除</AppButton>
          </div>
          <span class="plan-expand" :class="{ 'plan-expand--open': expandedPlan === plan.id }">▾</span>
        </div>
        <div v-if="expandedPlan === plan.id" class="plan-content">
          <div v-if="plan.parsed_content" class="parsed-text">{{ plan.parsed_content }}</div>
          <div v-else class="text-muted">解析内容为空</div>
        </div>
      </AppCard>
    </div>

    <AppModal :open="showUpload" title="上传训练计划" size="md" @close="showUpload = false">
      <div class="form-stack">
        <AppInput v-model="form.title" label="标题" placeholder="4月训练计划" required />
        <AppInput v-model="form.plan_date_range" label="日期范围（可选）" placeholder="2026-04-01 ~ 2026-04-30" />
        <div class="file-field">
          <label class="file-label">文件</label>
          <input type="file" class="file-input" accept=".pdf,.docx,.md" @change="onFileChange" />
          <div v-if="form.file" class="file-name">{{ form.file.name }}</div>
        </div>
      </div>
      <template #footer>
        <AppButton variant="ghost" @click="showUpload = false">取消</AppButton>
        <AppButton :loading="uploadLoading" :disabled="!form.file || !form.title" @click="uploadPlan">上传并解析</AppButton>
      </template>
    </AppModal>

    <AppConfirmDialog
      :open="!!deleteTarget"
      title="删除训练计划"
      :message="`确定要删除「${deleteTarget?.title || ''}」吗？`"
      :loading="deleteLoading"
      @confirm="confirmDelete"
      @cancel="deleteTarget = null"
    />
  </div>
</template>

<style scoped>
.loading-state { display: flex; justify-content: center; padding: var(--space-7); }
.plan-list { display: flex; flex-direction: column; gap: var(--space-3); }
.plan-card { padding: 0; }
.plan-header {
  display: flex; align-items: center; gap: var(--space-4);
  padding: var(--space-4) var(--space-5);
  cursor: pointer;
  transition: background var(--duration-fast) var(--ease-out);
}
.plan-header:hover { background: rgba(24,24,27,0.02); }
.plan-info { flex: 1; min-width: 0; }
.plan-title { font-weight: 600; font-size: var(--text-md); }
.plan-meta { display: flex; gap: var(--space-3); font-size: var(--text-xs); margin-top: 2px; }
.plan-actions { display: flex; align-items: center; gap: var(--space-2); }
.plan-expand {
  color: var(--color-text-subtle); font-size: 14px;
  transition: transform var(--duration-fast) var(--ease-out);
}
.plan-expand--open { transform: rotate(180deg); }
.plan-content {
  padding: 0 var(--space-5) var(--space-5);
  border-top: 1px solid var(--color-border);
}
.parsed-text {
  padding-top: var(--space-4);
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  line-height: var(--leading-relaxed);
  white-space: pre-wrap;
  color: var(--color-text);
  max-height: 400px;
  overflow-y: auto;
}
.form-stack { display: flex; flex-direction: column; gap: var(--space-3); }
.file-field { display: flex; flex-direction: column; gap: 6px; }
.file-label { font-size: var(--text-sm); font-weight: 500; }
.file-input {
  font-family: var(--font-sans);
  font-size: var(--text-sm);
  padding: 8px 12px;
  border: 1px dashed var(--color-border-strong);
  border-radius: var(--radius-md);
  background: rgba(24,24,27,0.02);
  color: var(--color-text);
}
.file-input::file-selector-button {
  background: var(--gradient-primary);
  color: #fff;
  border: none;
  border-radius: var(--radius-sm);
  padding: 4px 12px;
  font-family: var(--font-sans);
  font-size: var(--text-sm);
  font-weight: 500;
  cursor: pointer;
  margin-right: 12px;
}
.file-name { font-size: var(--text-sm); color: var(--color-text-muted); }
</style>
