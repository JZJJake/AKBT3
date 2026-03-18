<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import KChart from '../components/KChart.vue';

const stocks = ref([]);
const selectedStock = ref(null);
const loading = ref(true);
const selectedPeriod = ref('daily');

import { useRoute } from 'vue-router';
const route = useRoute();

onMounted(async () => {
  try {
    const res = await axios.get('/api/stocks');
    stocks.value = res.data;

    // Check if we arrived from Strategy View with a specific stock code
    if (route.query.code) {
        const found = stocks.value.find(s => s.code === route.query.code);
        if (found) {
            selectedStock.value = found;
        } else {
            selectedStock.value = stocks.value[0];
        }
    } else if (stocks.value.length > 0) {
      selectedStock.value = stocks.value[0];
    }
  } catch (err) {
    console.error("Failed to fetch stock list:", err);
  } finally {
    loading.value = false;
  }
});

const selectStock = (stock) => {
  selectedStock.value = stock;
};

const setPeriod = (period) => {
  selectedPeriod.value = period;
};
</script>

<template>
  <div class="terminal-view">
    <aside class="sidebar">
      <div class="sidebar-header">自选股池</div>
      <div v-if="loading" class="loading">加载中...</div>
      <ul v-else class="stock-list">
        <li
          v-for="stock in stocks"
          :key="stock.code"
          :class="{ active: selectedStock?.code === stock.code }"
          @click="selectStock(stock)"
        >
          <span class="stock-name">{{ stock.code_name }}</span>
          <span class="stock-code text-gold">{{ stock.code }}</span>
        </li>
        <li v-if="stocks.length === 0" class="empty">暂无数据，请前往数据维护页面更新</li>
      </ul>
    </aside>

    <section class="chart-section">
      <div class="period-tabs">
        <button :class="{ active: selectedPeriod === 'daily' }" @click="setPeriod('daily')">日线</button>
        <button :class="{ active: selectedPeriod === 'weekly' }" @click="setPeriod('weekly')">周线</button>
        <button :class="{ active: selectedPeriod === 'monthly' }" @click="setPeriod('monthly')">月线</button>
      </div>
      <template v-if="selectedStock">
        <KChart
          :code="selectedStock.code"
          :name="selectedStock.code_name"
          :period="selectedPeriod"
        />
      </template>
      <div v-else class="no-selection">请选择股票</div>
    </section>

    <aside class="details-sidebar">
      <div class="details-header">个股资料</div>
      <div v-if="selectedStock" class="details-content">
        <div class="detail-row">
          <span class="label">代码:</span>
          <span class="value text-gold">{{ selectedStock.code }}</span>
        </div>
        <div class="detail-row">
          <span class="label">名称:</span>
          <span class="value">{{ selectedStock.code_name }}</span>
        </div>
        <div class="divider"></div>
        <div class="info-block">
          <p>基本面信息与回测功能将在后续版本接入。</p>
        </div>
      </div>
    </aside>
  </div>
</template>

<style scoped>
.terminal-view { display: flex; width: 100%; height: 100%; background-color: #0b0e11; }
.sidebar { width: 250px; background-color: #1e222d; display: flex; flex-direction: column; border-right: 1px solid #2b3139; }
.sidebar-header { padding: 15px; font-weight: bold; color: #ffcc00; border-bottom: 1px solid #2b3139; background-color: #131722; }
.loading, .empty { padding: 20px; text-align: center; color: #758696; }
.stock-list { list-style: none; padding: 0; margin: 0; overflow-y: auto; flex: 1; }
.stock-list li { padding: 10px 15px; display: flex; justify-content: space-between; cursor: pointer; border-bottom: 1px solid #2b3139; transition: background-color 0.2s; }
.stock-list li:hover { background-color: #2b3139; }
.stock-list li.active { background-color: #2b3139; border-left: 3px solid #ffcc00; }
.stock-name { color: #d1d4dc; }
.chart-section { flex: 1; position: relative; background-color: #0b0e11; display: flex; flex-direction: column; }
.period-tabs { display: flex; padding: 10px; background-color: #131722; border-bottom: 1px solid #1e222d; }
.period-tabs button { background: none; border: none; color: #8891aa; padding: 5px 15px; cursor: pointer; font-size: 1rem; }
.period-tabs button:hover { color: #d1d4dc; }
.period-tabs button.active { color: #ffcc00; font-weight: bold; border-bottom: 2px solid #ffcc00; }
.no-selection { display: flex; align-items: center; justify-content: center; height: 100%; color: #758696; font-size: 1.2rem; }
.details-sidebar { width: 280px; background-color: #1e222d; border-left: 1px solid #2b3139; display: flex; flex-direction: column; }
.details-header { padding: 15px; font-weight: bold; color: #ffcc00; border-bottom: 1px solid #2b3139; background-color: #131722; }
.details-content { padding: 15px; overflow-y: auto; }
.detail-row { display: flex; justify-content: space-between; margin-bottom: 10px; }
.label { color: #8891aa; }
.value { color: #d1d4dc; }
.divider { height: 1px; background-color: #2b3139; margin: 15px 0; }
.info-block { padding: 10px; background-color: #131722; border-radius: 4px; color: #8891aa; font-size: 0.85rem; line-height: 1.5; }
</style>
