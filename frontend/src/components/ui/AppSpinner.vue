<script setup>
defineProps({
  size: { type: Number, default: 20 },
})
</script>

<template>
  <span class="spinner" :style="{ width: size + 'px', height: size + 'px' }" aria-label="加载中" />
</template>

<style scoped>
.spinner {
  display: inline-block;
  border: 2px solid rgba(139, 92, 246, 0.2);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
</style>
