<script setup>
defineProps({
  modelValue: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
})
const emit = defineEmits(['update:modelValue'])
</script>

<template>
  <button
    type="button"
    class="switch"
    :class="{ 'switch--on': modelValue, 'switch--disabled': disabled }"
    :disabled="disabled"
    role="switch"
    :aria-checked="modelValue"
    @click="emit('update:modelValue', !modelValue)"
  >
    <span class="switch-thumb" />
  </button>
</template>

<style scoped>
.switch {
  width: 36px; height: 20px;
  border-radius: 999px;
  background: rgba(24, 24, 27, 0.14);
  position: relative;
  transition: background var(--duration-base) var(--ease-out);
  padding: 0;
}
.switch-thumb {
  position: absolute; top: 2px; left: 2px;
  width: 16px; height: 16px;
  border-radius: 50%;
  background: #fff;
  box-shadow: var(--shadow-sm);
  transition: left var(--duration-base) var(--ease-out);
}
.switch--on { background: var(--gradient-primary); }
.switch--on .switch-thumb { left: 18px; }
.switch--disabled { opacity: 0.55; cursor: not-allowed; }
</style>
