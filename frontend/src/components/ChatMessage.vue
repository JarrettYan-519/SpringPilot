<script setup>
defineProps({
  role: { type: String, required: true },
  content: { type: String, required: true },
})
</script>

<template>
  <div class="msg" :class="`msg--${role}`">
    <div class="msg-avatar" :class="`msg-avatar--${role}`">
      <template v-if="role === 'assistant'">AI</template>
      <template v-else>ME</template>
    </div>
    <div class="msg-bubble">
      <div class="msg-text">{{ content }}</div>
    </div>
  </div>
</template>

<style scoped>
.msg { display: flex; gap: var(--space-3); }
.msg--user { flex-direction: row-reverse; }
.msg-avatar {
  width: 32px; height: 32px;
  border-radius: var(--radius-full);
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 700; flex-shrink: 0;
}
.msg-avatar--assistant { background: var(--gradient-primary); color: #fff; }
.msg-avatar--user { background: rgba(24,24,27,0.08); color: var(--color-text-muted); }
.msg-bubble {
  max-width: 70%;
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-lg);
  font-size: var(--text-sm);
  line-height: var(--leading-relaxed);
}
.msg--assistant .msg-bubble {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-top-left-radius: 4px;
}
.msg--user .msg-bubble {
  background: var(--gradient-primary-soft);
  border-top-right-radius: 4px;
}
.msg-text { white-space: pre-wrap; word-break: break-word; }
</style>
