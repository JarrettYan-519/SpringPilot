<script setup>
import { ref, computed, onMounted } from 'vue'
import { studyTasksApi } from '@/api/studyTasks'
import { useAsync } from '@/composables/useAsync'
import { useToast } from '@/composables/useToast'
import AppPageHeader from '@/components/ui/AppPageHeader.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppTextarea from '@/components/ui/AppTextarea.vue'
import AppModal from '@/components/ui/AppModal.vue'
import AppConfirmDialog from '@/components/ui/AppConfirmDialog.vue'
import AppEmptyState from '@/components/ui/AppEmptyState.vue'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import AppTag from '@/components/ui/AppTag.vue'
import AppCheckbox from '@/components/ui/AppCheckbox.vue'

const toast = useToast()
const { loading, run } = useAsync()

const tasks = ref([])
const filter = ref('all')
const showCreate = ref(false)
const editTarget = ref(null)
const deleteTarget = ref(null)
const deleteLoading = ref(false)

const form = ref({ title: '', description: '', tags: '', due_date: '' })

const filteredTasks = computed(() => {
  if (filter.value === 'active') return tasks.value.filter(t => !t.completed)
  if (filter.value === 'completed') return tasks.value.filter(t => t.completed)
  return tasks.value
})

const counts = computed(() => ({
  all: tasks.value.length,
  active: tasks.value.filter(t => !t.completed).length,
  completed: tasks.value.filter(t => t.completed).length,
}))

onMounted(() => load())

async function load() {
  await run(async () => {
    tasks.value = await studyTasksApi.list()
  })
}

function openCreate() {
  form.value = { title: '', description: '', tags: '', due_date: '' }
  showCreate.value = true
}

function openEdit(task) {
  editTarget.value = task
  form.value = {
    title: task.title,
    description: task.description || '',
    tags: task.tags || '',
    due_date: task.due_date ? task.due_date.slice(0, 10) : '',
  }
}

async function createTask() {
  const payload = {
    title: form.value.title,
    description: form.value.description || null,
    tags: form.value.tags || null,
    due_date: form.value.due_date ? new Date(form.value.due_date).toISOString() : null,
  }
  await run(async () => {
    const task = await studyTasksApi.create(payload)
    tasks.value.unshift(task)
    showCreate.value = false
    toast.success('任务已创建')
  })
}

async function saveEdit() {
  const payload = {
    title: form.value.title,
    description: form.value.description || null,
    tags: form.value.tags || null,
    due_date: form.value.due_date ? new Date(form.value.due_date).toISOString() : null,
  }
  await run(async () => {
    const updated = await studyTasksApi.update(editTarget.value.id, payload)
    const idx = tasks.value.findIndex(t => t.id === updated.id)
    if (idx !== -1) tasks.value[idx] = updated
    editTarget.value = null
    toast.success('任务已更新')
  })
}

async function toggleComplete(task) {
  await run(async () => {
    const updated = await studyTasksApi.update(task.id, { completed: !task.completed })
    const idx = tasks.value.findIndex(t => t.id === updated.id)
    if (idx !== -1) tasks.value[idx] = updated
  })
}

async function confirmDelete() {
  deleteLoading.value = true
  try {
    await studyTasksApi.remove(deleteTarget.value.id)
    tasks.value = tasks.value.filter(t => t.id !== deleteTarget.value.id)
    deleteTarget.value = null
    toast.success('已删除')
  } catch (e) {
    toast.error(e.message)
  } finally {
    deleteLoading.value = false
  }
}

function parseTags(tags) {
  if (!tags) return []
  return tags.split(',').map(t => t.trim()).filter(Boolean)
}

function formatDate(dt) {
  return dt ? new Date(dt).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }) : ''
}

function isOverdue(task) {
  return task.due_date && !task.completed && new Date(task.due_date) < new Date()
}
</script>

<template>
  <div>
    <AppPageHeader title="学习任务" subtitle="管理每日学习计划与进度">
      <template #actions>
        <AppButton @click="openCreate">+ 新建任务</AppButton>
      </template>
    </AppPageHeader>

    <div class="filter-row">
      <button v-for="f in ['all', 'active', 'completed']" :key="f" class="filter-chip" :class="{ 'filter-chip--active': filter === f }" @click="filter = f">
        {{ f === 'all' ? '全部' : f === 'active' ? '进行中' : '已完成' }}
        <span class="filter-count">{{ counts[f] }}</span>
      </button>
    </div>

    <div v-if="loading" class="loading-state"><AppSpinner :size="32" /></div>
    <AppEmptyState v-else-if="filteredTasks.length === 0" icon="✓" title="暂无任务" description="创建一个学习任务开始吧">
      <template #action><AppButton @click="openCreate">新建任务</AppButton></template>
    </AppEmptyState>
    <div v-else class="task-list">
      <div v-for="task in filteredTasks" :key="task.id" class="task-row" :class="{ 'task-row--done': task.completed }">
        <AppCheckbox :model-value="task.completed" @update:model-value="toggleComplete(task)" />
        <div class="task-body" @click="openEdit(task)">
          <div class="task-title" :class="{ 'task-title--done': task.completed }">{{ task.title }}</div>
          <div class="task-meta">
            <AppTag v-for="tag in parseTags(task.tags)" :key="tag">{{ tag }}</AppTag>
            <span v-if="task.due_date" class="task-due text-subtle" :class="{ 'task-due--overdue': isOverdue(task) }">
              {{ formatDate(task.due_date) }}
            </span>
          </div>
        </div>
        <button class="task-delete" @click.stop="deleteTarget = task">×</button>
      </div>
    </div>

    <AppModal :open="showCreate" title="新建学习任务" size="md" @close="showCreate = false">
      <div class="form-stack">
        <AppInput v-model="form.title" label="标题" placeholder="LeetCode 两数之和" required />
        <AppTextarea v-model="form.description" label="描述（可选）" :rows="2" />
        <AppInput v-model="form.tags" label="标签" placeholder="algorithm, Python（逗号分隔）" />
        <AppInput v-model="form.due_date" label="截止日期" type="date" />
      </div>
      <template #footer>
        <AppButton variant="ghost" @click="showCreate = false">取消</AppButton>
        <AppButton :loading="loading" :disabled="!form.title" @click="createTask">创建</AppButton>
      </template>
    </AppModal>

    <AppModal :open="!!editTarget" title="编辑任务" size="md" @close="editTarget = null">
      <div class="form-stack">
        <AppInput v-model="form.title" label="标题" required />
        <AppTextarea v-model="form.description" label="描述" :rows="2" />
        <AppInput v-model="form.tags" label="标签" placeholder="逗号分隔" />
        <AppInput v-model="form.due_date" label="截止日期" type="date" />
      </div>
      <template #footer>
        <AppButton variant="ghost" @click="editTarget = null">取消</AppButton>
        <AppButton :loading="loading" @click="saveEdit">保存</AppButton>
      </template>
    </AppModal>

    <AppConfirmDialog
      :open="!!deleteTarget"
      title="删除任务"
      :message="`确定要删除「${deleteTarget?.title || ''}」吗？`"
      :loading="deleteLoading"
      @confirm="confirmDelete"
      @cancel="deleteTarget = null"
    />
  </div>
</template>

<style scoped>
.filter-row { display: flex; gap: var(--space-2); margin-bottom: var(--space-5); }
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
  font-size: 11px; background: rgba(24,24,27,0.08); border-radius: 999px; padding: 1px 6px;
}
.filter-chip--active .filter-count { background: rgba(255,255,255,0.25); }
.task-list { display: flex; flex-direction: column; gap: var(--space-2); }
.task-row {
  display: flex; align-items: center; gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  transition: border var(--duration-fast) var(--ease-out);
}
.task-row:hover { border-color: var(--color-border-strong); }
.task-row--done { opacity: 0.6; }
.task-body { flex: 1; cursor: pointer; min-width: 0; }
.task-title { font-weight: 500; }
.task-title--done { text-decoration: line-through; color: var(--color-text-muted); }
.task-meta { display: flex; align-items: center; gap: var(--space-2); margin-top: 4px; }
.task-due { font-size: var(--text-xs); }
.task-due--overdue { color: var(--color-danger) !important; font-weight: 500; }
.task-delete {
  color: var(--color-text-subtle); font-size: 18px; padding: 4px 8px;
  border-radius: var(--radius-sm); transition: all var(--duration-fast) var(--ease-out);
}
.task-delete:hover { background: rgba(244, 63, 94, 0.1); color: var(--color-danger); }
.form-stack { display: flex; flex-direction: column; gap: var(--space-3); }
.loading-state { display: flex; justify-content: center; padding: var(--space-7); }
</style>
