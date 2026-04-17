<script setup>
defineProps({
  width: { type: String, default: '100%' },
  height: { type: String, default: '1em' },
  radius: { type: String, default: 'var(--radius-sm)' },
})
</script>

<template>
  <span class="skeleton" :style="{ width, height, borderRadius: radius }" />
</template>

<style scoped>
.skeleton {
  display: inline-block;
  background: linear-gradient(90deg, rgba(24,24,27,0.04) 0%, rgba(24,24,27,0.09) 50%, rgba(24,24,27,0.04) 100%);
  background-size: 200% 100%;
  animation: shimmer 1.4s ease-in-out infinite;
}
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
