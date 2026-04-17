<script setup>
defineProps({
  padded: { type: Boolean, default: true },
  glass: { type: Boolean, default: false },
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' },
})
</script>

<template>
  <section class="card" :class="{ 'card--padded': padded, 'card--glass': glass }">
    <header v-if="title || $slots.header" class="card-header">
      <slot name="header">
        <div>
          <div class="card-title">{{ title }}</div>
          <div v-if="subtitle" class="card-subtitle">{{ subtitle }}</div>
        </div>
      </slot>
      <div v-if="$slots.actions" class="card-actions">
        <slot name="actions" />
      </div>
    </header>
    <div class="card-body"><slot /></div>
  </section>
</template>

<style scoped>
.card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}
.card--glass { background: var(--color-surface-glass); backdrop-filter: blur(20px) saturate(140%); }
.card--padded .card-header { padding: var(--space-4) var(--space-5); }
.card--padded .card-body { padding: var(--space-5); }
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  border-bottom: 1px solid var(--color-border);
}
.card-title { font-size: var(--text-md); font-weight: 600; }
.card-subtitle { font-size: var(--text-xs); color: var(--color-text-muted); margin-top: 2px; }
.card-actions { display: flex; gap: var(--space-2); }
</style>
