<template>
  <div class="app-layout">
    <nav class="sidebar">
      <div class="logo">SpringPilot</div>
      <ul>
        <li><RouterLink to="/">首页</RouterLink></li>
        <li class="section-label">求职</li>
        <li><RouterLink to="/applications">投递记录</RouterLink></li>
        <li><RouterLink to="/study-tasks">学习任务</RouterLink></li>
        <li><RouterLink to="/jd-analysis">JD 分析</RouterLink></li>
        <li><RouterLink to="/mock-interview">模拟面试</RouterLink></li>
        <li class="section-label">健身</li>
        <li><RouterLink to="/fitness">数据概览</RouterLink></li>
        <li><RouterLink to="/trainer-plans">训练计划</RouterLink></li>
        <li class="section-label">系统</li>
        <li><RouterLink to="/settings">设置</RouterLink></li>
      </ul>
    </nav>
    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f6fa; }
.app-layout { display: flex; min-height: 100vh; }
.sidebar { width: 200px; background: #1a1a2e; color: #eee; padding: 1rem; flex-shrink: 0; }
.sidebar .logo { font-size: 1.2rem; font-weight: bold; color: #fff; margin-bottom: 1.5rem; }
.sidebar ul { list-style: none; }
.sidebar li { margin: 0.25rem 0; }
.sidebar .section-label { font-size: 0.7rem; color: #888; text-transform: uppercase; margin-top: 1rem; margin-bottom: 0.25rem; }
.sidebar a { color: #ccc; text-decoration: none; display: block; padding: 0.4rem 0.5rem; border-radius: 4px; }
.sidebar a:hover, .sidebar a.router-link-active { background: #16213e; color: #fff; }
.main-content { flex: 1; padding: 2rem; overflow: auto; }
</style>
