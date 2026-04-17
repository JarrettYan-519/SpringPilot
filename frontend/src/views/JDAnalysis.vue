<script setup>
import { ref } from 'vue'
import { aiApi } from '@/api/ai'
import { useSettingsStore } from '@/stores/settings'
import { useToast } from '@/composables/useToast'
import AppPageHeader from '@/components/ui/AppPageHeader.vue'
import AppCard from '@/components/ui/AppCard.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppTextarea from '@/components/ui/AppTextarea.vue'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import AppEmptyState from '@/components/ui/AppEmptyState.vue'
import AppBadge from '@/components/ui/AppBadge.vue'

const settings = useSettingsStore()
const toast = useToast()

const jdText = ref('')
const resumeText = ref('')
const analyzing = ref(false)
const result = ref(null)

async function analyze() {
  if (!jdText.value.trim()) {
    toast.warning('请输入职位描述')
    return
  }
  if (!settings.hasAnyLlmKey) {
    toast.error('请先在设置页面配置 AI 模型')
    return
  }
  analyzing.value = true
  result.value = null
  try {
    result.value = await aiApi.analyzeJd(jdText.value, resumeText.value || null)
  } catch (e) {
    toast.error(e.message)
  } finally {
    analyzing.value = false
  }
}
</script>

<template>
  <div>
    <AppPageHeader title="JD 分析" subtitle="粘贴职位描述，AI 提取关键技能并给出匹配建议" />

    <div class="analysis-grid">
      <AppCard title="输入">
        <div class="form-stack">
          <AppTextarea v-model="jdText" label="职位描述" :rows="8" placeholder="粘贴完整的职位描述..." />
          <AppTextarea v-model="resumeText" label="我的简历（可选）" :rows="4" placeholder="粘贴简历内容，AI 会分析匹配度..." />
          <div class="form-actions">
            <AppButton :loading="analyzing" :disabled="!jdText.trim()" @click="analyze">
              {{ analyzing ? '分析中...' : '开始分析' }}
            </AppButton>
          </div>
        </div>
      </AppCard>

      <div v-if="analyzing" class="loading-state"><AppSpinner :size="32" /></div>
      <AppEmptyState v-else-if="!result" icon="◎" title="等待分析" description="输入 JD 后点击分析按钮" />
      <template v-else>
        <div v-if="result.raw" class="result-cards">
          <AppCard title="AI 分析结果">
            <div class="result-raw">{{ result.raw }}</div>
          </AppCard>
        </div>

        <div v-else class="result-cards">
          <AppCard v-if="result.key_skills?.length" title="关键技能">
            <div class="skill-tags">
              <AppBadge v-for="skill in result.key_skills" :key="skill" variant="primary">{{ skill }}</AppBadge>
            </div>
          </AppCard>

          <AppCard v-if="result.requirements?.length" title="核心要求">
            <ul class="result-list">
              <li v-for="(req, i) in result.requirements" :key="i">{{ req }}</li>
            </ul>
          </AppCard>

          <AppCard v-if="result.match_analysis" title="匹配分析" glass>
            <p class="result-text">{{ result.match_analysis }}</p>
          </AppCard>

          <AppCard v-if="result.gaps?.length" title="差距">
            <ul class="result-list">
              <li v-for="(gap, i) in result.gaps" :key="i">
                <span class="gap-dot"></span>{{ gap }}
              </li>
            </ul>
          </AppCard>

          <AppCard v-if="result.suggestions?.length" title="建议">
            <ul class="result-list">
              <li v-for="(sug, i) in result.suggestions" :key="i">
                <span class="sug-dot"></span>{{ sug }}
              </li>
            </ul>
          </AppCard>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
.analysis-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); align-items: start; }
.form-stack { display: flex; flex-direction: column; gap: var(--space-3); }
.form-actions { display: flex; justify-content: flex-end; }
.loading-state { display: flex; justify-content: center; padding: var(--space-7); }
.result-cards { display: flex; flex-direction: column; gap: var(--space-3); }
.skill-tags { display: flex; flex-wrap: wrap; gap: var(--space-2); }
.result-list { display: flex; flex-direction: column; gap: var(--space-2); }
.result-list li {
  display: flex; align-items: flex-start; gap: var(--space-2);
  font-size: var(--text-sm); line-height: var(--leading-relaxed);
}
.gap-dot {
  flex-shrink: 0;
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--gradient-danger);
  margin-top: 7px;
}
.sug-dot {
  flex-shrink: 0;
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--gradient-success);
  margin-top: 7px;
}
.result-text { font-size: var(--text-sm); line-height: var(--leading-relaxed); white-space: pre-line; }
.result-raw { font-size: var(--text-sm); line-height: var(--leading-relaxed); white-space: pre-wrap; }
</style>
