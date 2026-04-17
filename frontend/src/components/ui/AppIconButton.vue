<script setup>
defineProps({
  size: { type: String, default: 'md' }, // sm | md | lg
  variant: { type: String, default: 'ghost' }, // ghost | solid
  disabled: { type: Boolean, default: false },
  ariaLabel: { type: String, required: true },
})
</script>

<template>
  <button class="icon-btn" :class="[`icon-btn--${size}`, `icon-btn--${variant}`]" :disabled="disabled" :aria-label="ariaLabel">
    <slot />
  </button>
</template>

<style scoped>
.icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  color: var(--color-text-muted);
  transition: background var(--duration-fast) var(--ease-out), color var(--duration-fast) var(--ease-out);
}
.icon-btn:not(:disabled):hover { background: rgba(24, 24, 27, 0.06); color: var(--color-text); }
.icon-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.icon-btn--sm { width: 28px; height: 28px; }
.icon-btn--md { width: 34px; height: 34px; }
.icon-btn--lg { width: 40px; height: 40px; }
.icon-btn--solid { background: var(--color-surface); border: 1px solid var(--color-border); box-shadow: var(--shadow-sm); }
</style>
