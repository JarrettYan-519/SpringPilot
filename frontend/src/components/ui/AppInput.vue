<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: [String, Number], default: '' },
  label: { type: String, default: '' },
  hint: { type: String, default: '' },
  error: { type: String, default: '' },
  type: { type: String, default: 'text' },
  placeholder: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
  required: { type: Boolean, default: false },
  size: { type: String, default: 'md' },
})
const emit = defineEmits(['update:modelValue'])

const invalid = computed(() => !!props.error)
</script>

<template>
  <label class="field">
    <span v-if="label" class="field-label">{{ label }}<span v-if="required" class="req">*</span></span>
    <input
      class="field-input"
      :class="[`field-input--${size}`, { 'field-input--invalid': invalid }]"
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      @input="emit('update:modelValue', $event.target.value)"
    />
    <span v-if="error" class="field-error">{{ error }}</span>
    <span v-else-if="hint" class="field-hint">{{ hint }}</span>
  </label>
</template>

<style scoped>
.field { display: flex; flex-direction: column; gap: 6px; }
.field-label { font-size: var(--text-sm); font-weight: 500; color: var(--color-text); }
.req { color: var(--color-danger); margin-left: 2px; }
.field-input {
  width: 100%;
  border-radius: var(--radius-md);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  color: var(--color-text);
  transition: border var(--duration-fast) var(--ease-out), box-shadow var(--duration-fast) var(--ease-out);
  font-family: var(--font-sans);
}
.field-input--sm { padding: 6px 10px; font-size: var(--text-sm); height: 32px; }
.field-input--md { padding: 8px 12px; font-size: var(--text-base); height: 38px; }
.field-input--lg { padding: 11px 14px; font-size: var(--text-md); height: 46px; }
.field-input::placeholder { color: var(--color-text-subtle); }
.field-input:focus { outline: none; border-color: var(--color-primary); box-shadow: var(--shadow-glow); }
.field-input:disabled { background: rgba(24, 24, 27, 0.03); cursor: not-allowed; }
.field-input--invalid { border-color: var(--color-danger); }
.field-input--invalid:focus { box-shadow: 0 0 0 4px rgba(244, 63, 94, 0.16); }
.field-hint { font-size: var(--text-xs); color: var(--color-text-subtle); }
.field-error { font-size: var(--text-xs); color: var(--color-danger); }
</style>
