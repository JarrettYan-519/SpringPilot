<script setup>
import { useNotificationsStore } from '@/stores/notifications'
const notifications = useNotificationsStore()

function iconFor(variant) {
  return { success: '✓', error: '!', warning: '⚠', info: 'i' }[variant] || 'i'
}
</script>

<template>
  <div class="toast-host" role="region" aria-live="polite">
    <transition-group name="toast" tag="div" class="toast-stack">
      <div
        v-for="t in notifications.items"
        :key="t.id"
        class="toast"
        :class="`toast--${t.variant}`"
        role="status"
      >
        <span class="toast-icon" aria-hidden="true">{{ iconFor(t.variant) }}</span>
        <div class="toast-body">
          <div v-if="t.title" class="toast-title">{{ t.title }}</div>
          <div class="toast-message">{{ t.message }}</div>
        </div>
        <button class="toast-close" aria-label="关闭" @click="notifications.dismiss(t.id)">×</button>
      </div>
    </transition-group>
  </div>
</template>

<style scoped>
.toast-host {
  position: fixed;
  top: var(--space-5);
  right: var(--space-5);
  z-index: var(--z-toast);
  pointer-events: none;
}
.toast-stack { display: flex; flex-direction: column; gap: var(--space-2); }
.toast {
  pointer-events: auto;
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  background: var(--color-surface-elevated);
  backdrop-filter: blur(20px) saturate(140%);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  min-width: 280px;
  max-width: 400px;
}
.toast-icon {
  width: 22px; height: 22px;
  border-radius: 50%;
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 13px;
  color: #fff;
  flex-shrink: 0;
  margin-top: 1px;
}
.toast--success .toast-icon { background: var(--gradient-success); }
.toast--error   .toast-icon { background: var(--gradient-danger); }
.toast--warning .toast-icon { background: var(--gradient-warning); }
.toast--info    .toast-icon { background: var(--gradient-info); }
.toast-body { flex: 1; }
.toast-title { font-size: var(--text-sm); font-weight: 600; margin-bottom: 2px; }
.toast-message { font-size: var(--text-sm); color: var(--color-text-muted); }
.toast-close {
  color: var(--color-text-subtle);
  font-size: 18px; line-height: 1;
  padding: 2px 4px;
  margin: -2px -4px 0 0;
}
.toast-close:hover { color: var(--color-text); }
.toast-enter-active, .toast-leave-active { transition: transform var(--duration-base) var(--ease-out), opacity var(--duration-base) var(--ease-out); }
.toast-enter-from { transform: translateX(24px); opacity: 0; }
.toast-leave-to { transform: translateX(24px); opacity: 0; }
.toast-leave-active { position: absolute; right: 0; }
</style>
