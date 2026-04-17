<script setup>
defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
})
</script>

<template>
  <header class="page-header">
    <div class="page-header-text">
      <h1 class="heading-1">{{ title }}</h1>
      <p v-if="subtitle" class="page-header-sub text-muted">{{ subtitle }}</p>
    </div>
    <div v-if="$slots.actions" class="page-header-actions"><slot name="actions" /></div>
  </header>
</template>

<style scoped>
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-5);
  margin-bottom: var(--space-6);
}
.page-header-sub { margin-top: 6px; font-size: var(--text-sm); }
.page-header-actions { display: flex; gap: var(--space-2); flex-shrink: 0; }
</style>
