<script setup>
import { RouterView } from 'vue-router'
</script>

<template>
  <div class="app-container">
    <header class="app-header">
      <div class="logo text-gold">A股交易系统 V1.0</div>
      <div class="nav-links">
        <router-link to="/">行情终端</router-link>
        <router-link to="/strategy">策略选股</router-link>
        <router-link to="/data">数据维护</router-link>
      </div>
    </header>
    <main class="app-main">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100vw;
  background-color: #0b0e11;
}

.app-header {
  display: flex;
  align-items: center;
  padding: 0 20px;
  height: 50px;
  background-color: #1e222d;
  border-bottom: 1px solid #2b3139;
}

.logo {
  font-size: 1.2rem;
  font-weight: bold;
  margin-right: 40px;
}

.nav-links a {
  color: #d1d4dc;
  text-decoration: none;
  margin-right: 20px;
  font-size: 0.95rem;
  padding: 10px 0;
}

.nav-links a:hover,
.nav-links a.router-link-active {
  color: #ffcc00;
  border-bottom: 2px solid #ffcc00;
}

.app-main {
  flex: 1;
  display: flex;
  overflow: hidden;
}
</style>
