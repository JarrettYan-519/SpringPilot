<script setup>
import { computed } from 'vue'

const props = defineProps({
  logs: { type: Array, default: () => [] }, // [{ recorded_at }]
})

const DAYS_SHOWN = 28

const heatmap = computed(() => {
  const dayMap = {}
  for (const log of props.logs) {
    const day = log.recorded_at.slice(0, 10)
    dayMap[day] = (dayMap[day] || 0) + 1
  }
  const cells = []
  const today = new Date()
  for (let i = DAYS_SHOWN - 1; i >= 0; i--) {
    const d = new Date(today.getTime() - i * 86400000)
    const key = d.toISOString().slice(0, 10)
    cells.push({
      key,
      count: dayMap[key] || 0,
      label: d.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }),
    })
  }
  return cells
})

function cellClass(count) {
  if (count === 0) return 'heat-0'
  if (count === 1) return 'heat-1'
  if (count === 2) return 'heat-2'
  return 'heat-3'
}
</script>

<template>
  <div class="heatmap">
    <div v-for="cell in heatmap" :key="cell.key" class="heat-cell" :class="cellClass(cell.count)" :title="`${cell.label}: ${cell.count} 次训练`" />
  </div>
</template>

<style scoped>
.heatmap { display: grid; grid-template-columns: repeat(7, 1fr); gap: 3px; }
.heat-cell {
  aspect-ratio: 1;
  border-radius: 3px;
  transition: background var(--duration-fast) var(--ease-out);
}
.heat-0 { background: rgba(24,24,27,0.04); }
.heat-1 { background: rgba(16, 185, 129, 0.25); }
.heat-2 { background: rgba(16, 185, 129, 0.5); }
.heat-3 { background: rgba(16, 185, 129, 0.8); }
</style>
