<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: { type: String, default: 'primary' }, // primary | secondary | ghost | danger | success
  size: { type: String, default: 'md' },          // sm | md | lg
  loading: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  type: { type: String, default: 'button' },
  block: { type: Boolean, default: false },
})

const classes = computed(() => [
  'btn',
  `btn--${props.variant}`,
  `btn--${props.size}`,
  { 'btn--block': props.block, 'btn--loading': props.loading },
])
</script>

<template>
  <button :type="type" :class="classes" :disabled="disabled || loading">
    <span v-if="loading" class="btn-spinner" aria-hidden="true"></span>
    <span class="btn-content" :class="{ 'btn-content--hidden': loading }">
      <slot />
    </span>
  </button>
</template>

<style scoped>
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  border-radius: var(--radius-md);
  font-weight: 600;
  letter-spacing: -0.01em;
  transition: transform var(--duration-fast) var(--ease-out), box-shadow var(--duration-fast) var(--ease-out), background var(--duration-fast) var(--ease-out), color var(--duration-fast) var(--ease-out);
  white-space: nowrap;
  position: relative;
}
.btn:disabled { cursor: not-allowed; opacity: 0.55; }
.btn:not(:disabled):active { transform: scale(0.98); }
.btn--block { width: 100%; }

.btn--sm { padding: 6px 12px; font-size: var(--text-sm); height: 30px; }
.btn--md { padding: 8px 16px; font-size: var(--text-base); height: 36px; }
.btn--lg { padding: 11px 20px; font-size: var(--text-md); height: 44px; }

.btn--primary {
  background: var(--gradient-primary);
  color: #fff;
  box-shadow: 0 4px 14px rgba(139, 92, 246, 0.32);
}
.btn--primary:not(:disabled):hover { box-shadow: 0 6px 20px rgba(139, 92, 246, 0.40); transform: translateY(-1px); }

.btn--secondary {
  background: var(--color-surface);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
}
.btn--secondary:not(:disabled):hover { border-color: var(--color-border-strong); background: #fff; }

.btn--ghost { background: transparent; color: var(--color-text-muted); }
.btn--ghost:not(:disabled):hover { background: rgba(24, 24, 27, 0.05); color: var(--color-text); }

.btn--danger {
  background: var(--gradient-danger);
  color: #fff;
  box-shadow: 0 4px 14px rgba(244, 63, 94, 0.32);
}
.btn--danger:not(:disabled):hover { box-shadow: 0 6px 20px rgba(244, 63, 94, 0.40); transform: translateY(-1px); }

.btn--success {
  background: var(--gradient-success);
  color: #fff;
  box-shadow: 0 4px 14px rgba(16, 185, 129, 0.32);
}
.btn--success:not(:disabled):hover { box-shadow: 0 6px 20px rgba(16, 185, 129, 0.40); transform: translateY(-1px); }

.btn-content--hidden { opacity: 0; }
.btn-spinner {
  position: absolute;
  width: 14px; height: 14px;
  border-radius: 50%;
  border: 2px solid currentColor;
  border-top-color: transparent;
  animation: spin 0.6s linear infinite;
}
</style>
