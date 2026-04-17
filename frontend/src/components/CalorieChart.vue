<script setup>
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip)

const props = defineProps({
  logs: { type: Array, default: () => [] }, // [{ recorded_at, calories, meal_type }]
})

const chartData = computed(() => {
  const dayMap = {}
  for (const log of props.logs) {
    const day = log.recorded_at.slice(0, 10)
    dayMap[day] = (dayMap[day] || 0) + (log.calories || 0)
  }
  const days = Object.keys(dayMap).sort().slice(-7)
  return {
    labels: days.map(d => d.slice(5)),
    datasets: [{
      data: days.map(d => dayMap[d]),
      backgroundColor: 'rgba(236, 72, 153, 0.18)',
      borderColor: '#ec4899',
      borderWidth: 1.5,
      borderRadius: 6,
      borderSkipped: false,
    }],
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: 'rgba(255,255,255,0.95)',
      titleColor: '#18181b',
      bodyColor: '#18181b',
      borderColor: 'rgba(24,24,27,0.08)',
      borderWidth: 1,
      cornerRadius: 8,
      padding: 10,
      callbacks: { label: (ctx) => `${ctx.parsed.y} kcal` },
    },
  },
  scales: {
    x: { grid: { display: false }, ticks: { color: '#a1a1aa', font: { size: 11 } } },
    y: { grid: { color: 'rgba(24,24,27,0.04)' }, ticks: { color: '#a1a1aa', font: { size: 11 } } },
  },
}
</script>

<template>
  <div style="height: 220px">
    <Bar v-if="logs.length" :data="chartData" :options="chartOptions" />
    <div v-else class="no-data text-subtle">暂无饮食记录</div>
  </div>
</template>

<style scoped>
.no-data {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-sm);
}
</style>
