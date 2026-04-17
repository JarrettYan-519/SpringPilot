<script setup>
import VueDatePicker from '@vuepic/vue-datepicker'
import '@vuepic/vue-datepicker/dist/main.css'

defineProps({
  modelValue: { type: [Date, String, Array, null], default: null },
  label: { type: String, default: '' },
  placeholder: { type: String, default: '选择日期' },
  range: { type: Boolean, default: false },
  clearable: { type: Boolean, default: true },
})
const emit = defineEmits(['update:modelValue'])
</script>

<template>
  <div class="datepicker-wrap">
    <div v-if="label" class="datepicker-label">{{ label }}</div>
    <VueDatePicker
      :model-value="modelValue"
      :range="range"
      :clearable="clearable"
      :placeholder="placeholder"
      :enable-time-picker="false"
      :format="range ? 'yyyy-MM-dd ~ yyyy-MM-dd' : 'yyyy-MM-dd'"
      auto-apply
      locale="zh-CN"
      @update:model-value="v => emit('update:modelValue', v)"
    />
  </div>
</template>

<style>
/* Override library CSS via custom properties */
.dp__theme_light {
  --dp-background-color: var(--color-surface);
  --dp-text-color: var(--color-text);
  --dp-border-color: var(--color-border);
  --dp-border-color-hover: var(--color-border-strong);
  --dp-primary-color: #8b5cf6;
  --dp-menu-border-color: var(--color-border);
  --dp-border-radius: var(--radius-md);
  --dp-font-family: var(--font-sans);
  --dp-input-padding: 8px 12px;
}
.dp__input {
  border-radius: var(--radius-md);
  height: 38px;
  font-family: var(--font-sans);
  font-size: var(--text-base);
}
.dp__input:focus, .dp__input:hover { border-color: var(--color-primary); box-shadow: var(--shadow-glow); }
.dp__menu { border-radius: var(--radius-lg); box-shadow: var(--shadow-md); }
</style>

<style scoped>
.datepicker-wrap { display: flex; flex-direction: column; gap: 6px; }
.datepicker-label { font-size: var(--text-sm); font-weight: 500; }
</style>
