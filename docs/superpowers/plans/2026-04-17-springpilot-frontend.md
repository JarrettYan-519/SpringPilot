# SpringPilot Frontend Pages Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the 9 placeholder Vue views with a production-quality, custom-styled SPA that consumes the already-shipped backend APIs (`applications`, `study-tasks`, `weight`, `diet`, `training`, `settings`, `ai`, `trainer-plans`).

**Architecture:** Design-system-first. Before any page: (1) CSS-variable design tokens, (2) base UI components, (3) API modules + notification store. Pages built on top — each composes base components, calls API modules via Pinia or direct, and renders via a shared page shell. No UI library used for styling; `@headlessui/vue` and `@vuepic/vue-datepicker` supply interaction logic only (their default styles are fully overridden).

**Design language:**
- Arc / Raycast gradient accents + Apple HIG large rounded corners, **light mode only**
- Primary gradient: `#6366f1` (indigo) → `#a855f7` (violet) → `#ec4899` (pink)
- Semantic gradients: success `#10b981→#14b8a6`, warning `#f59e0b→#f97316`, danger `#f43f5e→#ec4899`
- Neutral palette: warm-white base `#fafaf9` → ink `#18181b`
- Radii: card 16px / button 10px / modal 20px / input 10px
- Frosted glass (`backdrop-filter: blur(20px)` + semi-transparent bg) on sidebar, modals, popovers
- Typography: Inter (Latin) + PingFang SC → Noto Sans SC (CJK fallback)
- Shadow discipline: 1px border + faint `rgba(0,0,0,0.04)` fill; no heavy drop shadows

**Tech Stack:** Vue 3 (Composition API), Vite, Vue Router 4, Pinia 2, Axios, Chart.js 4 + vue-chartjs 5, @headlessui/vue 1.7, @vuepic/vue-datepicker 7, Inter + PingFang SC

**Backend surface (locked):** All endpoints exist under `/api` prefix with FastAPI. Key endpoints referenced in this plan:
- `GET/POST/PATCH/DELETE /api/applications`, `POST /api/applications/{id}/status`
- `GET/POST/PATCH/DELETE /api/study-tasks`
- `GET/POST/DELETE /api/weight`, `/api/diet` (`?day=`), `/api/training` (+`PATCH`)
- `GET /api/settings`, `GET/PUT /api/settings/{key}`
- `POST /api/ai/{analyze-jd|generate-questions|mock-interview|estimate-calories|daily-advice}`
- `GET/POST /api/trainer-plans` (multipart), `DELETE /api/trainer-plans/{id}`

---

## File Structure (new / modified)

```
frontend/
├── index.html                                   # MODIFY: load Inter font
├── package.json                                 # MODIFY: add headlessui + datepicker
└── src/
    ├── main.js                                  # MODIFY: import global styles
    ├── App.vue                                  # REWRITE: frosted-glass shell
    ├── styles/
    │   ├── tokens.css                           # NEW: CSS custom properties
    │   ├── reset.css                            # NEW: modern reset
    │   └── globals.css                          # NEW: body gradient mesh + utilities
    ├── api/
    │   ├── client.js                            # keep
    │   ├── applications.js                      # NEW
    │   ├── studyTasks.js                        # NEW
    │   ├── fitness.js                           # NEW (weight / diet / training)
    │   ├── ai.js                                # NEW
    │   ├── settings.js                          # NEW
    │   └── trainerPlans.js                      # NEW
    ├── stores/
    │   ├── settings.js                          # MODIFY: expand profile + llm schema
    │   └── notifications.js                     # NEW: toast queue
    ├── composables/
    │   ├── useToast.js                          # NEW: thin wrapper over notifications store
    │   └── useAsync.js                          # NEW: loading/error state helper
    ├── components/
    │   ├── ui/
    │   │   ├── AppButton.vue                    # NEW
    │   │   ├── AppIconButton.vue                # NEW
    │   │   ├── AppInput.vue                     # NEW
    │   │   ├── AppTextarea.vue                  # NEW
    │   │   ├── AppSelect.vue                    # NEW (headless Listbox)
    │   │   ├── AppCheckbox.vue                  # NEW
    │   │   ├── AppSwitch.vue                    # NEW
    │   │   ├── AppCard.vue                      # NEW
    │   │   ├── AppModal.vue                     # NEW (headless Dialog)
    │   │   ├── AppConfirmDialog.vue             # NEW
    │   │   ├── AppBadge.vue                     # NEW
    │   │   ├── AppTag.vue                       # NEW
    │   │   ├── AppEmptyState.vue                # NEW
    │   │   ├── AppSpinner.vue                   # NEW
    │   │   ├── AppSkeleton.vue                  # NEW
    │   │   ├── AppPageHeader.vue                # NEW
    │   │   ├── AppTabs.vue                      # NEW
    │   │   ├── AppToastHost.vue                 # NEW (renders queue)
    │   │   └── AppDatePicker.vue                # NEW (styled @vuepic/vue-datepicker)
    │   ├── StatusBadge.vue                      # NEW (Application.status → gradient badge)
    │   ├── WeightChart.vue                      # NEW (Chart.js line)
    │   ├── CalorieChart.vue                     # NEW (Chart.js bar)
    │   ├── TrainingHeatmap.vue                  # NEW (CSS grid heatmap)
    │   └── ChatMessage.vue                      # NEW (Mock interview bubble)
    └── views/
        ├── Dashboard.vue                        # REWRITE
        ├── Applications.vue                     # REWRITE
        ├── ApplicationDetail.vue                # REWRITE
        ├── StudyTasks.vue                       # REWRITE
        ├── MockInterview.vue                    # REWRITE
        ├── JDAnalysis.vue                       # REWRITE
        ├── FitnessOverview.vue                  # REWRITE
        ├── TrainerPlans.vue                     # REWRITE
        └── Settings.vue                         # REWRITE
```

---

## Design Token Reference (Task 10 establishes; subsequent tasks consume)

| Token | Value | Purpose |
|---|---|---|
| `--color-bg` | `#fafaf9` | Page base |
| `--color-surface` | `#ffffff` | Card / panel fill |
| `--color-surface-glass` | `rgba(255,255,255,0.72)` | Frosted glass surfaces |
| `--color-border` | `rgba(24,24,27,0.08)` | Hairline borders |
| `--color-border-strong` | `rgba(24,24,27,0.14)` | Focus / emphasis borders |
| `--color-text` | `#18181b` | Primary text |
| `--color-text-muted` | `#71717a` | Secondary text |
| `--color-text-subtle` | `#a1a1aa` | Hints, placeholders |
| `--gradient-primary` | `linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%)` | Primary buttons, active nav |
| `--gradient-success` | `linear-gradient(135deg, #10b981, #14b8a6)` | Success states |
| `--gradient-warning` | `linear-gradient(135deg, #f59e0b, #f97316)` | Warning states |
| `--gradient-danger` | `linear-gradient(135deg, #f43f5e, #ec4899)` | Destructive actions |
| `--gradient-info` | `linear-gradient(135deg, #3b82f6, #06b6d4)` | Info accents |
| `--gradient-mesh` | radial overlays behind shell | Body background |
| `--radius-sm` | `6px` | Tags, small chips |
| `--radius-md` | `10px` | Buttons, inputs |
| `--radius-lg` | `16px` | Cards |
| `--radius-xl` | `20px` | Modals |
| `--radius-full` | `9999px` | Pills, avatars |
| `--shadow-sm` | `0 1px 2px rgba(24,24,27,0.04)` | Subtle lift |
| `--shadow-md` | `0 4px 16px rgba(24,24,27,0.06)` | Cards, dropdowns |
| `--shadow-lg` | `0 12px 48px rgba(24,24,27,0.12)` | Modals |
| `--space-1..8` | 4/8/12/16/24/32/48/64 px | Spacing scale |
| `--font-sans` | `'Inter', 'PingFang SC', 'Noto Sans SC', system-ui, sans-serif` | Primary |
| `--font-mono` | `'JetBrains Mono', 'SF Mono', Menlo, monospace` | Code |
| `--duration-fast` | `120ms` | Micro-interactions |
| `--duration-base` | `220ms` | Standard |
| `--ease-out` | `cubic-bezier(0.16, 1, 0.3, 1)` | Hover/enter |

---

## Task 10: Design System Foundation

**Files:**
- Create: `frontend/src/styles/tokens.css`
- Create: `frontend/src/styles/reset.css`
- Create: `frontend/src/styles/globals.css`
- Modify: `frontend/src/main.js`
- Modify: `frontend/index.html`
- Modify: `frontend/src/App.vue`

- [ ] **Step 1: Add Inter font loader to `frontend/index.html`**

Replace the `<head>` block in `frontend/index.html` with:

```html
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8">
    <link rel="icon" href="/favicon.ico">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap">
    <title>SpringPilot</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
  </body>
</html>
```

- [ ] **Step 2: Create `frontend/src/styles/tokens.css`**

```css
:root {
  /* Palette — neutrals */
  --color-bg: #fafaf9;
  --color-surface: #ffffff;
  --color-surface-glass: rgba(255, 255, 255, 0.72);
  --color-surface-elevated: rgba(255, 255, 255, 0.92);
  --color-border: rgba(24, 24, 27, 0.08);
  --color-border-strong: rgba(24, 24, 27, 0.14);
  --color-text: #18181b;
  --color-text-muted: #71717a;
  --color-text-subtle: #a1a1aa;

  /* Brand — single-stop fallbacks for text/icon use */
  --color-primary: #8b5cf6;
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-danger: #f43f5e;
  --color-info: #3b82f6;

  /* Gradients */
  --gradient-primary: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
  --gradient-primary-soft: linear-gradient(135deg, rgba(99, 102, 241, 0.12), rgba(236, 72, 153, 0.12));
  --gradient-success: linear-gradient(135deg, #10b981, #14b8a6);
  --gradient-success-soft: linear-gradient(135deg, rgba(16, 185, 129, 0.12), rgba(20, 184, 166, 0.12));
  --gradient-warning: linear-gradient(135deg, #f59e0b, #f97316);
  --gradient-warning-soft: linear-gradient(135deg, rgba(245, 158, 11, 0.12), rgba(249, 115, 22, 0.12));
  --gradient-danger: linear-gradient(135deg, #f43f5e, #ec4899);
  --gradient-danger-soft: linear-gradient(135deg, rgba(244, 63, 94, 0.12), rgba(236, 72, 153, 0.12));
  --gradient-info: linear-gradient(135deg, #3b82f6, #06b6d4);
  --gradient-info-soft: linear-gradient(135deg, rgba(59, 130, 246, 0.12), rgba(6, 182, 212, 0.12));

  /* Radii */
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 16px;
  --radius-xl: 20px;
  --radius-full: 9999px;

  /* Shadows — minimal, non-skeuomorphic */
  --shadow-sm: 0 1px 2px rgba(24, 24, 27, 0.04);
  --shadow-md: 0 4px 16px rgba(24, 24, 27, 0.06);
  --shadow-lg: 0 12px 48px rgba(24, 24, 27, 0.12);
  --shadow-glow: 0 0 0 4px rgba(139, 92, 246, 0.16);

  /* Spacing scale (4px base) */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 24px;
  --space-6: 32px;
  --space-7: 48px;
  --space-8: 64px;

  /* Typography */
  --font-sans: 'Inter', 'PingFang SC', 'Noto Sans SC', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', 'SF Mono', Menlo, monospace;

  --text-xs: 12px;
  --text-sm: 13px;
  --text-base: 14px;
  --text-md: 15px;
  --text-lg: 17px;
  --text-xl: 20px;
  --text-2xl: 24px;
  --text-3xl: 32px;

  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.7;

  /* Motion */
  --duration-fast: 120ms;
  --duration-base: 220ms;
  --duration-slow: 420ms;
  --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);

  /* Z-index */
  --z-sticky: 100;
  --z-dropdown: 200;
  --z-modal: 1000;
  --z-toast: 2000;
}
```

- [ ] **Step 3: Create `frontend/src/styles/reset.css`**

```css
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html, body, #app {
  height: 100%;
}

html {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
}

body {
  font-family: var(--font-sans);
  font-size: var(--text-base);
  line-height: var(--leading-normal);
  color: var(--color-text);
  background: var(--color-bg);
}

button {
  font: inherit;
  color: inherit;
  background: none;
  border: none;
  cursor: pointer;
}

input, textarea, select {
  font: inherit;
  color: inherit;
}

a {
  color: inherit;
  text-decoration: none;
}

img, svg {
  display: block;
  max-width: 100%;
}

ul, ol {
  list-style: none;
}

:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
  border-radius: var(--radius-sm);
}

::selection {
  background: rgba(139, 92, 246, 0.2);
  color: var(--color-text);
}
```

- [ ] **Step 4: Create `frontend/src/styles/globals.css`**

```css
/* Background mesh — soft radial gradients to give frosted glass something to blur */
body {
  background-color: var(--color-bg);
  background-image:
    radial-gradient(at 12% 8%, rgba(99, 102, 241, 0.10) 0px, transparent 45%),
    radial-gradient(at 88% 16%, rgba(236, 72, 153, 0.08) 0px, transparent 42%),
    radial-gradient(at 72% 92%, rgba(20, 184, 166, 0.08) 0px, transparent 45%);
  background-attachment: fixed;
}

/* Typography utilities */
.heading-1 { font-size: var(--text-3xl); font-weight: 700; line-height: var(--leading-tight); letter-spacing: -0.02em; }
.heading-2 { font-size: var(--text-2xl); font-weight: 600; line-height: var(--leading-tight); letter-spacing: -0.015em; }
.heading-3 { font-size: var(--text-xl); font-weight: 600; line-height: var(--leading-tight); }
.text-muted { color: var(--color-text-muted); }
.text-subtle { color: var(--color-text-subtle); }
.text-gradient {
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

/* Scrollbar — refined */
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(24, 24, 27, 0.12); border-radius: 8px; border: 2px solid transparent; background-clip: padding-box; }
::-webkit-scrollbar-thumb:hover { background: rgba(24, 24, 27, 0.2); background-clip: padding-box; border: 2px solid transparent; }

/* Animation keyframes reused across components */
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideUp { from { transform: translateY(8px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
@keyframes slideDown { from { transform: translateY(-8px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
@keyframes pulse { 0%, 100% { opacity: 0.6; } 50% { opacity: 1; } }
@keyframes spin { to { transform: rotate(360deg); } }

/* Fade/slide entrance helper */
.enter-fade { animation: fadeIn var(--duration-base) var(--ease-out); }
.enter-up { animation: slideUp var(--duration-base) var(--ease-out); }

/* Layout helpers */
.stack { display: flex; flex-direction: column; }
.row { display: flex; align-items: center; }
.gap-1 { gap: var(--space-1); }
.gap-2 { gap: var(--space-2); }
.gap-3 { gap: var(--space-3); }
.gap-4 { gap: var(--space-4); }
.gap-5 { gap: var(--space-5); }
.gap-6 { gap: var(--space-6); }
```

- [ ] **Step 5: Import styles in `frontend/src/main.js`**

Replace the file content:

```js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'

import './styles/reset.css'
import './styles/tokens.css'
import './styles/globals.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
```

- [ ] **Step 6: Rewrite `frontend/src/App.vue` with frosted-glass shell**

Replace the entire file content:

```vue
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
  color: #fff;
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
</style>
```

- [ ] **Step 7: Create placeholder for `AppToastHost`**

`App.vue` imports `AppToastHost` which will be defined in Task 11. To keep the app runnable between tasks, create a stub now.

Create `frontend/src/components/ui/AppToastHost.vue`:

```vue
<template>
  <div />
</template>
```

- [ ] **Step 8: Run dev server and verify visually**

```bash
cd /Users/jarrett/Desktop/SpringPilot/frontend
npm run dev
```

Open http://localhost:5173. Expected:
- Warm off-white background with subtle pinkish / indigo / teal glow through the body
- Left sidebar: translucent white, blurred — gradient-glow logo, four sections with labels 求职 / 健身 / 系统
- Active nav item: gradient pill with soft purple shadow
- Clicking each link still shows the old "Coming soon..." placeholder (pages not rebuilt yet)
- Route transitions: subtle 6px slide + fade

- [ ] **Step 9: Commit**

```bash
cd /Users/jarrett/Desktop/SpringPilot
git add frontend/index.html frontend/src/main.js frontend/src/App.vue frontend/src/styles frontend/src/components/ui/AppToastHost.vue
git commit -m "feat(frontend): establish design system tokens and frosted-glass shell"
```

---

## Task 11: Base UI Components

**Files:**
- Modify: `frontend/package.json` (add `@headlessui/vue`, `@vuepic/vue-datepicker`)
- Create: `frontend/src/components/ui/AppButton.vue`
- Create: `frontend/src/components/ui/AppIconButton.vue`
- Create: `frontend/src/components/ui/AppInput.vue`
- Create: `frontend/src/components/ui/AppTextarea.vue`
- Create: `frontend/src/components/ui/AppSelect.vue`
- Create: `frontend/src/components/ui/AppCheckbox.vue`
- Create: `frontend/src/components/ui/AppSwitch.vue`
- Create: `frontend/src/components/ui/AppCard.vue`
- Create: `frontend/src/components/ui/AppModal.vue`
- Create: `frontend/src/components/ui/AppConfirmDialog.vue`
- Create: `frontend/src/components/ui/AppBadge.vue`
- Create: `frontend/src/components/ui/AppTag.vue`
- Create: `frontend/src/components/ui/AppEmptyState.vue`
- Create: `frontend/src/components/ui/AppSpinner.vue`
- Create: `frontend/src/components/ui/AppSkeleton.vue`
- Create: `frontend/src/components/ui/AppPageHeader.vue`
- Create: `frontend/src/components/ui/AppTabs.vue`
- Create: `frontend/src/components/ui/AppDatePicker.vue`
- Replace: `frontend/src/components/ui/AppToastHost.vue` (stub → real)

- [ ] **Step 1: Install headless dependencies**

```bash
cd /Users/jarrett/Desktop/SpringPilot/frontend
npm install @headlessui/vue@^1.7.23 @vuepic/vue-datepicker@^7.4.0
```

Verify `frontend/package.json` now contains both under `dependencies`.

- [ ] **Step 2: Create `AppButton.vue`**

```vue
<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: { type: String, default: 'primary' }, // primary | secondary | ghost | danger | success
  size: { type: String, default: 'md' },          // sm | md | lg
  loading: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  type: { type: String, default: 'button' },
  block: { type: Boolean, default: false },
})

const classes = computed(() => [
  'btn',
  `btn--${props.variant}`,
  `btn--${props.size}`,
  { 'btn--block': props.block, 'btn--loading': props.loading },
])
</script>

<template>
  <button :type="type" :class="classes" :disabled="disabled || loading">
    <span v-if="loading" class="btn-spinner" aria-hidden="true"></span>
    <span class="btn-content" :class="{ 'btn-content--hidden': loading }">
      <slot />
    </span>
  </button>
</template>

<style scoped>
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  border-radius: var(--radius-md);
  font-weight: 600;
  letter-spacing: -0.01em;
  transition: transform var(--duration-fast) var(--ease-out), box-shadow var(--duration-fast) var(--ease-out), background var(--duration-fast) var(--ease-out), color var(--duration-fast) var(--ease-out);
  white-space: nowrap;
  position: relative;
}
.btn:disabled { cursor: not-allowed; opacity: 0.55; }
.btn:not(:disabled):active { transform: scale(0.98); }
.btn--block { width: 100%; }

.btn--sm { padding: 6px 12px; font-size: var(--text-sm); height: 30px; }
.btn--md { padding: 8px 16px; font-size: var(--text-base); height: 36px; }
.btn--lg { padding: 11px 20px; font-size: var(--text-md); height: 44px; }

.btn--primary {
  background: var(--gradient-primary);
  color: #fff;
  box-shadow: 0 4px 14px rgba(139, 92, 246, 0.32);
}
.btn--primary:not(:disabled):hover { box-shadow: 0 6px 20px rgba(139, 92, 246, 0.40); transform: translateY(-1px); }

.btn--secondary {
  background: var(--color-surface);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
}
.btn--secondary:not(:disabled):hover { border-color: var(--color-border-strong); background: #fff; }

.btn--ghost { background: transparent; color: var(--color-text-muted); }
.btn--ghost:not(:disabled):hover { background: rgba(24, 24, 27, 0.05); color: var(--color-text); }

.btn--danger {
  background: var(--gradient-danger);
  color: #fff;
  box-shadow: 0 4px 14px rgba(244, 63, 94, 0.32);
}
.btn--danger:not(:disabled):hover { box-shadow: 0 6px 20px rgba(244, 63, 94, 0.40); transform: translateY(-1px); }

.btn--success {
  background: var(--gradient-success);
  color: #fff;
  box-shadow: 0 4px 14px rgba(16, 185, 129, 0.32);
}
.btn--success:not(:disabled):hover { box-shadow: 0 6px 20px rgba(16, 185, 129, 0.40); transform: translateY(-1px); }

.btn-content--hidden { opacity: 0; }
.btn-spinner {
  position: absolute;
  width: 14px; height: 14px;
  border-radius: 50%;
  border: 2px solid currentColor;
  border-top-color: transparent;
  animation: spin 0.6s linear infinite;
}
</style>
```

- [ ] **Step 3: Create `AppIconButton.vue`** (for header actions, close, etc.)

```vue
<script setup>
defineProps({
  size: { type: String, default: 'md' }, // sm | md | lg
  variant: { type: String, default: 'ghost' }, // ghost | solid
  disabled: { type: Boolean, default: false },
  ariaLabel: { type: String, required: true },
})
</script>

<template>
  <button class="icon-btn" :class="[`icon-btn--${size}`, `icon-btn--${variant}`]" :disabled="disabled" :aria-label="ariaLabel">
    <slot />
  </button>
</template>

<style scoped>
.icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  color: var(--color-text-muted);
  transition: background var(--duration-fast) var(--ease-out), color var(--duration-fast) var(--ease-out);
}
.icon-btn:not(:disabled):hover { background: rgba(24, 24, 27, 0.06); color: var(--color-text); }
.icon-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.icon-btn--sm { width: 28px; height: 28px; }
.icon-btn--md { width: 34px; height: 34px; }
.icon-btn--lg { width: 40px; height: 40px; }
.icon-btn--solid { background: var(--color-surface); border: 1px solid var(--color-border); box-shadow: var(--shadow-sm); }
</style>
```

- [ ] **Step 4: Create `AppInput.vue`**

```vue
<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: [String, Number], default: '' },
  label: { type: String, default: '' },
  hint: { type: String, default: '' },
  error: { type: String, default: '' },
  type: { type: String, default: 'text' },
  placeholder: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
  required: { type: Boolean, default: false },
  size: { type: String, default: 'md' },
})
const emit = defineEmits(['update:modelValue'])

const invalid = computed(() => !!props.error)
</script>

<template>
  <label class="field">
    <span v-if="label" class="field-label">{{ label }}<span v-if="required" class="req">*</span></span>
    <input
      class="field-input"
      :class="[`field-input--${size}`, { 'field-input--invalid': invalid }]"
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      @input="emit('update:modelValue', $event.target.value)"
    />
    <span v-if="error" class="field-error">{{ error }}</span>
    <span v-else-if="hint" class="field-hint">{{ hint }}</span>
  </label>
</template>

<style scoped>
.field { display: flex; flex-direction: column; gap: 6px; }
.field-label { font-size: var(--text-sm); font-weight: 500; color: var(--color-text); }
.req { color: var(--color-danger); margin-left: 2px; }
.field-input {
  width: 100%;
  border-radius: var(--radius-md);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  color: var(--color-text);
  transition: border var(--duration-fast) var(--ease-out), box-shadow var(--duration-fast) var(--ease-out);
  font-family: var(--font-sans);
}
.field-input--sm { padding: 6px 10px; font-size: var(--text-sm); height: 32px; }
.field-input--md { padding: 8px 12px; font-size: var(--text-base); height: 38px; }
.field-input--lg { padding: 11px 14px; font-size: var(--text-md); height: 46px; }
.field-input::placeholder { color: var(--color-text-subtle); }
.field-input:focus { outline: none; border-color: var(--color-primary); box-shadow: var(--shadow-glow); }
.field-input:disabled { background: rgba(24, 24, 27, 0.03); cursor: not-allowed; }
.field-input--invalid { border-color: var(--color-danger); }
.field-input--invalid:focus { box-shadow: 0 0 0 4px rgba(244, 63, 94, 0.16); }
.field-hint { font-size: var(--text-xs); color: var(--color-text-subtle); }
.field-error { font-size: var(--text-xs); color: var(--color-danger); }
</style>
```

- [ ] **Step 5: Create `AppTextarea.vue`**

```vue
<script setup>
defineProps({
  modelValue: { type: String, default: '' },
  label: { type: String, default: '' },
  placeholder: { type: String, default: '' },
  rows: { type: Number, default: 4 },
  disabled: { type: Boolean, default: false },
  error: { type: String, default: '' },
})
const emit = defineEmits(['update:modelValue'])
</script>

<template>
  <label class="field">
    <span v-if="label" class="field-label">{{ label }}</span>
    <textarea
      class="field-textarea"
      :class="{ 'field-textarea--invalid': !!error }"
      :value="modelValue"
      :rows="rows"
      :placeholder="placeholder"
      :disabled="disabled"
      @input="emit('update:modelValue', $event.target.value)"
    />
    <span v-if="error" class="field-error">{{ error }}</span>
  </label>
</template>

<style scoped>
.field { display: flex; flex-direction: column; gap: 6px; }
.field-label { font-size: var(--text-sm); font-weight: 500; color: var(--color-text); }
.field-textarea {
  width: 100%;
  border-radius: var(--radius-md);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  padding: 10px 12px;
  font-family: var(--font-sans);
  font-size: var(--text-base);
  line-height: var(--leading-normal);
  resize: vertical;
  transition: border var(--duration-fast) var(--ease-out), box-shadow var(--duration-fast) var(--ease-out);
}
.field-textarea::placeholder { color: var(--color-text-subtle); }
.field-textarea:focus { outline: none; border-color: var(--color-primary); box-shadow: var(--shadow-glow); }
.field-textarea--invalid { border-color: var(--color-danger); }
.field-error { font-size: var(--text-xs); color: var(--color-danger); }
</style>
```

- [ ] **Step 6: Create `AppSelect.vue`** (headless Listbox)

```vue
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
```

- [ ] **Step 7: Create `AppCheckbox.vue`**

```vue
<script setup>
defineProps({
  modelValue: { type: Boolean, default: false },
  label: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
})
const emit = defineEmits(['update:modelValue'])
</script>

<template>
  <label class="checkbox" :class="{ 'checkbox--disabled': disabled }">
    <input
      type="checkbox"
      class="checkbox-input"
      :checked="modelValue"
      :disabled="disabled"
      @change="emit('update:modelValue', $event.target.checked)"
    />
    <span class="checkbox-box">
      <svg v-if="modelValue" width="10" height="10" viewBox="0 0 10 10"><path d="M1 5l3 3 5-6" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
    </span>
    <span v-if="label" class="checkbox-label">{{ label }}</span>
  </label>
</template>

<style scoped>
.checkbox { display: inline-flex; align-items: center; gap: var(--space-2); cursor: pointer; font-size: var(--text-base); }
.checkbox--disabled { opacity: 0.55; cursor: not-allowed; }
.checkbox-input { position: absolute; opacity: 0; pointer-events: none; }
.checkbox-box {
  width: 18px; height: 18px;
  border-radius: 5px;
  border: 1.5px solid var(--color-border-strong);
  background: var(--color-surface);
  display: inline-flex; align-items: center; justify-content: center;
  transition: background var(--duration-fast) var(--ease-out), border var(--duration-fast) var(--ease-out);
}
.checkbox-input:checked + .checkbox-box {
  background: var(--gradient-primary);
  border-color: transparent;
}
.checkbox-input:focus-visible + .checkbox-box { box-shadow: var(--shadow-glow); }
.checkbox-label { color: var(--color-text); }
</style>
```

- [ ] **Step 8: Create `AppSwitch.vue`**

```vue
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
```

- [ ] **Step 9: Create `AppCard.vue`**

```vue
<script setup>
defineProps({
  padded: { type: Boolean, default: true },
  glass: { type: Boolean, default: false },
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' },
})
</script>

<template>
  <section class="card" :class="{ 'card--padded': padded, 'card--glass': glass }">
    <header v-if="title || $slots.header" class="card-header">
      <slot name="header">
        <div>
          <div class="card-title">{{ title }}</div>
          <div v-if="subtitle" class="card-subtitle">{{ subtitle }}</div>
        </div>
      </slot>
      <div v-if="$slots.actions" class="card-actions">
        <slot name="actions" />
      </div>
    </header>
    <div class="card-body"><slot /></div>
  </section>
</template>

<style scoped>
.card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}
.card--glass { background: var(--color-surface-glass); backdrop-filter: blur(20px) saturate(140%); }
.card--padded .card-header { padding: var(--space-4) var(--space-5); }
.card--padded .card-body { padding: var(--space-5); }
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  border-bottom: 1px solid var(--color-border);
}
.card-title { font-size: var(--text-md); font-weight: 600; }
.card-subtitle { font-size: var(--text-xs); color: var(--color-text-muted); margin-top: 2px; }
.card-actions { display: flex; gap: var(--space-2); }
</style>
```

- [ ] **Step 10: Create `AppModal.vue`** (headless Dialog)

```vue
<script setup>
import { Dialog, DialogPanel, DialogTitle } from '@headlessui/vue'

defineProps({
  open: { type: Boolean, default: false },
  title: { type: String, default: '' },
  size: { type: String, default: 'md' }, // sm | md | lg
})
const emit = defineEmits(['close'])
</script>

<template>
  <transition name="modal-fade">
    <Dialog v-if="open" as="div" class="modal" @close="emit('close')">
      <div class="modal-overlay" aria-hidden="true" />
      <div class="modal-container">
        <transition name="modal-pop" appear>
          <DialogPanel class="modal-panel" :class="`modal-panel--${size}`">
            <header v-if="title" class="modal-header">
              <DialogTitle class="modal-title">{{ title }}</DialogTitle>
              <button class="modal-close" aria-label="关闭" @click="emit('close')">×</button>
            </header>
            <div class="modal-body"><slot /></div>
            <footer v-if="$slots.footer" class="modal-footer"><slot name="footer" /></footer>
          </DialogPanel>
        </transition>
      </div>
    </Dialog>
  </transition>
</template>

<style scoped>
.modal { position: fixed; inset: 0; z-index: var(--z-modal); }
.modal-overlay {
  position: absolute; inset: 0;
  background: rgba(24, 24, 27, 0.32);
  backdrop-filter: blur(4px);
}
.modal-container {
  position: relative;
  min-height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-5);
}
.modal-panel {
  background: var(--color-surface-elevated);
  backdrop-filter: blur(24px) saturate(140%);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
  width: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  max-height: 90vh;
}
.modal-panel--sm { max-width: 420px; }
.modal-panel--md { max-width: 560px; }
.modal-panel--lg { max-width: 820px; }
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-5);
  border-bottom: 1px solid var(--color-border);
}
.modal-title { font-size: var(--text-lg); font-weight: 600; }
.modal-close {
  width: 32px; height: 32px;
  border-radius: var(--radius-md);
  color: var(--color-text-muted);
  font-size: 24px;
  display: inline-flex; align-items: center; justify-content: center;
  transition: background var(--duration-fast) var(--ease-out);
}
.modal-close:hover { background: rgba(24, 24, 27, 0.05); color: var(--color-text); }
.modal-body { padding: var(--space-5); overflow-y: auto; flex: 1; }
.modal-footer {
  padding: var(--space-4) var(--space-5);
  border-top: 1px solid var(--color-border);
  display: flex;
  justify-content: flex-end;
  gap: var(--space-2);
}
.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity var(--duration-base) var(--ease-out); }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
.modal-pop-enter-active { transition: transform var(--duration-base) var(--ease-out), opacity var(--duration-base) var(--ease-out); }
.modal-pop-enter-from { transform: translateY(12px) scale(0.98); opacity: 0; }
</style>
```

- [ ] **Step 11: Create `AppConfirmDialog.vue`**

```vue
<script setup>
import AppModal from './AppModal.vue'
import AppButton from './AppButton.vue'

defineProps({
  open: { type: Boolean, default: false },
  title: { type: String, default: '确认操作' },
  message: { type: String, default: '' },
  confirmText: { type: String, default: '确认' },
  cancelText: { type: String, default: '取消' },
  variant: { type: String, default: 'danger' }, // danger | primary
  loading: { type: Boolean, default: false },
})
const emit = defineEmits(['confirm', 'cancel'])
</script>

<template>
  <AppModal :open="open" :title="title" size="sm" @close="emit('cancel')">
    <p class="confirm-message">{{ message }}</p>
    <template #footer>
      <AppButton variant="ghost" :disabled="loading" @click="emit('cancel')">{{ cancelText }}</AppButton>
      <AppButton :variant="variant" :loading="loading" @click="emit('confirm')">{{ confirmText }}</AppButton>
    </template>
  </AppModal>
</template>

<style scoped>
.confirm-message { font-size: var(--text-base); color: var(--color-text-muted); line-height: var(--leading-relaxed); }
</style>
```

- [ ] **Step 12: Create `AppBadge.vue`**

```vue
<script setup>
defineProps({
  variant: { type: String, default: 'neutral' }, // neutral | primary | success | warning | danger | info
  soft: { type: Boolean, default: true },
})
</script>

<template>
  <span class="badge" :class="[`badge--${variant}`, { 'badge--soft': soft, 'badge--solid': !soft }]">
    <slot />
  </span>
</template>

<style scoped>
.badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 10px;
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: 600;
  letter-spacing: 0.01em;
  white-space: nowrap;
}
.badge--soft.badge--neutral { background: rgba(24, 24, 27, 0.06); color: var(--color-text-muted); }
.badge--soft.badge--primary { background: var(--gradient-primary-soft); color: var(--color-primary); }
.badge--soft.badge--success { background: var(--gradient-success-soft); color: var(--color-success); }
.badge--soft.badge--warning { background: var(--gradient-warning-soft); color: var(--color-warning); }
.badge--soft.badge--danger  { background: var(--gradient-danger-soft);  color: var(--color-danger); }
.badge--soft.badge--info    { background: var(--gradient-info-soft);    color: var(--color-info); }

.badge--solid { color: #fff; }
.badge--solid.badge--primary { background: var(--gradient-primary); }
.badge--solid.badge--success { background: var(--gradient-success); }
.badge--solid.badge--warning { background: var(--gradient-warning); }
.badge--solid.badge--danger  { background: var(--gradient-danger); }
.badge--solid.badge--info    { background: var(--gradient-info); }
.badge--solid.badge--neutral { background: #3f3f46; }
</style>
```

- [ ] **Step 13: Create `AppTag.vue`** (for task tags, small labels)

```vue
<script setup>
defineProps({
  closable: { type: Boolean, default: false },
})
const emit = defineEmits(['close'])
</script>

<template>
  <span class="tag">
    <slot />
    <button v-if="closable" class="tag-close" aria-label="移除" @click.stop="emit('close')">×</button>
  </span>
</template>

<style scoped>
.tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  background: rgba(24, 24, 27, 0.05);
  color: var(--color-text-muted);
  font-size: var(--text-xs);
  font-weight: 500;
}
.tag-close {
  font-size: 14px;
  line-height: 1;
  color: var(--color-text-subtle);
  padding: 0 2px;
}
.tag-close:hover { color: var(--color-danger); }
</style>
```

- [ ] **Step 14: Create `AppEmptyState.vue`**

```vue
<script setup>
defineProps({
  icon: { type: String, default: '∅' },
  title: { type: String, default: '暂无数据' },
  description: { type: String, default: '' },
})
</script>

<template>
  <div class="empty">
    <div class="empty-icon" aria-hidden="true">{{ icon }}</div>
    <div class="empty-title">{{ title }}</div>
    <div v-if="description" class="empty-desc">{{ description }}</div>
    <div v-if="$slots.action" class="empty-action"><slot name="action" /></div>
  </div>
</template>

<style scoped>
.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: var(--space-7) var(--space-5);
  gap: var(--space-2);
}
.empty-icon {
  width: 56px; height: 56px;
  border-radius: var(--radius-full);
  background: var(--gradient-primary-soft);
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 24px;
  color: var(--color-primary);
  margin-bottom: var(--space-2);
}
.empty-title { font-size: var(--text-md); font-weight: 600; color: var(--color-text); }
.empty-desc { font-size: var(--text-sm); color: var(--color-text-muted); max-width: 360px; }
.empty-action { margin-top: var(--space-4); }
</style>
```

- [ ] **Step 15: Create `AppSpinner.vue`**

```vue
<script setup>
defineProps({
  size: { type: Number, default: 20 },
})
</script>

<template>
  <span class="spinner" :style="{ width: size + 'px', height: size + 'px' }" aria-label="加载中" />
</template>

<style scoped>
.spinner {
  display: inline-block;
  border: 2px solid rgba(139, 92, 246, 0.2);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
</style>
```

- [ ] **Step 16: Create `AppSkeleton.vue`**

```vue
<script setup>
defineProps({
  width: { type: String, default: '100%' },
  height: { type: String, default: '1em' },
  radius: { type: String, default: 'var(--radius-sm)' },
})
</script>

<template>
  <span class="skeleton" :style="{ width, height, borderRadius: radius }" />
</template>

<style scoped>
.skeleton {
  display: inline-block;
  background: linear-gradient(90deg, rgba(24,24,27,0.04) 0%, rgba(24,24,27,0.09) 50%, rgba(24,24,27,0.04) 100%);
  background-size: 200% 100%;
  animation: shimmer 1.4s ease-in-out infinite;
}
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
```

- [ ] **Step 17: Create `AppPageHeader.vue`**

```vue
<script setup>
defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
})
</script>

<template>
  <header class="page-header">
    <div class="page-header-text">
      <h1 class="heading-1">{{ title }}</h1>
      <p v-if="subtitle" class="page-header-sub text-muted">{{ subtitle }}</p>
    </div>
    <div v-if="$slots.actions" class="page-header-actions"><slot name="actions" /></div>
  </header>
</template>

<style scoped>
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-5);
  margin-bottom: var(--space-6);
}
.page-header-sub { margin-top: 6px; font-size: var(--text-sm); }
.page-header-actions { display: flex; gap: var(--space-2); flex-shrink: 0; }
</style>
```

- [ ] **Step 18: Create `AppTabs.vue`**

```vue
<script setup>
defineProps({
  modelValue: { type: [String, Number], required: true },
  tabs: { type: Array, required: true }, // [{ value, label }]
})
const emit = defineEmits(['update:modelValue'])
</script>

<template>
  <div class="tabs">
    <button
      v-for="tab in tabs"
      :key="tab.value"
      class="tab"
      :class="{ 'tab--active': tab.value === modelValue }"
      @click="emit('update:modelValue', tab.value)"
    >
      {{ tab.label }}
    </button>
  </div>
</template>

<style scoped>
.tabs {
  display: inline-flex;
  gap: 2px;
  padding: 4px;
  background: rgba(24, 24, 27, 0.04);
  border-radius: var(--radius-md);
}
.tab {
  padding: 6px 14px;
  border-radius: 8px;
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text-muted);
  transition: background var(--duration-fast) var(--ease-out), color var(--duration-fast) var(--ease-out);
}
.tab:hover { color: var(--color-text); }
.tab--active {
  background: var(--color-surface);
  color: var(--color-text);
  box-shadow: var(--shadow-sm);
}
</style>
```

- [ ] **Step 19: Create `AppDatePicker.vue`** (styled `@vuepic/vue-datepicker`)

```vue
<script setup>
import VueDatePicker from '@vuepic/vue-datepicker'
import '@vuepic/vue-datepicker/dist/main.css'

defineProps({
  modelValue: { type: [Date, String, Array, null], default: null },
  label: { type: String, default: '' },
  placeholder: { type: String, default: '选择日期' },
  range: { type: Boolean, default: false },
  clearable: { type: Boolean, default: true },
})
const emit = defineEmits(['update:modelValue'])
</script>

<template>
  <div class="datepicker-wrap">
    <div v-if="label" class="datepicker-label">{{ label }}</div>
    <VueDatePicker
      :model-value="modelValue"
      :range="range"
      :clearable="clearable"
      :placeholder="placeholder"
      :enable-time-picker="false"
      :format="range ? 'yyyy-MM-dd ~ yyyy-MM-dd' : 'yyyy-MM-dd'"
      auto-apply
      locale="zh-CN"
      @update:model-value="v => emit('update:modelValue', v)"
    />
  </div>
</template>

<style>
/* Override library CSS via custom properties */
.dp__theme_light {
  --dp-background-color: var(--color-surface);
  --dp-text-color: var(--color-text);
  --dp-border-color: var(--color-border);
  --dp-border-color-hover: var(--color-border-strong);
  --dp-primary-color: #8b5cf6;
  --dp-menu-border-color: var(--color-border);
  --dp-border-radius: var(--radius-md);
  --dp-font-family: var(--font-sans);
  --dp-input-padding: 8px 12px;
}
.dp__input {
  border-radius: var(--radius-md);
  height: 38px;
  font-family: var(--font-sans);
  font-size: var(--text-base);
}
.dp__input:focus, .dp__input:hover { border-color: var(--color-primary); box-shadow: var(--shadow-glow); }
.dp__menu { border-radius: var(--radius-lg); box-shadow: var(--shadow-md); }
</style>

<style scoped>
.datepicker-wrap { display: flex; flex-direction: column; gap: 6px; }
.datepicker-label { font-size: var(--text-sm); font-weight: 500; }
</style>
```

- [ ] **Step 20: Replace `AppToastHost.vue` with real implementation**

Replace the Task-10 stub `frontend/src/components/ui/AppToastHost.vue`:

```vue
<script setup>
import { useNotificationsStore } from '@/stores/notifications'
const notifications = useNotificationsStore()
</script>

<template>
  <div class="toast-host" role="region" aria-live="polite">
    <transition-group name="toast" tag="div" class="toast-stack">
      <div
        v-for="t in notifications.items"
        :key="t.id"
        class="toast"
        :class="`toast--${t.variant}`"
        role="status"
      >
        <span class="toast-icon" aria-hidden="true">{{ iconFor(t.variant) }}</span>
        <div class="toast-body">
          <div v-if="t.title" class="toast-title">{{ t.title }}</div>
          <div class="toast-message">{{ t.message }}</div>
        </div>
        <button class="toast-close" aria-label="关闭" @click="notifications.dismiss(t.id)">×</button>
      </div>
    </transition-group>
  </div>
</template>

<script>
function iconFor(variant) {
  return { success: '✓', error: '!', warning: '⚠', info: 'i' }[variant] || 'i'
}
</script>

<style scoped>
.toast-host {
  position: fixed;
  top: var(--space-5);
  right: var(--space-5);
  z-index: var(--z-toast);
  pointer-events: none;
}
.toast-stack { display: flex; flex-direction: column; gap: var(--space-2); }
.toast {
  pointer-events: auto;
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  background: var(--color-surface-elevated);
  backdrop-filter: blur(20px) saturate(140%);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  min-width: 280px;
  max-width: 400px;
}
.toast-icon {
  width: 22px; height: 22px;
  border-radius: 50%;
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 13px;
  color: #fff;
  flex-shrink: 0;
  margin-top: 1px;
}
.toast--success .toast-icon { background: var(--gradient-success); }
.toast--error   .toast-icon { background: var(--gradient-danger); }
.toast--warning .toast-icon { background: var(--gradient-warning); }
.toast--info    .toast-icon { background: var(--gradient-info); }
.toast-body { flex: 1; }
.toast-title { font-size: var(--text-sm); font-weight: 600; margin-bottom: 2px; }
.toast-message { font-size: var(--text-sm); color: var(--color-text-muted); }
.toast-close {
  color: var(--color-text-subtle);
  font-size: 18px; line-height: 1;
  padding: 2px 4px;
  margin: -2px -4px 0 0;
}
.toast-close:hover { color: var(--color-text); }
.toast-enter-active, .toast-leave-active { transition: transform var(--duration-base) var(--ease-out), opacity var(--duration-base) var(--ease-out); }
.toast-enter-from { transform: translateX(24px); opacity: 0; }
.toast-leave-to { transform: translateX(24px); opacity: 0; }
.toast-leave-active { position: absolute; right: 0; }
</style>
```

> Note: This imports `useNotificationsStore` which will be created in Task 12. If Task 11 is merged before Task 12, the app will throw at runtime until Task 12 lands. To keep the app runnable, **do not integrate `AppToastHost` rendering into `App.vue`** before Task 12. The stub remains active from Task 10, and this step creates the real file but doesn't wire it. Task 12 will wire it.

**Correction:** delete this step's file replacement. Instead, leave the stub active, and **move Step 20's full implementation into Task 12 Step 5** (which creates the notifications store in the same commit). Proceed as follows: in this Task 11, **skip Step 20** — only keep Steps 1–19.

- [ ] **Step 21: Verify dev server renders with no errors**

```bash
cd /Users/jarrett/Desktop/SpringPilot/frontend
npm run dev
```

Open http://localhost:5173. The app should still render the shell (same as after Task 10). No new visual change — components exist but aren't mounted yet. Check browser console for 0 errors.

- [ ] **Step 22: Commit**

```bash
cd /Users/jarrett/Desktop/SpringPilot
git add frontend/package.json frontend/package-lock.json frontend/src/components/ui
git commit -m "feat(frontend): add base UI component library with flat-design tokens"
```

---

## Task 12: API Modules, Notifications Store, useAsync Composable

**Files:**
- Create: `frontend/src/api/applications.js`
- Create: `frontend/src/api/studyTasks.js`
- Create: `frontend/src/api/fitness.js`
- Create: `frontend/src/api/ai.js`
- Create: `frontend/src/api/settings.js`
- Create: `frontend/src/api/trainerPlans.js`
- Create: `frontend/src/stores/notifications.js`
- Create: `frontend/src/composables/useToast.js`
- Create: `frontend/src/composables/useAsync.js`
- Modify: `frontend/src/components/ui/AppToastHost.vue` (replace stub)

- [ ] **Step 1: Create `frontend/src/api/applications.js`**

```js
import client from './client'

export const applicationsApi = {
  list: (statusFilter = null) => {
    const params = statusFilter ? { status_filter: statusFilter } : {}
    return client.get('/applications', { params })
  },
  get: (id) => client.get(`/applications/${id}`),
  create: (payload) => client.post('/applications', payload),
  update: (id, payload) => client.patch(`/applications/${id}`, payload),
  remove: (id) => client.delete(`/applications/${id}`),
  updateStatus: (id, newStatus, note = null) =>
    client.post(`/applications/${id}/status`, { new_status: newStatus, note }),
}
```

- [ ] **Step 2: Create `frontend/src/api/studyTasks.js`**

```js
import client from './client'

export const studyTasksApi = {
  list: (completed = null) => {
    const params = completed === null ? {} : { completed }
    return client.get('/study-tasks', { params })
  },
  create: (payload) => client.post('/study-tasks', payload),
  update: (id, payload) => client.patch(`/study-tasks/${id}`, payload),
  remove: (id) => client.delete(`/study-tasks/${id}`),
}
```

- [ ] **Step 3: Create `frontend/src/api/fitness.js`**

```js
import client from './client'

export const weightApi = {
  list: (limit = 90) => client.get('/weight', { params: { limit } }),
  create: (payload) => client.post('/weight', payload),
  remove: (id) => client.delete(`/weight/${id}`),
}

export const dietApi = {
  list: (day = null) => {
    const params = day ? { day } : {}
    return client.get('/diet', { params })
  },
  create: (payload) => client.post('/diet', payload),
  remove: (id) => client.delete(`/diet/${id}`),
}

export const trainingApi = {
  list: (limit = 30) => client.get('/training', { params: { limit } }),
  create: (payload) => client.post('/training', payload),
  update: (id, payload) => client.patch(`/training/${id}`, payload),
  remove: (id) => client.delete(`/training/${id}`),
}
```

- [ ] **Step 4: Create `frontend/src/api/ai.js`**

```js
import client from './client'

export const aiApi = {
  analyzeJd: (jdText, resumeText = null) =>
    client.post('/ai/analyze-jd', { jd_text: jdText, resume_text: resumeText }),
  generateQuestions: (position, jdText, questionCount = 10) =>
    client.post('/ai/generate-questions', { position, jd_text: jdText, question_count: questionCount }),
  mockInterview: (history, userAnswer) =>
    client.post('/ai/mock-interview', { history, user_answer: userAnswer }),
  estimateCalories: (foodDescription) =>
    client.post('/ai/estimate-calories', { food_description: foodDescription }),
  dailyAdvice: (jobSummary, fitnessSummary) =>
    client.post('/ai/daily-advice', { job_summary: jobSummary, fitness_summary: fitnessSummary }),
}
```

- [ ] **Step 5: Create `frontend/src/api/settings.js`**

```js
import client from './client'

export const settingsApi = {
  getAll: () => client.get('/settings'),
  get: (key) => client.get(`/settings/${key}`),
  set: (key, value) => client.put(`/settings/${key}`, { value }),
}
```

- [ ] **Step 6: Create `frontend/src/api/trainerPlans.js`**

```js
import client from './client'

export const trainerPlansApi = {
  list: () => client.get('/trainer-plans'),
  upload: (file, title, planDateRange = null) => {
    const form = new FormData()
    form.append('file', file)
    form.append('title', title)
    if (planDateRange) form.append('plan_date_range', planDateRange)
    return client.post('/trainer-plans', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  remove: (id) => client.delete(`/trainer-plans/${id}`),
}
```

- [ ] **Step 7: Create `frontend/src/stores/notifications.js`**

```js
import { defineStore } from 'pinia'
import { ref } from 'vue'

let nextId = 0

export const useNotificationsStore = defineStore('notifications', () => {
  const items = ref([])

  function push({ variant = 'info', title = '', message, duration = 4000 }) {
    const id = ++nextId
    items.value.push({ id, variant, title, message })
    if (duration > 0) {
      setTimeout(() => dismiss(id), duration)
    }
    return id
  }

  function dismiss(id) {
    const index = items.value.findIndex(t => t.id === id)
    if (index !== -1) items.value.splice(index, 1)
  }

  function clear() {
    items.value = []
  }

  return { items, push, dismiss, clear }
})
```

- [ ] **Step 8: Create `frontend/src/composables/useToast.js`**

```js
import { useNotificationsStore } from '@/stores/notifications'

export function useToast() {
  const store = useNotificationsStore()
  return {
    success: (message, title = '') => store.push({ variant: 'success', title, message }),
    error: (message, title = '出错了') => store.push({ variant: 'error', title, message, duration: 6000 }),
    warning: (message, title = '') => store.push({ variant: 'warning', title, message }),
    info: (message, title = '') => store.push({ variant: 'info', title, message }),
  }
}
```

- [ ] **Step 9: Create `frontend/src/composables/useAsync.js`**

```js
import { ref } from 'vue'
import { useToast } from './useToast'

/**
 * Wraps an async operation with loading + error state and automatic error toast.
 * Usage:
 *   const { loading, error, run } = useAsync()
 *   await run(() => applicationsApi.list())
 */
export function useAsync({ silent = false } = {}) {
  const loading = ref(false)
  const error = ref(null)
  const toast = useToast()

  async function run(fn) {
    loading.value = true
    error.value = null
    try {
      return await fn()
    } catch (err) {
      error.value = err
      if (!silent) toast.error(err.message || '请求失败')
      throw err
    } finally {
      loading.value = false
    }
  }

  return { loading, error, run }
}
```

- [ ] **Step 10: Replace `frontend/src/components/ui/AppToastHost.vue` with real implementation**

```vue
<script setup>
import { useNotificationsStore } from '@/stores/notifications'
const notifications = useNotificationsStore()

function iconFor(variant) {
  return { success: '✓', error: '!', warning: '⚠', info: 'i' }[variant] || 'i'
}
</script>

<template>
  <div class="toast-host" role="region" aria-live="polite">
    <transition-group name="toast" tag="div" class="toast-stack">
      <div
        v-for="t in notifications.items"
        :key="t.id"
        class="toast"
        :class="`toast--${t.variant}`"
        role="status"
      >
        <span class="toast-icon" aria-hidden="true">{{ iconFor(t.variant) }}</span>
        <div class="toast-body">
          <div v-if="t.title" class="toast-title">{{ t.title }}</div>
          <div class="toast-message">{{ t.message }}</div>
        </div>
        <button class="toast-close" aria-label="关闭" @click="notifications.dismiss(t.id)">×</button>
      </div>
    </transition-group>
  </div>
</template>

<style scoped>
.toast-host {
  position: fixed;
  top: var(--space-5);
  right: var(--space-5);
  z-index: var(--z-toast);
  pointer-events: none;
}
.toast-stack { display: flex; flex-direction: column; gap: var(--space-2); }
.toast {
  pointer-events: auto;
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  background: var(--color-surface-elevated);
  backdrop-filter: blur(20px) saturate(140%);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  min-width: 280px;
  max-width: 400px;
}
.toast-icon {
  width: 22px; height: 22px;
  border-radius: 50%;
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 13px;
  color: #fff;
  flex-shrink: 0;
  margin-top: 1px;
}
.toast--success .toast-icon { background: var(--gradient-success); }
.toast--error   .toast-icon { background: var(--gradient-danger); }
.toast--warning .toast-icon { background: var(--gradient-warning); }
.toast--info    .toast-icon { background: var(--gradient-info); }
.toast-body { flex: 1; }
.toast-title { font-size: var(--text-sm); font-weight: 600; margin-bottom: 2px; }
.toast-message { font-size: var(--text-sm); color: var(--color-text-muted); }
.toast-close {
  color: var(--color-text-subtle);
  font-size: 18px; line-height: 1;
  padding: 2px 4px;
  margin: -2px -4px 0 0;
}
.toast-close:hover { color: var(--color-text); }
.toast-enter-active, .toast-leave-active { transition: transform var(--duration-base) var(--ease-out), opacity var(--duration-base) var(--ease-out); }
.toast-enter-from { transform: translateX(24px); opacity: 0; }
.toast-leave-to { transform: translateX(24px); opacity: 0; }
.toast-leave-active { position: absolute; right: 0; }
</style>
```

- [ ] **Step 11: Verify toast works via temporary dev harness**

Temporarily add a test button to `frontend/src/views/Dashboard.vue` (this will be fully rewritten in Task 14 — this is only a smoke test):

```vue
<script setup>
import { useToast } from '@/composables/useToast'
const toast = useToast()
</script>

<template>
  <div>
    <h1>首页</h1>
    <p>Coming soon...</p>
    <button @click="toast.success('测试成功消息')">测试成功</button>
    <button @click="toast.error('测试错误消息')">测试错误</button>
    <button @click="toast.warning('测试警告')">测试警告</button>
    <button @click="toast.info('测试信息')">测试信息</button>
  </div>
</template>
```

Then:

```bash
cd /Users/jarrett/Desktop/SpringPilot/frontend
npm run dev
```

Click each of the four buttons. Expected: each toast slides in from the right with the correct gradient icon, auto-dismisses after 4s (6s for error), manual dismiss via × works.

- [ ] **Step 12: Revert Dashboard.vue to placeholder**

Reset `frontend/src/views/Dashboard.vue` back to the placeholder so it's clean for Task 14:

```vue
<template>
  <div>
    <h1>首页</h1>
    <p>Coming soon...</p>
  </div>
</template>
```

- [ ] **Step 13: Verify backend connectivity (smoke test)**

Open browser devtools Network tab, run in console:

```js
fetch('/api/health').then(r => r.json()).then(console.log)
```

Expected: `{status: "ok"}` (requires backend running via `uvicorn backend.main:app --reload --port 8000`). If backend isn't running, start it in another terminal first.

- [ ] **Step 14: Commit**

```bash
cd /Users/jarrett/Desktop/SpringPilot
git add frontend/src/api frontend/src/stores/notifications.js frontend/src/composables frontend/src/components/ui/AppToastHost.vue
git commit -m "feat(frontend): add API modules, notifications store, toast host, and async composable"
```

---

## Task 13: Settings Page

**Context:** Settings is the gating page. AI features (JD analysis, mock interview, daily advice) and trainer plan parsing all depend on API keys configured here. Must ship before any AI-dependent page.

**What it does:**
- Section A — LLM providers: for each of GLM / DeepSeek / Claude / OpenAI, configure API key + base URL + model
- Section B — Scenario routing: per scenario (`default`, `jd_analysis`, `interview_gen`, `mock_interview`, `diet`) pick which provider to use
- Section C — User profile: height_cm, target_weight_kg, tdee_base
- Section D — MinerU API key
- Section E — Data export (download all app data as JSON)

**Storage contract (UserConfig keys):**
- `llm_api_key_{provider}` — per-provider API key
- `llm_base_url_{provider}` — optional base URL override
- `llm_model_{provider}` — model id
- `llm_provider_{scenario}` — provider name for scenario routing
- `height_cm`, `target_weight_kg`, `tdee_base`
- `mineru_api_key`

**Files:**
- Modify: `frontend/src/stores/settings.js` (expand schema)
- Rewrite: `frontend/src/views/Settings.vue`

- [ ] **Step 1: Expand `frontend/src/stores/settings.js`**

Replace the file content:

```js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { settingsApi } from '@/api/settings'

export const LLM_PROVIDERS = ['openai', 'deepseek', 'claude', 'glm']
export const LLM_SCENARIOS = [
  { value: 'default', label: '默认（日常使用）' },
  { value: 'jd_analysis', label: 'JD 分析' },
  { value: 'interview_gen', label: '面试题生成' },
  { value: 'mock_interview', label: '模拟面试' },
  { value: 'diet', label: '饮食估算' },
]

export const useSettingsStore = defineStore('settings', () => {
  const configs = ref({})
  const loaded = ref(false)

  async function loadAll() {
    const data = await settingsApi.getAll()
    configs.value = data.configs || {}
    loaded.value = true
  }

  async function set(key, value) {
    await settingsApi.set(key, value)
    configs.value = { ...configs.value, [key]: value }
  }

  async function setMany(entries) {
    for (const [key, value] of entries) {
      await settingsApi.set(key, value)
    }
    configs.value = { ...configs.value, ...Object.fromEntries(entries) }
  }

  function get(key, fallback = '') {
    const v = configs.value[key]
    return v === undefined || v === null ? fallback : v
  }

  // LLM helpers
  function llmApiKey(provider) { return get(`llm_api_key_${provider}`) }
  function llmBaseUrl(provider) { return get(`llm_base_url_${provider}`) }
  function llmModel(provider)   { return get(`llm_model_${provider}`) }
  function llmProviderFor(scenario) { return get(`llm_provider_${scenario}`) }

  const hasAnyLlmKey = computed(() =>
    LLM_PROVIDERS.some(p => !!configs.value[`llm_api_key_${p}`])
  )

  // Profile helpers
  const heightCm       = computed(() => Number(get('height_cm'))       || null)
  const targetWeightKg = computed(() => Number(get('target_weight_kg'))|| null)
  const tdeeBase       = computed(() => Number(get('tdee_base'))       || null)

  return {
    configs, loaded,
    loadAll, set, setMany, get,
    llmApiKey, llmBaseUrl, llmModel, llmProviderFor,
    hasAnyLlmKey,
    heightCm, targetWeightKg, tdeeBase,
  }
})
```

- [ ] **Step 2: Rewrite `frontend/src/views/Settings.vue`**

```vue
<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useSettingsStore, LLM_PROVIDERS, LLM_SCENARIOS } from '@/stores/settings'
import { useAsync } from '@/composables/useAsync'
import { useToast } from '@/composables/useToast'
import AppPageHeader from '@/components/ui/AppPageHeader.vue'
import AppCard from '@/components/ui/AppCard.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppSelect from '@/components/ui/AppSelect.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppTabs from '@/components/ui/AppTabs.vue'

const store = useSettingsStore()
const toast = useToast()
const { loading, run } = useAsync()

const providerMeta = {
  openai:   { label: 'OpenAI',   defaultModel: 'gpt-4o-mini',    defaultBase: '' },
  deepseek: { label: 'DeepSeek', defaultModel: 'deepseek-chat',  defaultBase: 'https://api.deepseek.com/v1' },
  claude:   { label: 'Claude',   defaultModel: 'claude-sonnet-4-6', defaultBase: '' },
  glm:      { label: '智谱 GLM', defaultModel: 'glm-4-flash',    defaultBase: '' },
}

const activeTab = ref('llm')
const tabs = [
  { value: 'llm',     label: 'AI 模型' },
  { value: 'routing', label: '场景路由' },
  { value: 'profile', label: '个人档案' },
  { value: 'mineru',  label: '文档解析' },
  { value: 'export',  label: '数据导出' },
]

// Editable form — mirrors store.configs but flushed on Save click per section
const form = reactive({
  llm: {
    openai:   { key: '', base: '', model: '' },
    deepseek: { key: '', base: '', model: '' },
    claude:   { key: '', base: '', model: '' },
    glm:      { key: '', base: '', model: '' },
  },
  routing: { default: '', jd_analysis: '', interview_gen: '', mock_interview: '', diet: '' },
  profile: { height_cm: '', target_weight_kg: '', tdee_base: '' },
  mineru_api_key: '',
})

function loadFormFromStore() {
  for (const p of LLM_PROVIDERS) {
    form.llm[p].key   = store.get(`llm_api_key_${p}`)
    form.llm[p].base  = store.get(`llm_base_url_${p}`)
    form.llm[p].model = store.get(`llm_model_${p}`)
  }
  for (const s of LLM_SCENARIOS) {
    form.routing[s.value] = store.get(`llm_provider_${s.value}`)
  }
  form.profile.height_cm        = store.get('height_cm')
  form.profile.target_weight_kg = store.get('target_weight_kg')
  form.profile.tdee_base        = store.get('tdee_base')
  form.mineru_api_key           = store.get('mineru_api_key')
}

onMounted(async () => {
  await run(() => store.loadAll())
  loadFormFromStore()
})

const providerOptions = computed(() => [
  { value: '', label: '（未指定）' },
  ...LLM_PROVIDERS.map(p => ({ value: p, label: providerMeta[p].label })),
])

async function saveLlmProvider(provider) {
  const p = form.llm[provider]
  await run(() => store.setMany([
    [`llm_api_key_${provider}`,  p.key],
    [`llm_base_url_${provider}`, p.base],
    [`llm_model_${provider}`,    p.model],
  ]))
  toast.success(`${providerMeta[provider].label} 配置已保存`)
}

async function saveRouting() {
  const entries = LLM_SCENARIOS.map(s => [`llm_provider_${s.value}`, form.routing[s.value]])
  await run(() => store.setMany(entries))
  toast.success('场景路由已保存')
}

async function saveProfile() {
  await run(() => store.setMany([
    ['height_cm',        form.profile.height_cm],
    ['target_weight_kg', form.profile.target_weight_kg],
    ['tdee_base',        form.profile.tdee_base],
  ]))
  toast.success('个人档案已保存')
}

async function saveMineru() {
  await run(() => store.set('mineru_api_key', form.mineru_api_key))
  toast.success('MinerU 配置已保存')
}

async function exportData() {
  await run(async () => {
    const [{ applicationsApi }, { studyTasksApi }, { weightApi, dietApi, trainingApi }, { trainerPlansApi }] = await Promise.all([
      import('@/api/applications'),
      import('@/api/studyTasks'),
      import('@/api/fitness'),
      import('@/api/trainerPlans'),
    ])
    const [applications, studyTasks, weight, diet, training, trainerPlans] = await Promise.all([
      applicationsApi.list(),
      studyTasksApi.list(),
      weightApi.list(9999),
      dietApi.list(),
      trainingApi.list(9999),
      trainerPlansApi.list(),
    ])
    const blob = new Blob(
      [JSON.stringify({ exported_at: new Date().toISOString(), applications, studyTasks, weight, diet, training, trainerPlans, settings: store.configs }, null, 2)],
      { type: 'application/json' },
    )
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `springpilot-backup-${new Date().toISOString().slice(0, 10)}.json`
    a.click()
    URL.revokeObjectURL(url)
    toast.success('数据已导出')
  })
}

function configuredBadge(provider) {
  return !!store.get(`llm_api_key_${provider}`)
}
</script>

<template>
  <div>
    <AppPageHeader title="设置" subtitle="配置 AI 模型、个人档案与数据管理" />

    <AppTabs v-model="activeTab" :tabs="tabs" />

    <div class="settings-body">
      <!-- LLM providers -->
      <div v-if="activeTab === 'llm'" class="settings-grid">
        <AppCard v-for="p in LLM_PROVIDERS" :key="p">
          <template #header>
            <div class="provider-head">
              <div>
                <div class="card-title">{{ providerMeta[p].label }}</div>
                <div class="card-subtitle">{{ providerMeta[p].defaultBase || '使用默认端点' }}</div>
              </div>
              <AppBadge :variant="configuredBadge(p) ? 'success' : 'neutral'">
                {{ configuredBadge(p) ? '已配置' : '未配置' }}
              </AppBadge>
            </div>
          </template>
          <div class="form-stack">
            <AppInput v-model="form.llm[p].key" label="API Key" type="password" placeholder="sk-..." />
            <AppInput v-model="form.llm[p].base" label="Base URL（可选）" :placeholder="providerMeta[p].defaultBase || '默认'" />
            <AppInput v-model="form.llm[p].model" label="模型名称" :placeholder="providerMeta[p].defaultModel" />
            <div class="form-actions">
              <AppButton :loading="loading" @click="saveLlmProvider(p)">保存</AppButton>
            </div>
          </div>
        </AppCard>
      </div>

      <!-- Scenario routing -->
      <AppCard v-else-if="activeTab === 'routing'" title="场景路由" subtitle="为不同场景指定使用哪个模型提供商">
        <div class="form-stack">
          <AppSelect
            v-for="s in LLM_SCENARIOS"
            :key="s.value"
            :label="s.label"
            :model-value="form.routing[s.value]"
            :options="providerOptions"
            @update:model-value="v => form.routing[s.value] = v"
          />
          <div class="form-actions">
            <AppButton :loading="loading" @click="saveRouting">保存路由</AppButton>
          </div>
        </div>
      </AppCard>

      <!-- Profile -->
      <AppCard v-else-if="activeTab === 'profile'" title="个人档案" subtitle="用于健身模块的 TDEE 计算和目标追踪">
        <div class="form-grid-2">
          <AppInput v-model="form.profile.height_cm"        label="身高 (cm)"    type="number" placeholder="178" />
          <AppInput v-model="form.profile.target_weight_kg" label="目标体重 (kg)" type="number" placeholder="70" />
          <AppInput v-model="form.profile.tdee_base"        label="基础代谢 (kcal/天)" type="number" placeholder="1800" hint="留空将由 AI 估算" />
        </div>
        <div class="form-actions">
          <AppButton :loading="loading" @click="saveProfile">保存档案</AppButton>
        </div>
      </AppCard>

      <!-- MinerU -->
      <AppCard v-else-if="activeTab === 'mineru'" title="MinerU 文档解析" subtitle="用于解析教练给的 PDF / DOCX 训练计划">
        <div class="form-stack">
          <AppInput v-model="form.mineru_api_key" label="MinerU API Key" type="password" placeholder="从 mineru.net 申请" />
          <p class="hint">仅解析 PDF / DOCX 时需要；上传 .md 文件不需要此 Key。</p>
          <div class="form-actions">
            <AppButton :loading="loading" @click="saveMineru">保存</AppButton>
          </div>
        </div>
      </AppCard>

      <!-- Export -->
      <AppCard v-else-if="activeTab === 'export'" title="数据导出" subtitle="将全部投递、任务、健身数据以 JSON 格式下载">
        <p class="hint">导出内容包含所有投递记录、学习任务、体重/饮食/训练日志、训练计划元数据和设置。不包含上传的原始文件。</p>
        <div class="form-actions">
          <AppButton :loading="loading" @click="exportData">下载备份 JSON</AppButton>
        </div>
      </AppCard>
    </div>
  </div>
</template>

<style scoped>
.settings-body { margin-top: var(--space-5); display: flex; flex-direction: column; gap: var(--space-4); }
.settings-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: var(--space-4); }
.provider-head { display: flex; align-items: center; justify-content: space-between; gap: var(--space-3); width: 100%; }
.card-title { font-size: var(--text-md); font-weight: 600; }
.card-subtitle { font-size: var(--text-xs); color: var(--color-text-muted); margin-top: 2px; }
.form-stack { display: flex; flex-direction: column; gap: var(--space-3); }
.form-grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--space-3); margin-bottom: var(--space-4); }
.form-actions { display: flex; justify-content: flex-end; gap: var(--space-2); margin-top: var(--space-2); }
.hint { font-size: var(--text-sm); color: var(--color-text-muted); line-height: var(--leading-relaxed); }
</style>
```

- [ ] **Step 3: Verify in browser**

```bash
cd /Users/jarrett/Desktop/SpringPilot/frontend && npm run dev
# In another terminal:
source .venv/bin/activate && uvicorn backend.main:app --reload --port 8000
```

Open http://localhost:5173/settings. Expected:
- Page header "设置" + tabs for AI 模型 / 场景路由 / 个人档案 / 文档解析 / 数据导出
- AI 模型 tab: 4 cards in a responsive grid, each showing provider name, "未配置" badge
- Entering key + clicking Save → toast "OpenAI 配置已保存"; reloading page keeps it; badge flips to "已配置"
- Scenario routing tab: 5 Listbox dropdowns; saving emits toast
- Profile tab: 2-col input grid; save works
- MinerU tab: key input + hint + save
- Export tab: clicking "下载备份 JSON" downloads a file named `springpilot-backup-YYYY-MM-DD.json`; open it and verify all 7 keys present

- [ ] **Step 4: Commit**

```bash
cd /Users/jarrett/Desktop/SpringPilot
git add frontend/src/stores/settings.js frontend/src/views/Settings.vue
git commit -m "feat(frontend): implement Settings page with LLM config, routing, profile, and export"
```

---


## Task 14: Dashboard Page

**Context:** The landing page. Shows at-a-glance summaries from both job and fitness modules plus a daily AI advice card. All data is fetched from existing APIs; no new backend work.

**What it does:**
- Top row: 4 stat cards (weekly applications count, interviews scheduled, pending study tasks, weekly training count)
- Middle row: two Chart.js sparklines — weight trend (last 30 days) and calorie intake (last 7 days)
- Bottom row: AI daily advice card (calls `/api/ai/daily-advice` with aggregated summaries)

**Files:**
- Create: `frontend/src/components/WeightChart.vue`
- Create: `frontend/src/components/CalorieChart.vue`
- Rewrite: `frontend/src/views/Dashboard.vue`

- [ ] **Step 1: Create `frontend/src/components/WeightChart.vue`**

```vue
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
```

- [ ] **Step 2: Create `frontend/src/components/CalorieChart.vue`**

```vue
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
```

- [ ] **Step 3: Rewrite `frontend/src/views/Dashboard.vue`**

```vue
<script setup>
import { ref, computed, onMounted } from 'vue'
import { applicationsApi } from '@/api/applications'
import { studyTasksApi } from '@/api/studyTasks'
import { weightApi, dietApi, trainingApi } from '@/api/fitness'
import { aiApi } from '@/api/ai'
import { useSettingsStore } from '@/stores/settings'
import AppPageHeader from '@/components/ui/AppPageHeader.vue'
import AppCard from '@/components/ui/AppCard.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppEmptyState from '@/components/ui/AppEmptyState.vue'
import WeightChart from '@/components/WeightChart.vue'
import CalorieChart from '@/components/CalorieChart.vue'

const settings = useSettingsStore()
const loading = ref(true)
const adviceLoading = ref(false)
const advice = ref('')

const applications = ref([])
const tasks = ref([])
const weightRecords = ref([])
const dietLogs = ref([])
const trainingLogs = ref([])

// Computed stats
const now = new Date()
const weekAgo = new Date(now.getTime() - 7 * 86400000)

const weeklyApps = computed(() =>
  applications.value.filter(a => new Date(a.created_at) >= weekAgo).length
)
const interviewing = computed(() =>
  applications.value.filter(a => a.status === 'Interviewing').length
)
const pendingTasks = computed(() =>
  tasks.value.filter(t => !t.completed).length
)
const weeklyTraining = computed(() =>
  trainingLogs.value.filter(t => new Date(t.recorded_at) >= weekAgo).length
)

// Stat card definitions
const stats = computed(() => [
  { label: '本周投递', value: weeklyApps.value, gradient: 'var(--gradient-primary)' },
  { label: '面试中', value: interviewing.value, gradient: 'var(--gradient-info)' },
  { label: '待办任务', value: pendingTasks.value, gradient: 'var(--gradient-warning)' },
  { label: '本周训练', value: weeklyTraining.value, gradient: 'var(--gradient-success)' },
])

onMounted(async () => {
  try {
    const [apps, t, w, d, tr] = await Promise.all([
      applicationsApi.list(),
      studyTasksApi.list(),
      weightApi.list(30),
      dietApi.list(),
      trainingApi.list(30),
    ])
    applications.value = apps
    tasks.value = t
    weightRecords.value = w
    dietLogs.value = d
    trainingLogs.value = tr
  } catch {
    // errors handled per-API by interceptor
  } finally {
    loading.value = false
  }
})

async function fetchAdvice() {
  if (!settings.hasAnyLlmKey) {
    advice.value = '请先在设置页面配置至少一个 AI 模型的 API Key。'
    return
  }
  adviceLoading.value = true
  try {
    const jobSummary = `投递${applications.value.length}家，面试中${interviewing.value}家，待办任务${pendingTasks.value}个。`
    const fitSummary = `近30天体重记录${weightRecords.value.length}条，训练${weeklyTraining.value}次/周。`
    const res = await aiApi.dailyAdvice(jobSummary, fitSummary)
    advice.value = res.advice
  } catch {
    advice.value = '获取建议失败，请检查 AI 模型配置。'
  } finally {
    adviceLoading.value = false
  }
}
</script>

<template>
  <div>
    <AppPageHeader title="首页" subtitle="求职 + 健身一站式概览" />

    <div v-if="loading" class="loading-state"><AppSpinner :size="32" /></div>

    <template v-else>
      <!-- Stat cards -->
      <div class="stats-row">
        <div v-for="s in stats" :key="s.label" class="stat-card">
          <div class="stat-value-row">
            <span class="stat-value">{{ s.value }}</span>
            <span class="stat-dot" :style="{ background: s.gradient }"></span>
          </div>
          <div class="stat-label">{{ s.label }}</div>
        </div>
      </div>

      <!-- Charts row -->
      <div class="charts-row">
        <AppCard title="体重趋势" subtitle="近 30 天">
          <WeightChart :records="weightRecords" />
        </AppCard>
        <AppCard title="热量摄入" subtitle="近 7 天">
          <CalorieChart :logs="dietLogs" />
        </AppCard>
      </div>

      <!-- AI Advice -->
      <AppCard title="AI 每日建议" subtitle="基于你的求职和健身数据">
        <template #actions>
          <AppButton size="sm" :loading="adviceLoading" @click="fetchAdvice">获取建议</AppButton>
        </template>
        <div v-if="advice" class="advice-text">{{ advice }}</div>
        <AppEmptyState v-else icon="◈" title="点击右上角获取今日建议" description="AI 会根据你的数据给出个性化建议" />
      </AppCard>
    </template>
  </div>
</template>

<style scoped>
.loading-state { display: flex; justify-content: center; padding: var(--space-7); }
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-4);
  margin-bottom: var(--space-5);
}
.stat-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-4) var(--space-5);
  box-shadow: var(--shadow-sm);
}
.stat-value-row { display: flex; align-items: baseline; gap: var(--space-2); }
.stat-value { font-size: var(--text-3xl); font-weight: 700; letter-spacing: -0.02em; }
.stat-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  margin-left: auto;
}
.stat-label { font-size: var(--text-sm); color: var(--color-text-muted); margin-top: 4px; }
.charts-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-4);
  margin-bottom: var(--space-5);
}
.advice-text {
  font-size: var(--text-base);
  line-height: var(--leading-relaxed);
  color: var(--color-text);
  white-space: pre-line;
  padding: var(--space-3) 0;
}
</style>
```

- [ ] **Step 4: Verify in browser**

Open http://localhost:5173/. Expected:
- 4 stat cards in a row with large numbers and gradient dots
- 2 chart cards side by side (empty if no data — enter some via the fitness page later)
- AI advice card at bottom with "获取建议" button (will fail gracefully if no API key configured; configure one via Settings page to test fully)

- [ ] **Step 5: Commit**

```bash
cd /Users/jarrett/Desktop/SpringPilot
git add frontend/src/components/WeightChart.vue frontend/src/components/CalorieChart.vue frontend/src/views/Dashboard.vue
git commit -m "feat(frontend): implement Dashboard with stat cards, charts, and AI daily advice"
```

---

## Task 15: Applications List + Application Detail

**Context:** Core CRUD page for job applications. Two views: list with filters and detail with status timeline + AI question generation.

**What Applications.vue does:**
- Table/card list of all applications, sortable by date
- Filter by status (tabs: All / Pending / Applied / Written Test / Interviewing / Offer / Rejected)
- Create modal (company, position, description, channel)
- Quick status change dropdown per row
- Delete with confirmation dialog

**What ApplicationDetail.vue does:**
- Full application info (editable)
- Status change timeline (vertical, left-aligned)
- AI interview question generation (calls `/api/ai/generate-questions`)

**Files:**
- Create: `frontend/src/components/StatusBadge.vue`
- Rewrite: `frontend/src/views/Applications.vue`
- Rewrite: `frontend/src/views/ApplicationDetail.vue`

- [ ] **Step 1: Create `frontend/src/components/StatusBadge.vue`**

```vue
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
```

- [ ] **Step 2: Rewrite `frontend/src/views/Applications.vue`**

```vue
<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { applicationsApi } from '@/api/applications'
import { useAsync } from '@/composables/useAsync'
import { useToast } from '@/composables/useToast'
import AppPageHeader from '@/components/ui/AppPageHeader.vue'
import AppCard from '@/components/ui/AppCard.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppTextarea from '@/components/ui/AppTextarea.vue'
import AppSelect from '@/components/ui/AppSelect.vue'
import AppModal from '@/components/ui/AppModal.vue'
import AppConfirmDialog from '@/components/ui/AppConfirmDialog.vue'
import AppEmptyState from '@/components/ui/AppEmptyState.vue'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import StatusBadge from '@/components/StatusBadge.vue'

const router = useRouter()
const toast = useToast()
const { loading, run } = useAsync()

const applications = ref([])
const activeFilter = ref('all')
const showCreate = ref(false)
const deleteTarget = ref(null)
const deleteLoading = ref(false)

const STATUS_OPTIONS = [
  { value: 'all',            label: '全部' },
  { value: 'Pending',        label: '待处理' },
  { value: 'Applied',        label: '已投递' },
  { value: 'Written Test',   label: '笔试' },
  { value: 'Interviewing',   label: '面试中' },
  { value: 'Offer',          label: 'Offer' },
  { value: 'Rejected',       label: '已拒绝' },
]

const NEXT_STATUS = {
  Pending: 'Applied',
  Applied: 'Written Test',
  'Written Test': 'Interviewing',
  Interviewing: 'Offer',
}

const filteredApps = computed(() => {
  if (activeFilter.value === 'all') return applications.value
  return applications.value.filter(a => a.status === activeFilter.value)
})

// Create form
const form = ref({ company: '', position: '', description: '', channel: '', status: 'Pending' })
const CHANNEL_OPTIONS = [
  { value: 'Boss直聘', label: 'Boss直聘' },
  { value: '官网', label: '官网' },
  { value: '内推', label: '内推' },
  { value: '猎头', label: '猎头' },
  { value: '其他', label: '其他' },
]

onMounted(() => load())

async function load() {
  await run(async () => {
    applications.value = await applicationsApi.list()
  })
}

function openCreate() {
  form.value = { company: '', position: '', description: '', channel: '', status: 'Pending' }
  showCreate.value = true
}

async function createApp() {
  await run(async () => {
    const app = await applicationsApi.create(form.value)
    applications.value.unshift(app)
    showCreate.value = false
    toast.success('投递记录已创建')
  })
}

async function advanceStatus(app) {
  const next = NEXT_STATUS[app.status]
  if (!next) return
  await run(async () => {
    const updated = await applicationsApi.updateStatus(app.id, next)
    const idx = applications.value.findIndex(a => a.id === app.id)
    if (idx !== -1) applications.value[idx] = updated
    toast.success(`状态已更新为 ${next}`)
  })
}

async function confirmDelete() {
  deleteLoading.value = true
  try {
    await applicationsApi.remove(deleteTarget.value.id)
    applications.value = applications.value.filter(a => a.id !== deleteTarget.value.id)
    deleteTarget.value = null
    toast.success('已删除')
  } catch (e) {
    toast.error(e.message)
  } finally {
    deleteLoading.value = false
  }
}

function goDetail(app) {
  router.push({ name: 'application-detail', params: { id: app.id } })
}

function formatDate(dt) {
  return dt ? new Date(dt).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }) : ''
}
</script>

<template>
  <div>
    <AppPageHeader title="投递记录" subtitle="追踪每一家公司的申请进度">
      <template #actions>
        <AppButton @click="openCreate">+ 新建投递</AppButton>
      </template>
    </AppPageHeader>

    <!-- Filter tabs -->
    <div class="filter-row">
      <button
        v-for="opt in STATUS_OPTIONS"
        :key="opt.value"
        class="filter-chip"
        :class="{ 'filter-chip--active': activeFilter === opt.value }"
        @click="activeFilter = opt.value"
      >
        {{ opt.label }}
        <span v-if="opt.value !== 'all'" class="filter-count">
          {{ applications.filter(a => a.status === opt.value).length }}
        </span>
      </button>
    </div>

    <!-- List -->
    <div v-if="loading" class="loading-state"><AppSpinner :size="32" /></div>
    <AppEmptyState v-else-if="filteredApps.length === 0" icon="✦" title="暂无投递记录" description="点击右上角新建你的第一条投递">
      <template #action><AppButton @click="openCreate">新建投递</AppButton></template>
    </AppEmptyState>
    <div v-else class="app-list">
      <div v-for="app in filteredApps" :key="app.id" class="app-row" @click="goDetail(app)">
        <div class="app-main">
          <div class="app-company">{{ app.company }}</div>
          <div class="app-position text-muted">{{ app.position }}</div>
        </div>
        <div class="app-meta">
          <StatusBadge :status="app.status" />
          <span class="app-date text-subtle">{{ formatDate(app.created_at) }}</span>
        </div>
        <div class="app-actions" @click.stop>
          <AppButton v-if="NEXT_STATUS[app.status]" size="sm" variant="ghost" @click="advanceStatus(app)">→ 推进</AppButton>
          <AppButton size="sm" variant="ghost" @click="deleteTarget = app">删除</AppButton>
        </div>
      </div>
    </div>

    <!-- Create modal -->
    <AppModal :open="showCreate" title="新建投递记录" size="md" @close="showCreate = false">
      <div class="form-stack">
        <AppInput v-model="form.company" label="公司名称" placeholder="字节跳动" required />
        <AppInput v-model="form.position" label="职位" placeholder="后端工程师" required />
        <AppTextarea v-model="form.description" label="备注（可选）" :rows="3" placeholder="JD 链接、内推人等" />
        <AppSelect v-model="form.channel" label="渠道" :options="CHANNEL_OPTIONS" placeholder="选择渠道" />
      </div>
      <template #footer>
        <AppButton variant="ghost" @click="showCreate = false">取消</AppButton>
        <AppButton :loading="loading" :disabled="!form.company || !form.position" @click="createApp">创建</AppButton>
      </template>
    </AppModal>

    <!-- Delete confirm -->
    <AppConfirmDialog
      :open="!!deleteTarget"
      title="删除投递记录"
      :message="`确定要删除「${deleteTarget?.company || ''} - ${deleteTarget?.position || ''}」吗？此操作不可撤销。`"
      :loading="deleteLoading"
      @confirm="confirmDelete"
      @cancel="deleteTarget = null"
    />
  </div>
</template>

<style scoped>
.filter-row { display: flex; flex-wrap: wrap; gap: var(--space-2); margin-bottom: var(--space-5); }
.filter-chip {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 6px 14px; border-radius: var(--radius-full);
  background: var(--color-surface); border: 1px solid var(--color-border);
  font-size: var(--text-sm); font-weight: 500; color: var(--color-text-muted);
  transition: all var(--duration-fast) var(--ease-out); cursor: pointer;
}
.filter-chip:hover { border-color: var(--color-border-strong); color: var(--color-text); }
.filter-chip--active {
  background: var(--gradient-primary); color: #fff; border-color: transparent;
  box-shadow: 0 4px 14px rgba(139, 92, 246, 0.32);
}
.filter-count {
  font-size: 11px;
  background: rgba(24,24,27,0.08);
  border-radius: 999px;
  padding: 1px 6px;
}
.filter-chip--active .filter-count { background: rgba(255,255,255,0.25); }
.app-list { display: flex; flex-direction: column; gap: var(--space-2); }
.app-row {
  display: flex; align-items: center; gap: var(--space-4);
  padding: var(--space-3) var(--space-4);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: border var(--duration-fast) var(--ease-out), box-shadow var(--duration-fast) var(--ease-out);
}
.app-row:hover { border-color: var(--color-border-strong); box-shadow: var(--shadow-sm); }
.app-main { flex: 1; min-width: 0; }
.app-company { font-weight: 600; font-size: var(--text-md); }
.app-position { font-size: var(--text-sm); }
.app-meta { display: flex; align-items: center; gap: var(--space-3); }
.app-date { font-size: var(--text-xs); }
.app-actions { display: flex; gap: var(--space-1); }
.form-stack { display: flex; flex-direction: column; gap: var(--space-3); }
.loading-state { display: flex; justify-content: center; padding: var(--space-7); }
</style>
```

- [ ] **Step 3: Rewrite `frontend/src/views/ApplicationDetail.vue`**

```vue
<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { applicationsApi } from '@/api/applications'
import { aiApi } from '@/api/ai'
import { useSettingsStore } from '@/stores/settings'
import { useAsync } from '@/composables/useAsync'
import { useToast } from '@/composables/useToast'
import AppPageHeader from '@/components/ui/AppPageHeader.vue'
import AppCard from '@/components/ui/AppCard.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppTextarea from '@/components/ui/AppTextarea.vue'
import AppSelect from '@/components/ui/AppSelect.vue'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import StatusBadge from '@/components/StatusBadge.vue'

const route = useRoute()
const router = useRouter()
const toast = useToast()
const settings = useSettingsStore()
const { loading, run } = useAsync()

const appId = computed(() => Number(route.params.id))
const app = ref(null)
const questions = ref([])
const questionsLoading = ref(false)

const STATUS_FLOW = [
  { value: 'Pending', label: '待处理' },
  { value: 'Applied', label: '已投递' },
  { value: 'Written Test', label: '笔试' },
  { value: 'Interviewing', label: '面试中' },
  { value: 'Offer', label: 'Offer' },
  { value: 'Rejected', label: '已拒绝' },
]

const editForm = ref({ company: '', position: '', description: '', channel: '' })
const editMode = ref(false)

onMounted(() => loadApp())

async function loadApp() {
  await run(async () => {
    app.value = await applicationsApi.get(appId.value)
    editForm.value = {
      company: app.value.company,
      position: app.value.position,
      description: app.value.description || '',
      channel: app.value.channel || '',
    }
  })
}

async function saveEdit() {
  await run(async () => {
    app.value = await applicationsApi.update(appId.value, editForm.value)
    editMode.value = false
    toast.success('已保存')
  })
}

async function changeStatus(newStatus) {
  await run(async () => {
    app.value = await applicationsApi.updateStatus(appId.value, newStatus)
    toast.success(`状态已更新为 ${newStatus}`)
  })
}

async function generateQuestions() {
  if (!settings.hasAnyLlmKey) {
    toast.error('请先在设置页面配置 AI 模型')
    return
  }
  questionsLoading.value = true
  try {
    const res = await aiApi.generateQuestions(app.value.position, app.value.description || '')
    questions.value = res.questions || []
  } catch (e) {
    toast.error(e.message)
  } finally {
    questionsLoading.value = false
  }
}

function formatDate(dt) {
  return dt ? new Date(dt).toLocaleString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) : ''
}

function goBack() {
  router.push({ name: 'applications' })
}
</script>

<template>
  <div>
    <div v-if="loading" class="loading-state"><AppSpinner :size="32" /></div>
    <template v-else-if="app">
      <AppPageHeader :title="`${app.company} — ${app.position}`">
        <template #actions>
          <AppButton variant="ghost" @click="goBack">← 返回列表</AppButton>
        </template>
      </AppPageHeader>

      <!-- Status + quick actions -->
      <AppCard>
        <div class="status-bar">
          <div class="status-flow">
            <div v-for="s in STATUS_FLOW" :key="s.value" class="status-step" :class="{ 'status-step--done': app.status === s.value, 'status-step--past': STATUS_FLOW.findIndex(x => x.value === app.status) > STATUS_FLOW.findIndex(x => x.value === s.value) }">
              <div class="step-dot" />
              <span class="step-label">{{ s.label }}</span>
            </div>
          </div>
          <AppSelect
            :model-value="app.status"
            :options="STATUS_FLOW"
            @update:model-value="changeStatus"
          />
        </div>
      </AppCard>

      <div class="detail-grid">
        <!-- Info card -->
        <AppCard title="投递信息">
          <template #actions>
            <AppButton size="sm" variant="ghost" @click="editMode = !editMode">{{ editMode ? '取消' : '编辑' }}</AppButton>
          </template>
          <template v-if="editMode">
            <div class="form-stack">
              <AppInput v-model="editForm.company" label="公司" />
              <AppInput v-model="editForm.position" label="职位" />
              <AppInput v-model="editForm.channel" label="渠道" />
              <AppTextarea v-model="editForm.description" label="备注" :rows="3" />
              <div class="form-actions">
                <AppButton :loading="loading" @click="saveEdit">保存</AppButton>
              </div>
            </div>
          </template>
          <template v-else>
            <div class="info-grid">
              <div class="info-item"><span class="info-label text-subtle">公司</span><span>{{ app.company }}</span></div>
              <div class="info-item"><span class="info-label text-subtle">职位</span><span>{{ app.position }}</span></div>
              <div class="info-item"><span class="info-label text-subtle">渠道</span><span>{{ app.channel || '-' }}</span></div>
              <div class="info-item"><span class="info-label text-subtle">创建时间</span><span>{{ formatDate(app.created_at) }}</span></div>
              <div v-if="app.description" class="info-item wide"><span class="info-label text-subtle">备注</span><span>{{ app.description }}</span></div>
            </div>
          </template>
        </AppCard>

        <!-- Status timeline -->
        <AppCard title="状态变更记录">
          <div v-if="app.status_logs.length === 0" class="text-muted" style="font-size: var(--text-sm)">暂无变更记录</div>
          <div v-else class="timeline">
            <div v-for="(log, i) in [...app.status_logs].reverse()" :key="log.id" class="timeline-item">
              <div class="timeline-line" :class="{ 'timeline-line--first': i === 0 }" />
              <div class="timeline-dot" :class="{ 'timeline-dot--first': i === 0 }" />
              <div class="timeline-content">
                <div class="timeline-badge">
                  <StatusBadge :status="log.old_status || '新建'" />
                  <span class="timeline-arrow">→</span>
                  <StatusBadge :status="log.new_status" />
                </div>
                <div class="timeline-meta">
                  <span class="text-subtle">{{ formatDate(log.created_at) }}</span>
                  <span v-if="log.note" class="text-muted">{{ log.note }}</span>
                </div>
              </div>
            </div>
          </div>
        </AppCard>
      </div>

      <!-- AI Questions -->
      <AppCard title="AI 面试题生成" subtitle="基于该职位的 JD 生成针对性面试题" style="margin-top: var(--space-4)">
        <template #actions>
          <AppButton size="sm" :loading="questionsLoading" @click="generateQuestions">生成题目</AppButton>
        </template>
        <div v-if="questionsLoading" class="loading-state"><AppSpinner :size="24" /></div>
        <div v-else-if="questions.length" class="question-list">
          <div v-for="(q, i) in questions" :key="i" class="question-item">
            <span class="q-num">{{ i + 1 }}</span>
            <span>{{ q }}</span>
          </div>
        </div>
        <div v-else class="text-muted" style="font-size: var(--text-sm)">点击右上角生成面试题</div>
      </AppCard>
    </template>
  </div>
</template>

<style scoped>
.loading-state { display: flex; justify-content: center; padding: var(--space-7); }
.detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); margin-top: var(--space-4); }
.status-bar {
  display: flex; align-items: center; justify-content: space-between; gap: var(--space-4);
  padding: var(--space-2) 0;
}
.status-flow { display: flex; gap: var(--space-4); }
.status-step { display: flex; flex-direction: column; align-items: center; gap: 4px; }
.step-dot {
  width: 10px; height: 10px; border-radius: 50%;
  background: rgba(24,24,27,0.12); transition: background var(--duration-fast) var(--ease-out);
}
.status-step--past .step-dot { background: var(--gradient-primary); opacity: 0.5; }
.status-step--done .step-dot { background: var(--gradient-primary); box-shadow: 0 0 0 4px rgba(139, 92, 246, 0.2); }
.step-label { font-size: 11px; color: var(--color-text-muted); white-space: nowrap; }
.status-step--done .step-label { color: var(--color-text); font-weight: 600; }
.info-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--space-3); }
.info-item { display: flex; flex-direction: column; gap: 2px; }
.info-item.wide { grid-column: span 2; }
.info-label { font-size: var(--text-xs); }
.form-stack { display: flex; flex-direction: column; gap: var(--space-3); }
.form-actions { display: flex; justify-content: flex-end; }
.timeline { display: flex; flex-direction: column; }
.timeline-item { display: flex; gap: var(--space-3); position: relative; padding-bottom: var(--space-4); }
.timeline-item:last-child { padding-bottom: 0; }
.timeline-line {
  position: absolute; left: 5px; top: 16px; bottom: 0; width: 2px;
  background: rgba(24,24,27,0.08);
}
.timeline-item:last-child .timeline-line { display: none; }
.timeline-dot {
  width: 12px; height: 12px; border-radius: 50%;
  background: rgba(24,24,27,0.12); flex-shrink: 0; margin-top: 4px;
}
.timeline-dot--first { background: var(--gradient-primary); }
.timeline-content { flex: 1; }
.timeline-badge { display: flex; align-items: center; gap: var(--space-2); }
.timeline-arrow { color: var(--color-text-subtle); }
.timeline-meta { display: flex; gap: var(--space-3); margin-top: 4px; font-size: var(--text-xs); }
.question-list { display: flex; flex-direction: column; gap: var(--space-2); }
.question-item {
  display: flex; align-items: flex-start; gap: var(--space-3);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  background: rgba(24,24,27,0.02);
  font-size: var(--text-sm);
  line-height: var(--leading-relaxed);
}
.q-num {
  flex-shrink: 0;
  width: 22px; height: 22px;
  border-radius: 50%;
  background: var(--gradient-primary-soft);
  color: var(--color-primary);
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 600;
}
</style>
```

- [ ] **Step 4: Verify in browser**

1. Open http://localhost:5173/applications → empty state with "新建投递" button
2. Create an application → row appears with status badge
3. Click the row → detail page with status flow dots, info grid, empty timeline
4. Change status via dropdown → timeline entry appears
5. Click "生成题目" → if AI configured, 10 questions appear
6. Back button returns to filtered list

- [ ] **Step 5: Commit**

```bash
cd /Users/jarrett/Desktop/SpringPilot
git add frontend/src/components/StatusBadge.vue frontend/src/views/Applications.vue frontend/src/views/ApplicationDetail.vue
git commit -m "feat(frontend): implement Applications list with filters, detail with status timeline, and AI question generation"
```

---

## Task 16: Study Tasks

**Context:** Task board for daily study planning — LeetCode practice, interview prep, etc. Tasks support tags and completion toggling.

**What it does:**
- List of tasks with completion checkboxes, tag badges, due dates
- Create modal (title, description, tags comma-separated, due date)
- Edit inline (toggle complete, edit modal)
- Delete with confirmation
- Filter: All / Active / Completed

**Files:**
- Rewrite: `frontend/src/views/StudyTasks.vue`

- [ ] **Step 1: Rewrite `frontend/src/views/StudyTasks.vue`**

```vue
<script setup>
import { ref, computed, onMounted } from 'vue'
import { studyTasksApi } from '@/api/studyTasks'
import { useAsync } from '@/composables/useAsync'
import { useToast } from '@/composables/useToast'
import AppPageHeader from '@/components/ui/AppPageHeader.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppTextarea from '@/components/ui/AppTextarea.vue'
import AppModal from '@/components/ui/AppModal.vue'
import AppConfirmDialog from '@/components/ui/AppConfirmDialog.vue'
import AppEmptyState from '@/components/ui/AppEmptyState.vue'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppTag from '@/components/ui/AppTag.vue'
import AppCheckbox from '@/components/ui/AppCheckbox.vue'

const toast = useToast()
const { loading, run } = useAsync()

const tasks = ref([])
const filter = ref('all')
const showCreate = ref(false)
const editTarget = ref(null)
const deleteTarget = ref(null)
const deleteLoading = ref(false)

const form = ref({ title: '', description: '', tags: '', due_date: '' })

const filteredTasks = computed(() => {
  if (filter.value === 'active') return tasks.value.filter(t => !t.completed)
  if (filter.value === 'completed') return tasks.value.filter(t => t.completed)
  return tasks.value
})

const counts = computed(() => ({
  all: tasks.value.length,
  active: tasks.value.filter(t => !t.completed).length,
  completed: tasks.value.filter(t => t.completed).length,
}))

onMounted(() => load())

async function load() {
  await run(async () => {
    tasks.value = await studyTasksApi.list()
  })
}

function openCreate() {
  form.value = { title: '', description: '', tags: '', due_date: '' }
  showCreate.value = true
}

function openEdit(task) {
  editTarget.value = task
  form.value = {
    title: task.title,
    description: task.description || '',
    tags: task.tags || '',
    due_date: task.due_date ? task.due_date.slice(0, 10) : '',
  }
}

async function createTask() {
  const payload = {
    title: form.value.title,
    description: form.value.description || null,
    tags: form.value.tags || null,
    due_date: form.value.due_date ? new Date(form.value.due_date).toISOString() : null,
  }
  await run(async () => {
    const task = await studyTasksApi.create(payload)
    tasks.value.unshift(task)
    showCreate.value = false
    toast.success('任务已创建')
  })
}

async function saveEdit() {
  const payload = {
    title: form.value.title,
    description: form.value.description || null,
    tags: form.value.tags || null,
    due_date: form.value.due_date ? new Date(form.value.due_date).toISOString() : null,
  }
  await run(async () => {
    const updated = await studyTasksApi.update(editTarget.value.id, payload)
    const idx = tasks.value.findIndex(t => t.id === updated.id)
    if (idx !== -1) tasks.value[idx] = updated
    editTarget.value = null
    toast.success('任务已更新')
  })
}

async function toggleComplete(task) {
  await run(async () => {
    const updated = await studyTasksApi.update(task.id, { completed: !task.completed })
    const idx = tasks.value.findIndex(t => t.id === updated.id)
    if (idx !== -1) tasks.value[idx] = updated
  })
}

async function confirmDelete() {
  deleteLoading.value = true
  try {
    await studyTasksApi.remove(deleteTarget.value.id)
    tasks.value = tasks.value.filter(t => t.id !== deleteTarget.value.id)
    deleteTarget.value = null
    toast.success('已删除')
  } catch (e) {
    toast.error(e.message)
  } finally {
    deleteLoading.value = false
  }
}

function parseTags(tags) {
  if (!tags) return []
  return tags.split(',').map(t => t.trim()).filter(Boolean)
}

function formatDate(dt) {
  return dt ? new Date(dt).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }) : ''
}

function isOverdue(task) {
  return task.due_date && !task.completed && new Date(task.due_date) < new Date()
}
</script>

<template>
  <div>
    <AppPageHeader title="学习任务" subtitle="管理每日学习计划与进度">
      <template #actions>
        <AppButton @click="openCreate">+ 新建任务</AppButton>
      </template>
    </AppPageHeader>

    <!-- Filter -->
    <div class="filter-row">
      <button v-for="f in ['all', 'active', 'completed']" :key="f" class="filter-chip" :class="{ 'filter-chip--active': filter === f }" @click="filter = f">
        {{ f === 'all' ? '全部' : f === 'active' ? '进行中' : '已完成' }}
        <span class="filter-count">{{ counts[f] }}</span>
      </button>
    </div>

    <!-- List -->
    <div v-if="loading" class="loading-state"><AppSpinner :size="32" /></div>
    <AppEmptyState v-else-if="filteredTasks.length === 0" icon="✓" title="暂无任务" description="创建一个学习任务开始吧">
      <template #action><AppButton @click="openCreate">新建任务</AppButton></template>
    </AppEmptyState>
    <div v-else class="task-list">
      <div v-for="task in filteredTasks" :key="task.id" class="task-row" :class="{ 'task-row--done': task.completed }">
        <AppCheckbox :model-value="task.completed" @update:model-value="toggleComplete(task)" />
        <div class="task-body" @click="openEdit(task)">
          <div class="task-title" :class="{ 'task-title--done': task.completed }">{{ task.title }}</div>
          <div class="task-meta">
            <AppTag v-for="tag in parseTags(task.tags)" :key="tag">{{ tag }}</AppTag>
            <span v-if="task.due_date" class="task-due text-subtle" :class="{ 'task-due--overdue': isOverdue(task) }">
              {{ formatDate(task.due_date) }}
            </span>
          </div>
        </div>
        <button class="task-delete" @click.stop="deleteTarget = task">×</button>
      </div>
    </div>

    <!-- Create modal -->
    <AppModal :open="showCreate" title="新建学习任务" size="md" @close="showCreate = false">
      <div class="form-stack">
        <AppInput v-model="form.title" label="标题" placeholder="LeetCode 两数之和" required />
        <AppTextarea v-model="form.description" label="描述（可选）" :rows="2" />
        <AppInput v-model="form.tags" label="标签" placeholder="algorithm, Python（逗号分隔）" />
        <AppInput v-model="form.due_date" label="截止日期" type="date" />
      </div>
      <template #footer>
        <AppButton variant="ghost" @click="showCreate = false">取消</AppButton>
        <AppButton :loading="loading" :disabled="!form.title" @click="createTask">创建</AppButton>
      </template>
    </AppModal>

    <!-- Edit modal -->
    <AppModal :open="!!editTarget" title="编辑任务" size="md" @close="editTarget = null">
      <div class="form-stack">
        <AppInput v-model="form.title" label="标题" required />
        <AppTextarea v-model="form.description" label="描述" :rows="2" />
        <AppInput v-model="form.tags" label="标签" placeholder="逗号分隔" />
        <AppInput v-model="form.due_date" label="截止日期" type="date" />
      </div>
      <template #footer>
        <AppButton variant="ghost" @click="editTarget = null">取消</AppButton>
        <AppButton :loading="loading" @click="saveEdit">保存</AppButton>
      </template>
    </AppModal>

    <!-- Delete confirm -->
    <AppConfirmDialog
      :open="!!deleteTarget"
      title="删除任务"
      :message="`确定要删除「${deleteTarget?.title || ''}」吗？`"
      :loading="deleteLoading"
      @confirm="confirmDelete"
      @cancel="deleteTarget = null"
    />
  </div>
</template>

<style scoped>
.filter-row { display: flex; gap: var(--space-2); margin-bottom: var(--space-5); }
.filter-chip {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 6px 14px; border-radius: var(--radius-full);
  background: var(--color-surface); border: 1px solid var(--color-border);
  font-size: var(--text-sm); font-weight: 500; color: var(--color-text-muted);
  transition: all var(--duration-fast) var(--ease-out); cursor: pointer;
}
.filter-chip:hover { border-color: var(--color-border-strong); color: var(--color-text); }
.filter-chip--active {
  background: var(--gradient-primary); color: #fff; border-color: transparent;
  box-shadow: 0 4px 14px rgba(139, 92, 246, 0.32);
}
.filter-count {
  font-size: 11px; background: rgba(24,24,27,0.08); border-radius: 999px; padding: 1px 6px;
}
.filter-chip--active .filter-count { background: rgba(255,255,255,0.25); }
.task-list { display: flex; flex-direction: column; gap: var(--space-2); }
.task-row {
  display: flex; align-items: center; gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  transition: border var(--duration-fast) var(--ease-out);
}
.task-row:hover { border-color: var(--color-border-strong); }
.task-row--done { opacity: 0.6; }
.task-body { flex: 1; cursor: pointer; min-width: 0; }
.task-title { font-weight: 500; }
.task-title--done { text-decoration: line-through; color: var(--color-text-muted); }
.task-meta { display: flex; align-items: center; gap: var(--space-2); margin-top: 4px; }
.task-due { font-size: var(--text-xs); }
.task-due--overdue { color: var(--color-danger) !important; font-weight: 500; }
.task-delete {
  color: var(--color-text-subtle); font-size: 18px; padding: 4px 8px;
  border-radius: var(--radius-sm); transition: all var(--duration-fast) var(--ease-out);
}
.task-delete:hover { background: rgba(244, 63, 94, 0.1); color: var(--color-danger); }
.form-stack { display: flex; flex-direction: column; gap: var(--space-3); }
.loading-state { display: flex; justify-content: center; padding: var(--space-7); }
</style>
```

- [ ] **Step 2: Verify in browser**

1. Open http://localhost:5173/study-tasks → empty state
2. Create a task with tags → appears with tag badges
3. Click checkbox → task toggles complete, styles dim
4. Click task body → edit modal pre-fills
5. Set a past due date → due date shows in red
6. Delete → confirmation dialog, then removed

- [ ] **Step 3: Commit**

```bash
cd /Users/jarrett/Desktop/SpringPilot
git add frontend/src/views/StudyTasks.vue
git commit -m "feat(frontend): implement Study Tasks page with CRUD, tags, filters, and completion toggling"
```

---

## Task 17: JD Analysis

**Context:** Paste a job description, optionally provide a resume, and get AI-powered skill extraction + gap analysis.

**What it does:**
- Textarea for JD input (required)
- Textarea for resume (optional)
- "Analyze" button → calls `/api/ai/analyze-jd`
- Results displayed as structured cards: key skills, requirements, match analysis, gaps, suggestions

**Files:**
- Rewrite: `frontend/src/views/JDAnalysis.vue`

- [ ] **Step 1: Rewrite `frontend/src/views/JDAnalysis.vue`**

```vue
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
      <!-- Input panel -->
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

      <!-- Results panel -->
      <div v-if="analyzing" class="loading-state"><AppSpinner :size="32" /></div>
      <AppEmptyState v-else-if="!result" icon="◎" title="等待分析" description="输入 JD 后点击分析按钮" />
      <template v-else>
        <!-- Raw fallback -->
        <div v-if="result.raw" class="result-cards">
          <AppCard title="AI 分析结果">
            <div class="result-raw">{{ result.raw }}</div>
          </AppCard>
        </div>

        <!-- Structured results -->
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
```

- [ ] **Step 2: Verify in browser**

1. Open http://localhost:5173/jd-analysis → split layout: input left, empty right
2. Paste a JD, click "开始分析" → spinner, then structured result cards appear
3. Paste both JD and resume → match_analysis card appears
4. If no AI key configured → error toast

- [ ] **Step 3: Commit**

```bash
cd /Users/jarrett/Desktop/SpringPilot
git add frontend/src/views/JDAnalysis.vue
git commit -m "feat(frontend): implement JD Analysis page with AI-powered skill extraction and gap analysis"
```

---


## Task 18: Mock Interview

**Context:** Chat-style interface where the AI plays the interviewer, asks follow-up questions based on answers.

**What it does:**
- User enters a target position to start
- Chat interface: user types answers, AI replies with follow-ups or feedback
- History persisted in component state (not in DB — stateless per session)
- "New Interview" resets the chat

**Files:**
- Create: `frontend/src/components/ChatMessage.vue`
- Rewrite: `frontend/src/views/MockInterview.vue`

- [ ] **Step 1: Create `frontend/src/components/ChatMessage.vue`**

```vue
<script setup>
defineProps({
  role: { type: String, required: true }, // 'assistant' | 'user'
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
.msg-avatar--assistant {
  background: var(--gradient-primary);
  color: #fff;
}
.msg-avatar--user {
  background: rgba(24,24,27,0.08);
  color: var(--color-text-muted);
}
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
```

- [ ] **Step 2: Rewrite `frontend/src/views/MockInterview.vue`**

```vue
<script setup>
import { ref, nextTick, computed } from 'vue'
import { aiApi } from '@/api/ai'
import { useSettingsStore } from '@/stores/settings'
import { useToast } from '@/composables/useToast'
import AppPageHeader from '@/components/ui/AppPageHeader.vue'
import AppCard from '@/components/ui/AppCard.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import AppEmptyState from '@/components/ui/AppEmptyState.vue'
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

    <!-- Start screen -->
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

    <!-- Chat interface -->
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

/* Typing indicator */
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
```

- [ ] **Step 3: Verify in browser**

1. Open http://localhost:5173/mock-interview → start screen with position input
2. Enter "后端工程师" → click "开始" → AI greeting appears
3. Type answer, Enter or click "发送" → AI replies with follow-up
4. Click "重新开始" → back to start screen

- [ ] **Step 4: Commit**

```bash
cd /Users/jarrett/Desktop/SpringPilot
git add frontend/src/components/ChatMessage.vue frontend/src/views/MockInterview.vue
git commit -m "feat(frontend): implement Mock Interview chat with AI interviewer and typing indicator"
```

---

## Task 19: Fitness Overview

**Context:** The main fitness hub page. Combines weight tracking, diet logging, and training check-ins with charts and quick-add modals.

**What it does:**
- Top row: stat cards (current weight, today's calories, weekly training count, calorie deficit)
- Weight section: chart (reuse WeightChart) + add record modal
- Diet section: today's meals + add log modal (with AI calorie estimation)
- Training section: recent logs + add log modal

**Files:**
- Create: `frontend/src/components/TrainingHeatmap.vue`
- Rewrite: `frontend/src/views/FitnessOverview.vue`

- [ ] **Step 1: Create `frontend/src/components/TrainingHeatmap.vue`**

```vue
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
```

- [ ] **Step 2: Rewrite `frontend/src/views/FitnessOverview.vue`**

```vue
<script setup>
import { ref, computed, onMounted } from 'vue'
import { weightApi, dietApi, trainingApi } from '@/api/fitness'
import { aiApi } from '@/api/ai'
import { useSettingsStore } from '@/stores/settings'
import { useAsync } from '@/composables/useAsync'
import { useToast } from '@/composables/useToast'
import AppPageHeader from '@/components/ui/AppPageHeader.vue'
import AppCard from '@/components/ui/AppCard.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppTextarea from '@/components/ui/AppTextarea.vue'
import AppSelect from '@/components/ui/AppSelect.vue'
import AppModal from '@/components/ui/AppModal.vue'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import AppEmptyState from '@/components/ui/AppEmptyState.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import WeightChart from '@/components/WeightChart.vue'
import CalorieChart from '@/components/CalorieChart.vue'
import TrainingHeatmap from '@/components/TrainingHeatmap.vue'

const settings = useSettingsStore()
const toast = useToast()
const { loading, run } = useAsync()

const weightRecords = ref([])
const dietLogs = ref([])
const trainingLogs = ref([])

const showWeightModal = ref(false)
const showDietModal = ref(false)
const showTrainingModal = ref(false)

const weightForm = ref({ weight_kg: '', note: '' })
const dietForm = ref({ meal_type: 'breakfast', content: '', calories: '' })
const trainingForm = ref({ training_type: 'strength', content: '', duration_minutes: '' })

const estimatingCalories = ref(false)

const MEAL_OPTIONS = [
  { value: 'breakfast', label: '早餐' },
  { value: 'lunch', label: '午餐' },
  { value: 'dinner', label: '晚餐' },
  { value: 'snack', label: '加餐' },
]
const TRAINING_TYPE_OPTIONS = [
  { value: 'strength', label: '力量训练' },
  { value: 'cardio', label: '有氧' },
  { value: 'stretching', label: '拉伸' },
]

// Stats
const currentWeight = computed(() => {
  if (!weightRecords.value.length) return '-'
  return weightRecords.value[0].weight_kg
})
const todayStr = new Date().toISOString().slice(0, 10)
const todayCalories = computed(() => {
  return dietLogs.value
    .filter(l => l.recorded_at.slice(0, 10) === todayStr)
    .reduce((sum, l) => sum + (l.calories || 0), 0)
})
const weeklyTraining = computed(() => {
  const weekAgo = new Date(Date.now() - 7 * 86400000)
  return trainingLogs.value.filter(t => new Date(t.recorded_at) >= weekAgo).length
})
const todayDietLogs = computed(() =>
  dietLogs.value.filter(l => l.recorded_at.slice(0, 10) === todayStr)
)

const stats = computed(() => [
  { label: '当前体重', value: currentWeight.value === '-' ? '-' : `${currentWeight.value} kg`, gradient: 'var(--gradient-primary)' },
  { label: '今日热量', value: `${todayCalories.value} kcal`, gradient: 'var(--gradient-warning)' },
  { label: '本周训练', value: `${weeklyTraining.value} 次`, gradient: 'var(--gradient-success)' },
])

onMounted(() => loadData())

async function loadData() {
  await run(async () => {
    const [w, d, t] = await Promise.all([
      weightApi.list(90),
      dietApi.list(),
      trainingApi.list(30),
    ])
    weightRecords.value = w
    dietLogs.value = d
    trainingLogs.value = t
  })
}

async function addWeight() {
  await run(async () => {
    const record = await weightApi.create({
      weight_kg: Number(weightForm.value.weight_kg),
      note: weightForm.value.note || null,
    })
    weightRecords.value.unshift(record)
    showWeightModal.value = false
    weightForm.value = { weight_kg: '', note: '' }
    toast.success('体重已记录')
  })
}

async function addDiet() {
  await run(async () => {
    const record = await dietApi.create({
      meal_type: dietForm.value.meal_type,
      content: dietForm.value.content,
      calories: dietForm.value.calories ? Number(dietForm.value.calories) : null,
    })
    dietLogs.value.unshift(record)
    showDietModal.value = false
    dietForm.value = { meal_type: 'breakfast', content: '', calories: '' }
    toast.success('饮食已记录')
  })
}

async function estimateCalories() {
  if (!dietForm.value.content.trim()) return
  if (!settings.hasAnyLlmKey) {
    toast.error('请先在设置页面配置 AI 模型')
    return
  }
  estimatingCalories.value = true
  try {
    const res = await aiApi.estimateCalories(dietForm.value.content)
    dietForm.value.calories = String(res.calories)
    toast.success(`AI 估算: ${res.calories} kcal`)
  } catch (e) {
    toast.error(e.message)
  } finally {
    estimatingCalories.value = false
  }
}

async function addTraining() {
  await run(async () => {
    const record = await trainingApi.create({
      training_type: trainingForm.value.training_type,
      content: trainingForm.value.content,
      duration_minutes: trainingForm.value.duration_minutes ? Number(trainingForm.value.duration_minutes) : null,
    })
    trainingLogs.value.unshift(record)
    showTrainingModal.value = false
    trainingForm.value = { training_type: 'strength', content: '', duration_minutes: '' }
    toast.success('训练已记录')
  })
}

async function toggleTrainingComplete(log) {
  await run(async () => {
    const updated = await trainingApi.update(log.id, { completed: !log.completed })
    const idx = trainingLogs.value.findIndex(t => t.id === updated.id)
    if (idx !== -1) trainingLogs.value[idx] = updated
  })
}

function mealTypeLabel(type) {
  return MEAL_OPTIONS.find(m => m.value === type)?.label || type
}

function trainingTypeLabel(type) {
  return TRAINING_TYPE_OPTIONS.find(t => t.value === type)?.label || type
}
</script>

<template>
  <div>
    <AppPageHeader title="数据概览" subtitle="体重、饮食与训练数据一览" />

    <div v-if="loading" class="loading-state"><AppSpinner :size="32" /></div>
    <template v-else>
      <!-- Stat cards -->
      <div class="stats-row">
        <div v-for="s in stats" :key="s.label" class="stat-card">
          <div class="stat-value-row">
            <span class="stat-value">{{ s.value }}</span>
            <span class="stat-dot" :style="{ background: s.gradient }"></span>
          </div>
          <div class="stat-label">{{ s.label }}</div>
        </div>
      </div>

      <!-- Weight + Diet charts -->
      <div class="charts-row">
        <AppCard title="体重趋势" subtitle="近 90 天">
          <template #actions>
            <AppButton size="sm" @click="showWeightModal = true">+ 记录体重</AppButton>
          </template>
          <WeightChart :records="weightRecords" />
        </AppCard>
        <AppCard title="热量摄入" subtitle="近 7 天">
          <template #actions>
            <AppButton size="sm" @click="showDietModal = true">+ 记录饮食</AppButton>
          </template>
          <CalorieChart :logs="dietLogs" />
        </AppCard>
      </div>

      <div class="bottom-row">
        <!-- Today's diet -->
        <AppCard title="今日饮食">
          <div v-if="todayDietLogs.length === 0" class="text-muted" style="font-size: var(--text-sm)">今天还没有记录</div>
          <div v-else class="diet-list">
            <div v-for="log in todayDietLogs" :key="log.id" class="diet-item">
              <AppBadge :variant="log.meal_type === 'snack' ? 'neutral' : 'primary'" soft>{{ mealTypeLabel(log.meal_type) }}</AppBadge>
              <span class="diet-content">{{ log.content }}</span>
              <span class="diet-cal text-subtle">{{ log.calories ? `${log.calories} kcal` : '-' }}</span>
            </div>
          </div>
        </AppCard>

        <!-- Training -->
        <AppCard title="训练记录">
          <template #actions>
            <AppButton size="sm" @click="showTrainingModal = true">+ 记录训练</AppButton>
          </template>
          <TrainingHeatmap :logs="trainingLogs" />
          <div class="training-list">
            <div v-for="log in trainingLogs.slice(0, 5)" :key="log.id" class="training-item" @click="toggleTrainingComplete(log)">
              <div class="training-check" :class="{ 'training-check--done': log.completed }">✓</div>
              <div class="training-info">
                <span class="training-type">{{ trainingTypeLabel(log.training_type) }}</span>
                <span class="training-content text-muted">{{ log.content }}</span>
              </div>
              <span v-if="log.duration_minutes" class="text-subtle">{{ log.duration_minutes }}分钟</span>
            </div>
          </div>
        </AppCard>
      </div>
    </template>

    <!-- Weight modal -->
    <AppModal :open="showWeightModal" title="记录体重" size="sm" @close="showWeightModal = false">
      <div class="form-stack">
        <AppInput v-model="weightForm.weight_kg" label="体重 (kg)" type="number" placeholder="75.5" required />
        <AppInput v-model="weightForm.note" label="备注（可选）" placeholder="早晨空腹" />
      </div>
      <template #footer>
        <AppButton variant="ghost" @click="showWeightModal = false">取消</AppButton>
        <AppButton :loading="loading" :disabled="!weightForm.weight_kg" @click="addWeight">保存</AppButton>
      </template>
    </AppModal>

    <!-- Diet modal -->
    <AppModal :open="showDietModal" title="记录饮食" size="sm" @close="showDietModal = false">
      <div class="form-stack">
        <AppSelect v-model="dietForm.meal_type" label="餐次" :options="MEAL_OPTIONS" />
        <AppTextarea v-model="dietForm.content" label="内容" :rows="2" placeholder="鸡胸肉、糙米饭、蔬菜沙拉" required />
        <div class="calorie-row">
          <AppInput v-model="dietForm.calories" label="热量 (kcal)" type="number" placeholder="手动输入或 AI 估算" />
          <AppButton size="sm" variant="ghost" :loading="estimatingCalories" @click="estimateCalories">AI 估算</AppButton>
        </div>
      </div>
      <template #footer>
        <AppButton variant="ghost" @click="showDietModal = false">取消</AppButton>
        <AppButton :loading="loading" :disabled="!dietForm.content" @click="addDiet">保存</AppButton>
      </template>
    </AppModal>

    <!-- Training modal -->
    <AppModal :open="showTrainingModal" title="记录训练" size="sm" @close="showTrainingModal = false">
      <div class="form-stack">
        <AppSelect v-model="trainingForm.training_type" label="类型" :options="TRAINING_TYPE_OPTIONS" />
        <AppTextarea v-model="trainingForm.content" label="内容" :rows="2" placeholder="卧推 3x8, 深蹲 3x10" required />
        <AppInput v-model="trainingForm.duration_minutes" label="时长（分钟）" type="number" placeholder="60" />
      </div>
      <template #footer>
        <AppButton variant="ghost" @click="showTrainingModal = false">取消</AppButton>
        <AppButton :loading="loading" :disabled="!trainingForm.content" @click="addTraining">保存</AppButton>
      </template>
    </AppModal>
  </div>
</template>

<style scoped>
.loading-state { display: flex; justify-content: center; padding: var(--space-7); }
.stats-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-4); margin-bottom: var(--space-5); }
.stat-card {
  background: var(--color-surface); border: 1px solid var(--color-border);
  border-radius: var(--radius-lg); padding: var(--space-4) var(--space-5);
  box-shadow: var(--shadow-sm);
}
.stat-value-row { display: flex; align-items: baseline; gap: var(--space-2); }
.stat-value { font-size: var(--text-2xl); font-weight: 700; letter-spacing: -0.02em; }
.stat-dot { width: 8px; height: 8px; border-radius: 50%; margin-left: auto; }
.stat-label { font-size: var(--text-sm); color: var(--color-text-muted); margin-top: 4px; }
.charts-row { display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--space-4); margin-bottom: var(--space-4); }
.bottom-row { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); }
.form-stack { display: flex; flex-direction: column; gap: var(--space-3); }
.calorie-row { display: flex; gap: var(--space-2); align-items: flex-end; }
.calorie-row > :first-child { flex: 1; }

.diet-list { display: flex; flex-direction: column; gap: var(--space-2); }
.diet-item {
  display: flex; align-items: center; gap: var(--space-3);
  padding: var(--space-2) 0; border-bottom: 1px solid var(--color-border);
  font-size: var(--text-sm);
}
.diet-item:last-child { border-bottom: none; }
.diet-content { flex: 1; }
.diet-cal { font-size: var(--text-xs); white-space: nowrap; }

.training-list { display: flex; flex-direction: column; gap: var(--space-2); margin-top: var(--space-4); }
.training-item {
  display: flex; align-items: center; gap: var(--space-3);
  padding: var(--space-2) var(--space-3); border-radius: var(--radius-md);
  cursor: pointer; transition: background var(--duration-fast) var(--ease-out);
  font-size: var(--text-sm);
}
.training-item:hover { background: rgba(24,24,27,0.03); }
.training-check {
  width: 20px; height: 20px; border-radius: 5px;
  border: 1.5px solid var(--color-border-strong);
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 11px; color: transparent; flex-shrink: 0;
  transition: all var(--duration-fast) var(--ease-out);
}
.training-check--done {
  background: var(--gradient-success); border-color: transparent; color: #fff;
}
.training-info { flex: 1; }
.training-type { font-weight: 500; }
.training-content { margin-left: var(--space-2); }
</style>
```

- [ ] **Step 3: Verify in browser**

1. Open http://localhost:5173/fitness → 3 stat cards at top
2. Click "+ 记录体重" → modal, enter weight, save → chart updates
3. Click "+ 记录饮食" → modal with AI calorie estimate button, save → today's diet list updates
4. Click "+ 记录训练" → modal, save → heatmap shows green cells, training list updates
5. Click training row → toggles complete checkmark

- [ ] **Step 4: Commit**

```bash
cd /Users/jarrett/Desktop/SpringPilot
git add frontend/src/components/TrainingHeatmap.vue frontend/src/views/FitnessOverview.vue
git commit -m "feat(frontend): implement Fitness Overview with weight/diet/training tracking, charts, and AI calorie estimation"
```

---

## Task 20: Trainer Plans

**Context:** Upload trainer-provided training plan documents (PDF/DOCX/MD), view parsed content, and delete plans.

**What it does:**
- List of uploaded plans with title, date range, and parsed content preview
- Upload modal with file picker, title, optional date range
- View parsed content in expandable card (markdown rendered as plain text)
- Delete with confirmation

**Files:**
- Rewrite: `frontend/src/views/TrainerPlans.vue`

- [ ] **Step 1: Rewrite `frontend/src/views/TrainerPlans.vue`**

```vue
<script setup>
import { ref, onMounted } from 'vue'
import { trainerPlansApi } from '@/api/trainerPlans'
import { useAsync } from '@/composables/useAsync'
import { useToast } from '@/composables/useToast'
import AppPageHeader from '@/components/ui/AppPageHeader.vue'
import AppCard from '@/components/ui/AppCard.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppModal from '@/components/ui/AppModal.vue'
import AppConfirmDialog from '@/components/ui/AppConfirmDialog.vue'
import AppEmptyState from '@/components/ui/AppEmptyState.vue'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import AppBadge from '@/components/ui/AppBadge.vue'

const toast = useToast()
const { loading, run } = useAsync()

const plans = ref([])
const showUpload = ref(false)
const deleteTarget = ref(null)
const deleteLoading = ref(false)
const uploadLoading = ref(false)
const expandedPlan = ref(null)

const form = ref({ title: '', plan_date_range: '', file: null })
const fileInput = ref(null)

onMounted(() => load())

async function load() {
  await run(async () => {
    plans.value = await trainerPlansApi.list()
  })
}

function openUpload() {
  form.value = { title: '', plan_date_range: '', file: null }
  showUpload.value = true
}

function onFileChange(e) {
  form.value.file = e.target.files[0] || null
}

async function uploadPlan() {
  if (!form.value.file || !form.value.title.trim()) {
    toast.warning('请填写标题并选择文件')
    return
  }
  uploadLoading.value = true
  try {
    const plan = await trainerPlansApi.upload(
      form.value.file,
      form.value.title.trim(),
      form.value.plan_date_range || null,
    )
    plans.value.unshift(plan)
    showUpload.value = false
    toast.success('训练计划已上传并解析')
  } catch (e) {
    toast.error(e.message)
  } finally {
    uploadLoading.value = false
  }
}

async function confirmDelete() {
  deleteLoading.value = true
  try {
    await trainerPlansApi.remove(deleteTarget.value.id)
    plans.value = plans.value.filter(p => p.id !== deleteTarget.value.id)
    if (expandedPlan.value === deleteTarget.value?.id) expandedPlan.value = null
    deleteTarget.value = null
    toast.success('已删除')
  } catch (e) {
    toast.error(e.message)
  } finally {
    deleteLoading.value = false
  }
}

function toggleExpand(id) {
  expandedPlan.value = expandedPlan.value === id ? null : id
}

function formatDate(dt) {
  return dt ? new Date(dt).toLocaleDateString('zh-CN') : ''
}
</script>

<template>
  <div>
    <AppPageHeader title="训练计划" subtitle="上传教练提供的训练计划文档，自动解析内容">
      <template #actions>
        <AppButton @click="openUpload">+ 上传计划</AppButton>
      </template>
    </AppPageHeader>

    <div v-if="loading" class="loading-state"><AppSpinner :size="32" /></div>
    <AppEmptyState v-else-if="plans.length === 0" icon="◇" title="暂无训练计划" description="上传教练给的 PDF / DOCX / MD 文件">
      <template #action><AppButton @click="openUpload">上传计划</AppButton></template>
    </AppEmptyState>
    <div v-else class="plan-list">
      <AppCard v-for="plan in plans" :key="plan.id" class="plan-card">
        <div class="plan-header" @click="toggleExpand(plan.id)">
          <div class="plan-info">
            <div class="plan-title">{{ plan.title }}</div>
            <div class="plan-meta">
              <span v-if="plan.plan_date_range" class="text-muted">{{ plan.plan_date_range }}</span>
              <span class="text-subtle">{{ formatDate(plan.created_at) }}</span>
            </div>
          </div>
          <div class="plan-actions" @click.stop>
            <AppBadge v-if="plan.parsed_content" variant="success" soft>已解析</AppBadge>
            <AppBadge v-else variant="warning" soft>未解析</AppBadge>
            <AppButton size="sm" variant="ghost" @click="deleteTarget = plan">删除</AppButton>
          </div>
          <span class="plan-expand" :class="{ 'plan-expand--open': expandedPlan === plan.id }">▾</span>
        </div>
        <div v-if="expandedPlan === plan.id" class="plan-content">
          <div v-if="plan.parsed_content" class="parsed-text">{{ plan.parsed_content }}</div>
          <div v-else class="text-muted">解析内容为空</div>
        </div>
      </AppCard>
    </div>

    <!-- Upload modal -->
    <AppModal :open="showUpload" title="上传训练计划" size="md" @close="showUpload = false">
      <div class="form-stack">
        <AppInput v-model="form.title" label="标题" placeholder="4月训练计划" required />
        <AppInput v-model="form.plan_date_range" label="日期范围（可选）" placeholder="2026-04-01 ~ 2026-04-30" />
        <div class="file-field">
          <label class="file-label">文件</label>
          <input ref="fileInput" type="file" class="file-input" accept=".pdf,.docx,.md" @change="onFileChange" />
          <div v-if="form.file" class="file-name">{{ form.file.name }}</div>
        </div>
      </div>
      <template #footer>
        <AppButton variant="ghost" @click="showUpload = false">取消</AppButton>
        <AppButton :loading="uploadLoading" :disabled="!form.file || !form.title" @click="uploadPlan">上传并解析</AppButton>
      </template>
    </AppModal>

    <!-- Delete confirm -->
    <AppConfirmDialog
      :open="!!deleteTarget"
      title="删除训练计划"
      :message="`确定要删除「${deleteTarget?.title || ''}」吗？`"
      :loading="deleteLoading"
      @confirm="confirmDelete"
      @cancel="deleteTarget = null"
    />
  </div>
</template>

<style scoped>
.loading-state { display: flex; justify-content: center; padding: var(--space-7); }
.plan-list { display: flex; flex-direction: column; gap: var(--space-3); }
.plan-card { padding: 0; }
.plan-header {
  display: flex; align-items: center; gap: var(--space-4);
  padding: var(--space-4) var(--space-5);
  cursor: pointer;
  transition: background var(--duration-fast) var(--ease-out);
}
.plan-header:hover { background: rgba(24,24,27,0.02); }
.plan-info { flex: 1; min-width: 0; }
.plan-title { font-weight: 600; font-size: var(--text-md); }
.plan-meta { display: flex; gap: var(--space-3); font-size: var(--text-xs); margin-top: 2px; }
.plan-actions { display: flex; align-items: center; gap: var(--space-2); }
.plan-expand {
  color: var(--color-text-subtle); font-size: 14px;
  transition: transform var(--duration-fast) var(--ease-out);
}
.plan-expand--open { transform: rotate(180deg); }
.plan-content {
  padding: 0 var(--space-5) var(--space-5);
  border-top: 1px solid var(--color-border);
}
.parsed-text {
  padding-top: var(--space-4);
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  line-height: var(--leading-relaxed);
  white-space: pre-wrap;
  color: var(--color-text);
  max-height: 400px;
  overflow-y: auto;
}
.form-stack { display: flex; flex-direction: column; gap: var(--space-3); }
.file-field { display: flex; flex-direction: column; gap: 6px; }
.file-label { font-size: var(--text-sm); font-weight: 500; }
.file-input {
  font-family: var(--font-sans);
  font-size: var(--text-sm);
  padding: 8px 12px;
  border: 1px dashed var(--color-border-strong);
  border-radius: var(--radius-md);
  background: rgba(24,24,27,0.02);
  color: var(--color-text);
}
.file-input::file-selector-button {
  background: var(--gradient-primary);
  color: #fff;
  border: none;
  border-radius: var(--radius-sm);
  padding: 4px 12px;
  font-family: var(--font-sans);
  font-size: var(--text-sm);
  font-weight: 500;
  cursor: pointer;
  margin-right: 12px;
}
.file-name { font-size: var(--text-sm); color: var(--color-text-muted); }
</style>
```

- [ ] **Step 2: Verify in browser**

1. Open http://localhost:5173/trainer-plans → empty state
2. Click "上传计划" → modal with title, date range, file picker
3. Upload a .md file → plan appears with "已解析" badge
4. Click the plan row → expands to show parsed markdown content
5. Upload a .pdf → if MinerU key configured, parses; otherwise shows error note
6. Delete → confirmation dialog, then removed

- [ ] **Step 3: Commit**

```bash
cd /Users/jarrett/Desktop/SpringPilot
git add frontend/src/views/TrainerPlans.vue
git commit -m "feat(frontend): implement Trainer Plans page with upload, parse, and expandable content view"
```

---

## Self-Review Checklist

**1. Spec coverage:**

| Spec requirement | Task |
|---|---|
| LLM multi-model config (4 providers, per-scenario) | Task 13 (Settings) |
| API Key management per provider | Task 13 |
| MinerU API key | Task 13 |
| User profile (height, weight target, TDEE) | Task 13 |
| Data export (JSON) | Task 13 |
| Dashboard: job overview stats | Task 14 |
| Dashboard: fitness overview stats | Task 14 |
| Dashboard: AI daily advice | Task 14 |
| Dashboard: weight chart + calorie chart | Task 14 |
| Application list with status filter | Task 15 |
| Application status timeline | Task 15 |
| AI interview question generation | Task 15 |
| Study task CRUD with tags + completion | Task 16 |
| JD analysis (paste + AI extract) | Task 17 |
| Mock interview (chat-style AI) | Task 18 |
| Weight tracking + chart | Task 19 |
| Diet log + AI calorie estimate | Task 19 |
| Training log + heatmap | Task 19 |
| Trainer plan upload + parse | Task 20 |

**2. Placeholder scan:** No TBD / TODO / "implement later" found.

**3. Type consistency:** All API function signatures in Task 12 (`applicationsApi.list()`, `aiApi.analyzeJd()`, etc.) match their consumption in Tasks 13–20. All component prop names match across producer/consumer boundaries.
