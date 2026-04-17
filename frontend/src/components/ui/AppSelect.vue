<script setup>
import { computed } from 'vue'
import { Listbox, ListboxButton, ListboxOptions, ListboxOption } from '@headlessui/vue'

const props = defineProps({
  modelValue: { type: [String, Number, null], default: null },
  options: { type: Array, required: true }, // [{ value, label }]
  label: { type: String, default: '' },
  placeholder: { type: String, default: '请选择' },
  disabled: { type: Boolean, default: false },
})
const emit = defineEmits(['update:modelValue'])

const selectedLabel = computed(() => {
  const match = props.options.find(o => o.value === props.modelValue)
  return match ? match.label : ''
})
</script>

<template>
  <div class="select-wrap">
    <div v-if="label" class="select-label">{{ label }}</div>
    <Listbox :model-value="modelValue" :disabled="disabled" @update:model-value="v => emit('update:modelValue', v)">
      <div class="select-root">
        <ListboxButton class="select-button">
          <span v-if="selectedLabel" class="select-value">{{ selectedLabel }}</span>
          <span v-else class="select-placeholder">{{ placeholder }}</span>
          <span class="select-chevron" aria-hidden="true">⌄</span>
        </ListboxButton>
        <transition name="select-pop">
          <ListboxOptions class="select-options">
            <ListboxOption v-for="opt in options" :key="opt.value" :value="opt.value" v-slot="{ active, selected }">
              <li class="select-option" :class="{ 'select-option--active': active, 'select-option--selected': selected }">
                <span>{{ opt.label }}</span>
                <span v-if="selected" class="select-check" aria-hidden="true">✓</span>
              </li>
            </ListboxOption>
          </ListboxOptions>
        </transition>
      </div>
    </Listbox>
  </div>
</template>

<style scoped>
.select-wrap { display: flex; flex-direction: column; gap: 6px; }
.select-label { font-size: var(--text-sm); font-weight: 500; }
.select-root { position: relative; }
.select-button {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2);
  padding: 8px 12px;
  height: 38px;
  border-radius: var(--radius-md);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  font-family: var(--font-sans);
  font-size: var(--text-base);
  color: var(--color-text);
  cursor: pointer;
  transition: border var(--duration-fast) var(--ease-out), box-shadow var(--duration-fast) var(--ease-out);
}
.select-button:hover { border-color: var(--color-border-strong); }
.select-button:focus { outline: none; border-color: var(--color-primary); box-shadow: var(--shadow-glow); }
.select-placeholder { color: var(--color-text-subtle); }
.select-chevron { color: var(--color-text-muted); font-size: 12px; }
.select-options {
  position: absolute;
  top: calc(100% + 6px);
  left: 0; right: 0;
  background: var(--color-surface-elevated);
  backdrop-filter: blur(20px);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 4px;
  box-shadow: var(--shadow-md);
  max-height: 280px;
  overflow-y: auto;
  z-index: var(--z-dropdown);
  outline: none;
}
.select-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 10px;
  border-radius: var(--radius-sm);
  font-size: var(--text-base);
  cursor: pointer;
  transition: background var(--duration-fast) var(--ease-out);
}
.select-option--active { background: rgba(24, 24, 27, 0.05); }
.select-option--selected { color: var(--color-primary); font-weight: 500; }
.select-check { color: var(--color-primary); }
.select-pop-enter-active, .select-pop-leave-active { transition: opacity var(--duration-fast) var(--ease-out), transform var(--duration-fast) var(--ease-out); }
.select-pop-enter-from, .select-pop-leave-to { opacity: 0; transform: translateY(-4px); }
</style>
