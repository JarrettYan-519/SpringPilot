<script setup>
defineProps({
  modelValue: { type: String, default: '' },
  label: { type: String, default: '' },
  placeholder: { type: String, default: '' },
  rows: { type: Number, default: 4 },
  disabled: { type: Boolean, default: false },
  error: { type: String, default: '' },
})
const emit = defineEmits(['update:modelValue'])
</script>

<template>
  <label class="field">
    <span v-if="label" class="field-label">{{ label }}</span>
    <textarea
      class="field-textarea"
      :class="{ 'field-textarea--invalid': !!error }"
      :value="modelValue"
      :rows="rows"
      :placeholder="placeholder"
      :disabled="disabled"
      @input="emit('update:modelValue', $event.target.value)"
    />
    <span v-if="error" class="field-error">{{ error }}</span>
  </label>
</template>

<style scoped>
.field { display: flex; flex-direction: column; gap: 6px; }
.field-label { font-size: var(--text-sm); font-weight: 500; color: var(--color-text); }
.field-textarea {
  width: 100%;
  border-radius: var(--radius-md);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  padding: 10px 12px;
  font-family: var(--font-sans);
  font-size: var(--text-base);
  line-height: var(--leading-normal);
  resize: vertical;
  transition: border var(--duration-fast) var(--ease-out), box-shadow var(--duration-fast) var(--ease-out);
}
.field-textarea::placeholder { color: var(--color-text-subtle); }
.field-textarea:focus { outline: none; border-color: var(--color-primary); box-shadow: var(--shadow-glow); }
.field-textarea--invalid { border-color: var(--color-danger); }
.field-error { font-size: var(--text-xs); color: var(--color-danger); }
</style>
