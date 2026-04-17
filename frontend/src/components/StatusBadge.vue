<script setup>
import AppBadge from '@/components/ui/AppBadge.vue'
import { computed } from 'vue'

const props = defineProps({
  status: { type: String, required: true },
})

const STATUS_MAP = {
  Pending:        { variant: 'neutral',  label: '待处理' },
  Applied:        { variant: 'info',     label: '已投递' },
  'Written Test': { variant: 'warning',  label: '笔试' },
  Interviewing:   { variant: 'primary',  label: '面试中' },
  Offer:          { variant: 'success',  label: 'Offer' },
  Rejected:       { variant: 'danger',   label: '已拒绝' },
}

const info = computed(() => STATUS_MAP[props.status] || { variant: 'neutral', label: props.status })
</script>

<template>
  <AppBadge :variant="info.variant" soft>{{ info.label }}</AppBadge>
</template>
