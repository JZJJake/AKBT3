<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const router = useRouter();
const selectedStocks = ref([]);
const loading = ref(false);
const message = ref('');

const runStrategy = async () => {
  loading.value = true;
  message.value = '正在根据策略回测所有股票数据，请稍候...';
  try {
    const res = await axios.get('/api/strategy/run');
    if (res.data.status === 'success') {
      selectedStocks.value = res.data.data;
      message.value = `策略执行完成，共选出 ${selectedStocks.value.length} 只股票。`;
    } else {
      message.value = `策略执行失败: ${res.data.message}`;
    }
  } catch (err) {
    message.value = `策略执行失败: ${err.message}`;
  } finally {
    loading.value = false;
  }
};

const goToTerminal = (code) => {
  // Pass the selected stock code to the terminal (e.g., via query or store, here we'll just log and route for demo,
  // in a fully mature app we'd use Pinia or similar to share state).
  router.push({ name: 'terminal', query: { code } });
};
</script>

<template>
  <div class="strategy-view">
    <div class="header">
      <h2>策略选股中心</h2>
      <p class="subtitle text-gold">执行定制的量化选股策略：市值小于350亿，排除科创板，结合 M20均线多头 及 KDJ(J)底背离金叉</p>
    </div>

    <div class="actions">
      <button @click="runStrategy" :disabled="loading" class="btn btn-primary">
        {{ loading ? '策略正在执行中...' : '运行选股策略' }}
      </button>
    </div>

    <div v-if="message" class="message-box">
      <strong>系统提示:</strong> {{ message }}
    </div>

    <div v-if="selectedStocks.length > 0" class="results-container">
      <h3>策略选股结果 ({{ selectedStocks[0].date }})</h3>
      <table class="results-table">
        <thead>
          <tr>
            <th>股票代码</th>
            <th>股票名称</th>
            <th>最新收盘价</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="stock in selectedStocks" :key="stock.code">
            <td class="text-gold">{{ stock.code }}</td>
            <td>{{ stock.code_name }}</td>
            <td class="text-up">{{ stock.close.toFixed(2) }}</td>
            <td>
              <button @click="goToTerminal(stock.code)" class="btn-small">查看K线</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.strategy-view { padding: 30px; width: 100%; background-color: #0b0e11; color: #d1d4dc; overflow-y: auto; }
.header { margin-bottom: 30px; border-bottom: 1px solid #2b3139; padding-bottom: 20px; }
.header h2 { margin: 0 0 10px 0; color: #ffcc00; }
.subtitle { color: #8891aa; margin: 0; }
.actions { margin-bottom: 20px; }
.btn { padding: 10px 20px; border: none; border-radius: 4px; font-weight: bold; cursor: pointer; transition: opacity 0.2s; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn:hover:not(:disabled) { opacity: 0.8; }
.btn-primary { background-color: #2962FF; color: white; }
.btn-small { padding: 5px 10px; background-color: #089981; color: white; border: none; border-radius: 4px; cursor: pointer; }
.message-box { background-color: #1e222d; border-left: 4px solid #ffcc00; padding: 15px; border-radius: 4px; margin-bottom: 20px; }
.results-container { margin-top: 20px; background-color: #1e222d; padding: 20px; border-radius: 8px; border: 1px solid #2b3139; }
.results-container h3 { color: #ffcc00; margin-top: 0; }
.results-table { width: 100%; border-collapse: collapse; margin-top: 15px; }
.results-table th, .results-table td { padding: 12px; text-align: left; border-bottom: 1px solid #2b3139; }
.results-table th { color: #8891aa; font-weight: normal; }
.text-up { color: #f23645; }
</style>
