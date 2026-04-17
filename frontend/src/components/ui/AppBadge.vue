<script setup>
defineProps({
  variant: { type: String, default: 'neutral' }, // neutral | primary | success | warning | danger | info
  soft: { type: Boolean, default: true },
})
</script>

<template>
  <span class="badge" :class="[`badge--${variant}`, { 'badge--soft': soft, 'badge--solid': !soft }]">
    <slot />
  </span>
</template>

<style scoped>
.badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 10px;
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: 600;
  letter-spacing: 0.01em;
  white-space: nowrap;
}
.badge--soft.badge--neutral { background: rgba(24, 24, 27, 0.06); color: var(--color-text-muted); }
.badge--soft.badge--primary { background: var(--gradient-primary-soft); color: var(--color-primary); }
.badge--soft.badge--success { background: var(--gradient-success-soft); color: var(--color-success); }
.badge--soft.badge--warning { background: var(--gradient-warning-soft); color: var(--color-warning); }
.badge--soft.badge--danger  { background: var(--gradient-danger-soft);  color: var(--color-danger); }
.badge--soft.badge--info    { background: var(--gradient-info-soft);    color: var(--color-info); }

.badge--solid { color: #fff; }
.badge--solid.badge--primary { background: var(--gradient-primary); }
.badge--solid.badge--success { background: var(--gradient-success); }
.badge--solid.badge--warning { background: var(--gradient-warning); }
.badge--solid.badge--danger  { background: var(--gradient-danger); }
.badge--solid.badge--info    { background: var(--gradient-info); }
.badge--solid.badge--neutral { background: #3f3f46; }
</style>
