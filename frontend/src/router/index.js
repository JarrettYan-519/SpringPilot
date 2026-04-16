import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', component: () => import('@/views/Dashboard.vue'), name: 'dashboard' },
  { path: '/applications', component: () => import('@/views/Applications.vue'), name: 'applications' },
  { path: '/applications/:id', component: () => import('@/views/ApplicationDetail.vue'), name: 'application-detail' },
  { path: '/study-tasks', component: () => import('@/views/StudyTasks.vue'), name: 'study-tasks' },
  { path: '/mock-interview', component: () => import('@/views/MockInterview.vue'), name: 'mock-interview' },
  { path: '/jd-analysis', component: () => import('@/views/JDAnalysis.vue'), name: 'jd-analysis' },
  { path: '/fitness', component: () => import('@/views/FitnessOverview.vue'), name: 'fitness' },
  { path: '/trainer-plans', component: () => import('@/views/TrainerPlans.vue'), name: 'trainer-plans' },
  { path: '/settings', component: () => import('@/views/Settings.vue'), name: 'settings' },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
