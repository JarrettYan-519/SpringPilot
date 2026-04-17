<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { applicationsApi } from '@/api/applications'
import { useAsync } from '@/composables/useAsync'
import { useToast } from '@/composables/useToast'
import AppPageHeader from '@/components/ui/AppPageHeader.vue'
import AppCard from '@/components/ui/AppCard.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppTextarea from '@/components/ui/AppTextarea.vue'
import AppSelect from '@/components/ui/AppSelect.vue'
import AppModal from '@/components/ui/AppModal.vue'
import AppConfirmDialog from '@/components/ui/AppConfirmDialog.vue'
import AppEmptyState from '@/components/ui/AppEmptyState.vue'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import StatusBadge from '@/components/StatusBadge.vue'

const router = useRouter()
const toast = useToast()
const { loading, run } = useAsync()

const applications = ref([])
const activeFilter = ref('all')
const showCreate = ref(false)
const deleteTarget = ref(null)
const deleteLoading = ref(false)

const STATUS_OPTIONS = [
  { value: 'all',            label: '全部' },
  { value: 'Pending',        label: '待处理' },
  { value: 'Applied',        label: '已投递' },
  { value: 'Written Test',   label: '笔试' },
  { value: 'Interviewing',   label: '面试中' },
  { value: 'Offer',          label: 'Offer' },
  { value: 'Rejected',       label: '已拒绝' },
]

const NEXT_STATUS = {
  Pending: 'Applied',
  Applied: 'Written Test',
  'Written Test': 'Interviewing',
  Interviewing: 'Offer',
}

const filteredApps = computed(() => {
  if (activeFilter.value === 'all') return applications.value
  return applications.value.filter(a => a.status === activeFilter.value)
})

// Create form
const form = ref({ company: '', position: '', description: '', channel: '', status: 'Pending' })
const CHANNEL_OPTIONS = [
  { value: 'Boss直聘', label: 'Boss直聘' },
  { value: '官网', label: '官网' },
  { value: '内推', label: '内推' },
  { value: '猎头', label: '猎头' },
  { value: '其他', label: '其他' },
]

onMounted(() => load())

async function load() {
  await run(async () => {
    applications.value = await applicationsApi.list()
  })
}

function openCreate() {
  form.value = { company: '', position: '', description: '', channel: '', status: 'Pending' }
  showCreate.value = true
}

async function createApp() {
  await run(async () => {
    const app = await applicationsApi.create(form.value)
    applications.value.unshift(app)
    showCreate.value = false
    toast.success('投递记录已创建')
  })
}

async function advanceStatus(app) {
  const next = NEXT_STATUS[app.status]
  if (!next) return
  await run(async () => {
    const updated = await applicationsApi.updateStatus(app.id, next)
    const idx = applications.value.findIndex(a => a.id === app.id)
    if (idx !== -1) applications.value[idx] = updated
    toast.success(`状态已更新为 ${next}`)
  })
}

async function confirmDelete() {
  deleteLoading.value = true
  try {
    await applicationsApi.remove(deleteTarget.value.id)
    applications.value = applications.value.filter(a => a.id !== deleteTarget.value.id)
    deleteTarget.value = null
    toast.success('已删除')
  } catch (e) {
    toast.error(e.message)
  } finally {
    deleteLoading.value = false
  }
}

function goDetail(app) {
  router.push({ name: 'application-detail', params: { id: app.id } })
}

function formatDate(dt) {
  return dt ? new Date(dt).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }) : ''
}
</script>

<template>
  <div>
    <AppPageHeader title="投递记录" subtitle="追踪每一家公司的申请进度">
      <template #actions>
        <AppButton @click="openCreate">+ 新建投递</AppButton>
      </template>
    </AppPageHeader>

    <!-- Filter tabs -->
    <div class="filter-row">
      <button
        v-for="opt in STATUS_OPTIONS"
        :key="opt.value"
        class="filter-chip"
        :class="{ 'filter-chip--active': activeFilter === opt.value }"
        @click="activeFilter = opt.value"
      >
        {{ opt.label }}
        <span v-if="opt.value !== 'all'" class="filter-count">
          {{ applications.filter(a => a.status === opt.value).length }}
        </span>
      </button>
    </div>

    <!-- List -->
    <div v-if="loading" class="loading-state"><AppSpinner :size="32" /></div>
    <AppEmptyState v-else-if="filteredApps.length === 0" icon="✦" title="暂无投递记录" description="点击右上角新建你的第一条投递">
      <template #action><AppButton @click="openCreate">新建投递</AppButton></template>
    </AppEmptyState>
    <div v-else class="app-list">
      <div v-for="app in filteredApps" :key="app.id" class="app-row" @click="goDetail(app)">
        <div class="app-main">
          <div class="app-company">{{ app.company }}</div>
          <div class="app-position text-muted">{{ app.position }}</div>
        </div>
        <div class="app-meta">
          <StatusBadge :status="app.status" />
          <span class="app-date text-subtle">{{ formatDate(app.created_at) }}</span>
        </div>
        <div class="app-actions" @click.stop>
          <AppButton v-if="NEXT_STATUS[app.status]" size="sm" variant="ghost" @click="advanceStatus(app)">→ 推进</AppButton>
          <AppButton size="sm" variant="ghost" @click="deleteTarget = app">删除</AppButton>
        </div>
      </div>
    </div>

    <!-- Create modal -->
    <AppModal :open="showCreate" title="新建投递记录" size="md" @close="showCreate = false">
      <div class="form-stack">
        <AppInput v-model="form.company" label="公司名称" placeholder="字节跳动" required />
        <AppInput v-model="form.position" label="职位" placeholder="后端工程师" required />
        <AppTextarea v-model="form.description" label="备注（可选）" :rows="3" placeholder="JD 链接、内推人等" />
        <AppSelect v-model="form.channel" label="渠道" :options="CHANNEL_OPTIONS" placeholder="选择渠道" />
      </div>
      <template #footer>
        <AppButton variant="ghost" @click="showCreate = false">取消</AppButton>
        <AppButton :loading="loading" :disabled="!form.company || !form.position" @click="createApp">创建</AppButton>
      </template>
    </AppModal>

    <!-- Delete confirm -->
    <AppConfirmDialog
      :open="!!deleteTarget"
      title="删除投递记录"
      :message="`确定要删除「${deleteTarget?.company || ''} - ${deleteTarget?.position || ''}」吗？此操作不可撤销。`"
      :loading="deleteLoading"
      @confirm="confirmDelete"
      @cancel="deleteTarget = null"
    />
  </div>
</template>

<style scoped>
.filter-row { display: flex; flex-wrap: wrap; gap: var(--space-2); margin-bottom: var(--space-5); }
.filter-chip {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 6px 14px; border-radius: var(--radius-full);
  background: var(--color-surface); border: 1px solid var(--color-border);
  font-size: var(--text-sm); font-weight: 500; color: var(--color-text-muted);
  transition: all var(--duration-fast) var(--ease-out); cursor: pointer;
}
.filter-chip:hover { border-color: var(--color-border-strong); color: var(--color-text); }
.filter-chip--active {
  background: var(--gradient-primary); color: #fff; border-color: transparent;
  box-shadow: 0 4px 14px rgba(139, 92, 246, 0.32);
}
.filter-count {
  font-size: 11px;
  background: rgba(24,24,27,0.08);
  border-radius: 999px;
  padding: 1px 6px;
}
.filter-chip--active .filter-count { background: rgba(255,255,255,0.25); }
.app-list { display: flex; flex-direction: column; gap: var(--space-2); }
.app-row {
  display: flex; align-items: center; gap: var(--space-4);
  padding: var(--space-3) var(--space-4);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: border var(--duration-fast) var(--ease-out), box-shadow var(--duration-fast) var(--ease-out);
}
.app-row:hover { border-color: var(--color-border-strong); box-shadow: var(--shadow-sm); }
.app-main { flex: 1; min-width: 0; }
.app-company { font-weight: 600; font-size: var(--text-md); }
.app-position { font-size: var(--text-sm); }
.app-meta { display: flex; align-items: center; gap: var(--space-3); }
.app-date { font-size: var(--text-xs); }
.app-actions { display: flex; gap: var(--space-1); }
.form-stack { display: flex; flex-direction: column; gap: var(--space-3); }
.loading-state { display: flex; justify-content: center; padding: var(--space-7); }
</style>
