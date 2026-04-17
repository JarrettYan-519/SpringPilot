<script setup>
defineProps({
  modelValue: { type: [String, Number], required: true },
  tabs: { type: Array, required: true }, // [{ value, label }]
})
const emit = defineEmits(['update:modelValue'])
</script>

<template>
  <div class="tabs">
    <button
      v-for="tab in tabs"
      :key="tab.value"
      class="tab"
      :class="{ 'tab--active': tab.value === modelValue }"
      @click="emit('update:modelValue', tab.value)"
    >
      {{ tab.label }}
    </button>
  </div>
</template>

<style scoped>
.tabs {
  display: inline-flex;
  gap: 2px;
  padding: 4px;
  background: rgba(24, 24, 27, 0.04);
  border-radius: var(--radius-md);
}
.tab {
  padding: 6px 14px;
  border-radius: 8px;
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text-muted);
  transition: background var(--duration-fast) var(--ease-out), color var(--duration-fast) var(--ease-out);
}
.tab:hover { color: var(--color-text); }
.tab--active {
  background: var(--color-surface);
  color: var(--color-text);
  box-shadow: var(--shadow-sm);
}
</style>
