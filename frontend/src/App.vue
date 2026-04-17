<script setup>
import { RouterLink, RouterView } from 'vue-router'
import AppToastHost from '@/components/ui/AppToastHost.vue'

const navSections = [
  {
    items: [{ to: '/', label: '首页', icon: '⌂' }],
  },
  {
    label: '求职',
    items: [
      { to: '/applications', label: '投递记录', icon: '✦' },
      { to: '/study-tasks', label: '学习任务', icon: '✓' },
      { to: '/jd-analysis', label: 'JD 分析', icon: '◎' },
      { to: '/mock-interview', label: '模拟面试', icon: '◈' },
    ],
  },
  {
    label: '健身',
    items: [
      { to: '/fitness', label: '数据概览', icon: '◐' },
      { to: '/trainer-plans', label: '训练计划', icon: '◇' },
    ],
  },
  {
    label: '系统',
    items: [{ to: '/settings', label: '设置', icon: '⚙' }],
  },
]
</script>

<template>
  <div class="shell">
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-mark" aria-hidden="true"></div>
        <div class="brand-name">SpringPilot</div>
      </div>

      <nav class="nav">
        <div v-for="(section, si) in navSections" :key="si" class="nav-section">
          <div v-if="section.label" class="nav-section-label">{{ section.label }}</div>
          <ul>
            <li v-for="item in section.items" :key="item.to">
              <RouterLink :to="item.to" class="nav-link">
                <span class="nav-link-icon" aria-hidden="true">{{ item.icon }}</span>
                <span class="nav-link-label">{{ item.label }}</span>
              </RouterLink>
            </li>
          </ul>
        </div>
      </nav>

      <div class="sidebar-footer">
        <div class="footer-meta">春招 · 2026</div>
      </div>
    </aside>

    <main class="main">
      <RouterView v-slot="{ Component, route }">
        <transition name="route" mode="out-in">
          <component :is="Component" :key="route.fullPath" />
        </transition>
      </RouterView>
    </main>

    <AppToastHost />
  </div>
</template>

<style scoped>
.shell {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 232px;
  flex-shrink: 0;
  position: sticky;
  top: 0;
  height: 100vh;
  padding: var(--space-5) var(--space-4);
  background: var(--color-surface-glass);
  backdrop-filter: blur(24px) saturate(140%);
  -webkit-backdrop-filter: blur(24px) saturate(140%);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

.brand {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: 0 var(--space-2);
}

.brand-mark {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: var(--gradient-primary);
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.28);
}

.brand-name {
  font-size: var(--text-lg);
  font-weight: 700;
  letter-spacing: -0.015em;
}

.nav {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.nav-section-label {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.08em;
  color: var(--color-text-subtle);
  text-transform: uppercase;
  padding: 0 var(--space-3);
  margin-bottom: var(--space-2);
}

.nav ul {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: 8px 12px;
  border-radius: var(--radius-md);
  color: var(--color-text-muted);
  font-size: var(--text-base);
  font-weight: 500;
  transition: background var(--duration-fast) var(--ease-out), color var(--duration-fast) var(--ease-out);
}

.nav-link:hover {
  background: rgba(24, 24, 27, 0.04);
  color: var(--color-text);
}

.nav-link.router-link-active {
  color: var(--color-surface);
  background: var(--gradient-primary);
  box-shadow: 0 6px 18px rgba(139, 92, 246, 0.32);
}

.nav-link-icon {
  width: 20px;
  font-size: 14px;
  text-align: center;
  opacity: 0.9;
}

.sidebar-footer {
  padding: var(--space-3);
  color: var(--color-text-subtle);
  font-size: var(--text-xs);
}

.main {
  flex: 1;
  min-width: 0;
  padding: var(--space-6) var(--space-7);
  overflow-x: hidden;
}

.route-enter-active, .route-leave-active {
  transition: opacity var(--duration-base) var(--ease-out), transform var(--duration-base) var(--ease-out);
}
.route-enter-from { opacity: 0; transform: translateY(6px); }
.route-leave-to { opacity: 0; transform: translateY(-4px); }

@supports not (backdrop-filter: blur(1px)) {
  .sidebar {
    background: var(--color-surface);
  }
}
</style>
