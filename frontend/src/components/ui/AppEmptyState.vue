<script setup>
defineProps({
  icon: { type: String, default: '∅' },
  title: { type: String, default: '暂无数据' },
  description: { type: String, default: '' },
})
</script>

<template>
  <div class="empty">
    <div class="empty-icon" aria-hidden="true">{{ icon }}</div>
    <div class="empty-title">{{ title }}</div>
    <div v-if="description" class="empty-desc">{{ description }}</div>
    <div v-if="$slots.action" class="empty-action"><slot name="action" /></div>
  </div>
</template>

<style scoped>
.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: var(--space-7) var(--space-5);
  gap: var(--space-2);
}
.empty-icon {
  width: 56px; height: 56px;
  border-radius: var(--radius-full);
  background: var(--gradient-primary-soft);
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 24px;
  color: var(--color-primary);
  margin-bottom: var(--space-2);
}
.empty-title { font-size: var(--text-md); font-weight: 600; color: var(--color-text); }
.empty-desc { font-size: var(--text-sm); color: var(--color-text-muted); max-width: 360px; }
.empty-action { margin-top: var(--space-4); }
</style>
