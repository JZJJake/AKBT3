<script setup>
import { ref } from 'vue';
import axios from 'axios';

const message = ref('');
const loadingState = ref({ basics: false, daily: false, fundamentals: false });

const updateData = async (type) => {
  loadingState.value[type] = true;
  message.value = `正在启动 ${type} 数据更新...`;
  try {
    const res = await axios.post(`/api/update/${type}`);
    message.value = res.data.message || '更新任务已在后台启动。';
  } catch (err) {
    message.value = `更新失败: ${err.message}`;
  } finally {
    loadingState.value[type] = false;
  }
};
</script>

<template>
  <div class="data-view">
    <div class="header">
      <h2>数据维护中心</h2>
      <p class="subtitle text-gold">从 Baostock 和 Akshare 获取最新全量数据</p>
    </div>

    <div class="actions">
      <div class="card">
        <h3>1. 基础信息维护</h3>
        <p>下载或更新所有A股的基本信息（代码、名称等）。</p>
        <button @click="updateData('basics')" :disabled="loadingState.basics" class="btn btn-primary">
          {{ loadingState.basics ? '更新中...' : '更新基础信息' }}
        </button>
      </div>

      <div class="card">
        <h3>2. 历史行情下载</h3>
        <p>下载日线数据并计算 MACD、KDJ 等技术指标（耗时较长）。</p>
        <button @click="updateData('daily')" :disabled="loadingState.daily" class="btn btn-warning">
          {{ loadingState.daily ? '更新中...' : '更新历史行情' }}
        </button>
      </div>

      <div class="card">
        <h3>3. 基本面数据下载</h3>
        <p>获取最新流通市值等基本面数据。</p>
        <button @click="updateData('fundamentals')" :disabled="loadingState.fundamentals" class="btn btn-info">
          {{ loadingState.fundamentals ? '更新中...' : '更新基本面数据' }}
        </button>
      </div>
    </div>

    <div v-if="message" class="message-box">
      <strong>系统提示:</strong> {{ message }}
    </div>
  </div>
</template>

<style scoped>
.data-view { padding: 30px; width: 100%; background-color: #0b0e11; color: #d1d4dc; overflow-y: auto; }
.header { margin-bottom: 30px; border-bottom: 1px solid #2b3139; padding-bottom: 20px; }
.header h2 { margin: 0 0 10px 0; color: #ffcc00; }
.subtitle { color: #8891aa; margin: 0; }
.actions { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }
.card { background-color: #1e222d; border: 1px solid #2b3139; border-radius: 8px; padding: 20px; display: flex; flex-direction: column; }
.card h3 { margin-top: 0; color: #ffcc00; }
.card p { color: #8891aa; flex: 1; }
.btn { padding: 10px 20px; border: none; border-radius: 4px; font-weight: bold; cursor: pointer; transition: opacity 0.2s; margin-top: 15px; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn:hover:not(:disabled) { opacity: 0.8; }
.btn-primary { background-color: #2962FF; color: white; }
.btn-warning { background-color: #FF6D00; color: white; }
.btn-info { background-color: #089981; color: white; }
.message-box { background-color: #1e222d; border-left: 4px solid #ffcc00; padding: 15px; border-radius: 4px; }
</style>
