<script setup>
import { Dialog, DialogPanel, DialogTitle } from '@headlessui/vue'

defineProps({
  open: { type: Boolean, default: false },
  title: { type: String, default: '' },
  size: { type: String, default: 'md' }, // sm | md | lg
})
const emit = defineEmits(['close'])
</script>

<template>
  <transition name="modal-fade">
    <Dialog v-if="open" as="div" class="modal" @close="emit('close')">
      <div class="modal-overlay" aria-hidden="true" />
      <div class="modal-container">
        <transition name="modal-pop" appear>
          <DialogPanel class="modal-panel" :class="`modal-panel--${size}`">
            <header v-if="title" class="modal-header">
              <DialogTitle class="modal-title">{{ title }}</DialogTitle>
              <button class="modal-close" aria-label="关闭" @click="emit('close')">×</button>
            </header>
            <div class="modal-body"><slot /></div>
            <footer v-if="$slots.footer" class="modal-footer"><slot name="footer" /></footer>
          </DialogPanel>
        </transition>
      </div>
    </Dialog>
  </transition>
</template>

<style scoped>
.modal { position: fixed; inset: 0; z-index: var(--z-modal); }
.modal-overlay {
  position: absolute; inset: 0;
  background: rgba(24, 24, 27, 0.32);
  backdrop-filter: blur(4px);
}
.modal-container {
  position: relative;
  min-height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-5);
}
.modal-panel {
  background: var(--color-surface-elevated);
  backdrop-filter: blur(24px) saturate(140%);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
  width: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  max-height: 90vh;
}
.modal-panel--sm { max-width: 420px; }
.modal-panel--md { max-width: 560px; }
.modal-panel--lg { max-width: 820px; }
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-5);
  border-bottom: 1px solid var(--color-border);
}
.modal-title { font-size: var(--text-lg); font-weight: 600; }
.modal-close {
  width: 32px; height: 32px;
  border-radius: var(--radius-md);
  color: var(--color-text-muted);
  font-size: 24px;
  display: inline-flex; align-items: center; justify-content: center;
  transition: background var(--duration-fast) var(--ease-out);
}
.modal-close:hover { background: rgba(24, 24, 27, 0.05); color: var(--color-text); }
.modal-body { padding: var(--space-5); overflow-y: auto; flex: 1; }
.modal-footer {
  padding: var(--space-4) var(--space-5);
  border-top: 1px solid var(--color-border);
  display: flex;
  justify-content: flex-end;
  gap: var(--space-2);
}
.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity var(--duration-base) var(--ease-out); }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
.modal-pop-enter-active { transition: transform var(--duration-base) var(--ease-out), opacity var(--duration-base) var(--ease-out); }
.modal-pop-enter-from { transform: translateY(12px) scale(0.98); opacity: 0; }
</style>
