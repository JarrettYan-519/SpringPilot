<script setup>
import { ref, nextTick } from 'vue'
import { aiApi } from '@/api/ai'
import { useSettingsStore } from '@/stores/settings'
import { useToast } from '@/composables/useToast'
import AppPageHeader from '@/components/ui/AppPageHeader.vue'
import AppCard from '@/components/ui/AppCard.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import ChatMessage from '@/components/ChatMessage.vue'

const settings = useSettingsStore()
const toast = useToast()

const position = ref('')
const started = ref(false)
const history = ref([])
const userInput = ref('')
const sending = ref(false)
const chatContainer = ref(null)

async function startInterview() {
  if (!position.value.trim()) {
    toast.warning('请输入目标职位')
    return
  }
  if (!settings.hasAnyLlmKey) {
    toast.error('请先在设置页面配置 AI 模型')
    return
  }
  started.value = true
  sending.value = true
  try {
    const res = await aiApi.mockInterview(
      [],
      `你好，我是来应聘${position.value}职位的，请开始面试。`,
    )
    history.value.push(
      { role: 'user', content: `你好，我是来应聘${position.value}职位的，请开始面试。` },
      { role: 'assistant', content: res.reply },
    )
    scrollToBottom()
  } catch (e) {
    toast.error(e.message)
    started.value = false
  } finally {
    sending.value = false
  }
}

async function sendMessage() {
  const text = userInput.value.trim()
  if (!text || sending.value) return
  userInput.value = ''
  history.value.push({ role: 'user', content: text })
  scrollToBottom()

  sending.value = true
  try {
    const res = await aiApi.mockInterview(history.value.slice(0, -1), text)
    history.value.push({ role: 'assistant', content: res.reply })
    scrollToBottom()
  } catch (e) {
    toast.error(e.message)
  } finally {
    sending.value = false
  }
}

function resetInterview() {
  started.value = false
  history.value = []
  position.value = ''
}

function scrollToBottom() {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

function handleKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}
</script>

<template>
  <div>
    <AppPageHeader title="模拟面试" subtitle="AI 扮演面试官，进行实时技术面试">
      <template v-if="started" #actions>
        <AppButton variant="ghost" @click="resetInterview">重新开始</AppButton>
      </template>
    </AppPageHeader>

    <AppCard v-if="!started" glass>
      <div class="start-screen">
        <div class="start-icon" aria-hidden="true">◈</div>
        <h2 class="heading-2">开始面试</h2>
        <p class="text-muted" style="max-width: 400px; text-align: center;">输入你的目标职位，AI 将作为面试官与你进行实时对话</p>
        <div class="start-form">
          <AppInput v-model="position" placeholder="例如：后端工程师" size="lg" @keydown.enter="startInterview" />
          <AppButton size="lg" :disabled="!position.trim()" @click="startInterview">开始</AppButton>
        </div>
      </div>
    </AppCard>

    <template v-else>
      <div class="chat-shell">
        <div ref="chatContainer" class="chat-messages">
          <ChatMessage v-for="(msg, i) in history" :key="i" :role="msg.role" :content="msg.content" />
          <div v-if="sending" class="typing-indicator">
            <div class="msg-avatar msg-avatar--assistant">AI</div>
            <div class="typing-dots"><span></span><span></span><span></span></div>
          </div>
        </div>
        <div class="chat-input-bar">
          <textarea
            v-model="userInput"
            class="chat-input"
            :disabled="sending"
            rows="1"
            placeholder="输入你的回答..."
            @keydown="handleKeydown"
          />
          <AppButton size="sm" :loading="sending" :disabled="!userInput.trim()" @click="sendMessage">发送</AppButton>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.start-screen {
  display: flex; flex-direction: column; align-items: center;
  padding: var(--space-7) var(--space-5); gap: var(--space-4);
}
.start-icon {
  width: 64px; height: 64px; border-radius: var(--radius-full);
  background: var(--gradient-primary-soft);
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 28px;
}
.start-form { display: flex; gap: var(--space-2); width: 100%; max-width: 420px; margin-top: var(--space-2); }

.chat-shell {
  display: flex; flex-direction: column;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  height: calc(100vh - 200px);
  overflow: hidden;
}
.chat-messages {
  flex: 1; overflow-y: auto; padding: var(--space-5);
  display: flex; flex-direction: column; gap: var(--space-4);
}
.chat-input-bar {
  display: flex; align-items: center; gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  border-top: 1px solid var(--color-border);
  background: var(--color-surface);
}
.chat-input {
  flex: 1;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 8px 12px;
  font-family: var(--font-sans);
  font-size: var(--text-base);
  resize: none;
  line-height: var(--leading-normal);
  max-height: 120px;
}
.chat-input:focus { outline: none; border-color: var(--color-primary); box-shadow: var(--shadow-glow); }

.typing-indicator { display: flex; align-items: center; gap: var(--space-3); }
.msg-avatar {
  width: 32px; height: 32px; border-radius: var(--radius-full);
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 700;
}
.msg-avatar--assistant { background: var(--gradient-primary); color: #fff; }
.typing-dots { display: flex; gap: 4px; }
.typing-dots span {
  width: 7px; height: 7px; border-radius: 50%; background: var(--color-text-subtle);
  animation: pulse 1.2s ease-in-out infinite;
}
.typing-dots span:nth-child(2) { animation-delay: 0.15s; }
.typing-dots span:nth-child(3) { animation-delay: 0.3s; }
</style>
