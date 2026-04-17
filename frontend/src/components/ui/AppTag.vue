<script setup>
defineProps({
  closable: { type: Boolean, default: false },
})
const emit = defineEmits(['close'])
</script>

<template>
  <span class="tag">
    <slot />
    <button v-if="closable" class="tag-close" aria-label="移除" @click.stop="emit('close')">×</button>
  </span>
</template>

<style scoped>
.tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  background: rgba(24, 24, 27, 0.05);
  color: var(--color-text-muted);
  font-size: var(--text-xs);
  font-weight: 500;
}
.tag-close {
  font-size: 14px;
  line-height: 1;
  color: var(--color-text-subtle);
  padding: 0 2px;
}
.tag-close:hover { color: var(--color-danger); }
</style>
