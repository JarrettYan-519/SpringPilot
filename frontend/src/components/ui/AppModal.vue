<script setup>
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  title: { type: String, default: '' },
  size: { type: String, default: 'md' },
})
const emit = defineEmits(['close'])

const panelRef = ref(null)
const previouslyFocused = ref(null)

function onOverlayClick(e) {
  if (e.target === e.currentTarget) emit('close')
}

function onKeydown(e) {
  if (e.key === 'Escape') emit('close')
}

watch(() => props.open, async (val) => {
  if (val) {
    previouslyFocused.value = document.activeElement
    document.addEventListener('keydown', onKeydown)
    document.body.style.overflow = 'hidden'
    await nextTick()
    panelRef.value?.focus()
  } else {
    document.removeEventListener('keydown', onKeydown)
    document.body.style.overflow = ''
    previouslyFocused.value?.focus()
  }
})

onUnmounted(() => {
  document.removeEventListener('keydown', onKeydown)
  document.body.style.overflow = ''
})
</script>

<template>
  <Teleport to="body">
    <div v-if="open" class="modal" role="dialog" aria-modal="true">
      <div class="modal-overlay" @click="onOverlayClick" />
      <div class="modal-panel" ref="panelRef" tabindex="-1" :class="`modal-panel--${size}`" @click.stop>
        <header v-if="title" class="modal-header">
          <h2 class="modal-title">{{ title }}</h2>
          <button class="modal-close" aria-label="关闭" @click="emit('close')">×</button>
        </header>
        <div class="modal-body"><slot /></div>
        <footer v-if="$slots.footer" class="modal-footer"><slot name="footer" /></footer>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.modal {
  position: fixed; inset: 0; z-index: var(--z-modal);
  display: flex; align-items: center; justify-content: center;
  padding: var(--space-5);
}
.modal-overlay {
  position: fixed; inset: 0;
  background: rgba(24, 24, 27, 0.32);
  backdrop-filter: blur(4px);
}
.modal-panel {
  position: relative;
  background: var(--color-surface-elevated);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
  width: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  max-height: 90vh;
  outline: none;
  animation: modal-enter var(--duration-base) var(--ease-out);
}
.modal-panel:focus { outline: none; }
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
@keyframes modal-enter {
  from { transform: translateY(12px) scale(0.98); opacity: 0; }
  to { transform: translateY(0) scale(1); opacity: 1; }
}
</style>
