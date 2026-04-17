<script setup>
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Filler, Tooltip)

const props = defineProps({
  records: { type: Array, default: () => [] }, // [{ recorded_at, weight_kg }]
})

const chartData = computed(() => {
  const sorted = [...props.records].reverse()
  return {
    labels: sorted.map(r => r.recorded_at.slice(5, 10)),
    datasets: [{
      data: sorted.map(r => r.weight_kg),
      borderColor: '#8b5cf6',
      backgroundColor: 'rgba(139, 92, 246, 0.08)',
      borderWidth: 2,
      pointRadius: 3,
      pointBackgroundColor: '#8b5cf6',
      pointBorderWidth: 0,
      tension: 0.35,
      fill: true,
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
      callbacks: { label: (ctx) => `${ctx.parsed.y} kg` },
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
    <Line v-if="records.length" :data="chartData" :options="chartOptions" />
    <div v-else class="no-data text-subtle">暂无体重数据</div>
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
