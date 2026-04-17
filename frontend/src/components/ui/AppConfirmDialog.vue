<script setup>
import AppModal from './AppModal.vue'
import AppButton from './AppButton.vue'

defineProps({
  open: { type: Boolean, default: false },
  title: { type: String, default: '确认操作' },
  message: { type: String, default: '' },
  confirmText: { type: String, default: '确认' },
  cancelText: { type: String, default: '取消' },
  variant: { type: String, default: 'danger' }, // danger | primary
  loading: { type: Boolean, default: false },
})
const emit = defineEmits(['confirm', 'cancel'])
</script>

<template>
  <AppModal :open="open" :title="title" size="sm" @close="emit('cancel')">
    <p class="confirm-message">{{ message }}</p>
    <template #footer>
      <AppButton variant="ghost" :disabled="loading" @click="emit('cancel')">{{ cancelText }}</AppButton>
      <AppButton :variant="variant" :loading="loading" @click="emit('confirm')">{{ confirmText }}</AppButton>
    </template>
  </AppModal>
</template>

<style scoped>
.confirm-message { font-size: var(--text-base); color: var(--color-text-muted); line-height: var(--leading-relaxed); }
</style>
