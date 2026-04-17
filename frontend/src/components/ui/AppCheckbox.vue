<script setup>
defineProps({
  modelValue: { type: Boolean, default: false },
  label: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
})
const emit = defineEmits(['update:modelValue'])
</script>

<template>
  <label class="checkbox" :class="{ 'checkbox--disabled': disabled }">
    <input
      type="checkbox"
      class="checkbox-input"
      :checked="modelValue"
      :disabled="disabled"
      @change="emit('update:modelValue', $event.target.checked)"
    />
    <span class="checkbox-box">
      <svg v-if="modelValue" width="10" height="10" viewBox="0 0 10 10"><path d="M1 5l3 3 5-6" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
    </span>
    <span v-if="label" class="checkbox-label">{{ label }}</span>
  </label>
</template>

<style scoped>
.checkbox { display: inline-flex; align-items: center; gap: var(--space-2); cursor: pointer; font-size: var(--text-base); }
.checkbox--disabled { opacity: 0.55; cursor: not-allowed; }
.checkbox-input { position: absolute; opacity: 0; pointer-events: none; }
.checkbox-box {
  width: 18px; height: 18px;
  border-radius: 5px;
  border: 1.5px solid var(--color-border-strong);
  background: var(--color-surface);
  display: inline-flex; align-items: center; justify-content: center;
  transition: background var(--duration-fast) var(--ease-out), border var(--duration-fast) var(--ease-out);
}
.checkbox-input:checked + .checkbox-box {
  background: var(--gradient-primary);
  border-color: transparent;
}
.checkbox-input:focus-visible + .checkbox-box { box-shadow: var(--shadow-glow); }
.checkbox-label { color: var(--color-text); }
</style>
