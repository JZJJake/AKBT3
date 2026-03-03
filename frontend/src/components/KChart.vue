<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import { createChart, CrosshairMode, LineStyle } from 'lightweight-charts';
import axios from 'axios';

const props = defineProps({
  code: { type: String, required: true },
  name: { type: String, default: '' },
  period: { type: String, default: 'daily' }
});

const chartContainer = ref(null);
let chart = null;
let candleSeries = null;
let volumeSeries = null;
let macdSeries = null;
let signalSeries = null;
let histSeries = null;
let kSeries = null;
let dSeries = null;
let jSeries = null;

const resizeObserver = new ResizeObserver((entries) => {
  if (chartContainer.value && chart) {
    const { width, height } = entries[0].contentRect;
    chart.applyOptions({ width, height });
  }
});

onMounted(() => {
  initChart();
  resizeObserver.observe(chartContainer.value);
  if (props.code) {
    fetchData();
  }
});

watch(() => props.period, () => {
  if (props.code && props.period) {
    fetchData();
  }
});

watch(() => chartContainer.value, () => {
  if (chartContainer.value && props.code) {
    if (!chart) initChart();
    fetchData();
  }
});

onUnmounted(() => {
  resizeObserver.disconnect();
  if (chart) {
    chart.remove();
  }
});

watch(() => props.code, () => {
  if (props.code) {
    fetchData();
  }
});

const initChart = () => {
  if (!chartContainer.value) return;

  const chartOptions = {
    layout: {
      background: { type: 'solid', color: '#0b0e11' },
      textColor: '#8891aa',
    },
    width: chartContainer.value.clientWidth || 800,
    height: chartContainer.value.clientHeight || 500,
    grid: {
      vertLines: { color: '#1f2933', style: LineStyle.Dotted },
      horzLines: { color: '#1f2933', style: LineStyle.Dotted },
    },
    crosshair: {
      mode: CrosshairMode.Normal,
      vertLine: { width: 1, color: '#758696', style: LineStyle.Dashed, labelBackgroundColor: '#1f2933' },
      horzLine: { width: 1, color: '#758696', style: LineStyle.Dashed, labelBackgroundColor: '#1f2933' },
    },
    rightPriceScale: { borderColor: '#2b3139' },
    timeScale: { borderColor: '#2b3139', timeVisible: true, secondsVisible: false },
    watermark: { color: 'rgba(255, 204, 0, 0.05)', visible: true, text: 'A-Share Terminal', fontSize: 48, horzAlign: 'center', vertAlign: 'center' },
  };

  chart = createChart(chartContainer.value, chartOptions);

  candleSeries = chart.addCandlestickSeries({
    priceScaleId: 'right',
    upColor: '#f23645', downColor: '#089981', borderDownColor: '#089981', borderUpColor: '#f23645', wickDownColor: '#089981', wickUpColor: '#f23645',
  });

  volumeSeries = chart.addHistogramSeries({
    priceFormat: { type: 'volume' }, priceScaleId: '', scaleMargins: { top: 0.8, bottom: 0 },
  });

  macdSeries = chart.addLineSeries({ color: '#2962FF', lineWidth: 1, priceScaleId: 'macd' });
  signalSeries = chart.addLineSeries({ color: '#FF6D00', lineWidth: 1, priceScaleId: 'macd' });
  histSeries = chart.addHistogramSeries({ priceScaleId: 'macd' });

  kSeries = chart.addLineSeries({ color: '#ffcc00', lineWidth: 1, priceScaleId: 'kdj' });
  dSeries = chart.addLineSeries({ color: '#00ffff', lineWidth: 1, priceScaleId: 'kdj' });
  jSeries = chart.addLineSeries({ color: '#ff00ff', lineWidth: 1, priceScaleId: 'kdj' });

  chart.priceScale('right').applyOptions({ scaleMargins: { top: 0.1, bottom: 0.5 } });
  chart.priceScale('macd').applyOptions({ scaleMargins: { top: 0.55, bottom: 0.25 } });
  chart.priceScale('kdj').applyOptions({ scaleMargins: { top: 0.8, bottom: 0.05 } });
};

const fetchData = async () => {
  try {
    const res = await axios.get(`/api/${props.period}/${props.code}`);
    const data = res.data;

    if (!data || data.length === 0) {
       candleSeries.setData([]);
       return;
    }

    const cData = [];
    const vData = [];
    const mData = [];
    const sData = [];
    const hData = [];
    const kData = [];
    const dData = [];
    const jData = [];

    const sortedData = [...data].sort((a, b) => new Date(a.date) - new Date(b.date));

    const uniqueData = [];
    const seenTimes = new Set();
    sortedData.forEach(item => {
       if (!seenTimes.has(item.date)) {
           seenTimes.add(item.date);
           uniqueData.push(item);
       }
    });

    uniqueData.forEach(item => {
      const time = item.date;
      cData.push({ time, open: item.open || 0, high: item.high || 0, low: item.low || 0, close: item.close || 0 });
      const vColor = (item.close || 0) >= (item.open || 0) ? 'rgba(242, 54, 69, 0.5)' : 'rgba(8, 153, 129, 0.5)';
      vData.push({ time, value: item.volume || 0, color: vColor });
      if (item.macd !== null && item.macd !== undefined) mData.push({ time, value: item.macd });
      if (item.macd_signal !== null && item.macd_signal !== undefined) sData.push({ time, value: item.macd_signal });
      if (item.macd_hist !== null && item.macd_hist !== undefined) {
          const hColor = item.macd_hist >= 0 ? 'rgba(242, 54, 69, 0.7)' : 'rgba(8, 153, 129, 0.7)';
          hData.push({ time, value: item.macd_hist, color: hColor });
      }
      if (item.kdj_k !== null && item.kdj_k !== undefined) kData.push({ time, value: item.kdj_k });
      if (item.kdj_d !== null && item.kdj_d !== undefined) dData.push({ time, value: item.kdj_d });
      if (item.kdj_j !== null && item.kdj_j !== undefined) jData.push({ time, value: item.kdj_j });
    });

    cData.sort((a,b) => new Date(a.time) - new Date(b.time));
    vData.sort((a,b) => new Date(a.time) - new Date(b.time));
    mData.sort((a,b) => new Date(a.time) - new Date(b.time));
    sData.sort((a,b) => new Date(a.time) - new Date(b.time));
    hData.sort((a,b) => new Date(a.time) - new Date(b.time));
    kData.sort((a,b) => new Date(a.time) - new Date(b.time));
    dData.sort((a,b) => new Date(a.time) - new Date(b.time));
    jData.sort((a,b) => new Date(a.time) - new Date(b.time));

    // Remove duplicates properly after sorting to avoid errors
    const removeDups = (arr) => arr.filter((v,i,a)=>a.findIndex(t=>(t.time === v.time))===i);

    const cleanC = removeDups(cData);
    const cleanV = removeDups(vData);
    const cleanM = removeDups(mData);
    const cleanS = removeDups(sData);
    const cleanH = removeDups(hData);
    const cleanK = removeDups(kData);
    const cleanD = removeDups(dData);
    const cleanJ = removeDups(jData);

    candleSeries.setData(cleanC);
    volumeSeries.setData(cleanV);
    macdSeries.setData(cleanM);
    signalSeries.setData(cleanS);
    histSeries.setData(cleanH);
    kSeries.setData(cleanK);
    dSeries.setData(cleanD);
    jSeries.setData(cleanJ);

    chart.timeScale().fitContent();

  } catch (err) {
    console.error('Failed to fetch chart data:', err);
  }
};
</script>

<template>
  <div class="chart-wrapper">
     <div class="chart-header">
       <span class="stock-title text-gold">{{ props.name || 'Select a stock' }} ({{ props.code }})</span>
       <span class="period-badge">{{ props.period.toUpperCase() }}</span>
     </div>
     <div class="chart-container" ref="chartContainer"></div>
  </div>
</template>

<style scoped>
.chart-wrapper {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  position: relative;
  border-left: 1px solid #1e222d;
}
.chart-header {
  position: absolute;
  top: 10px;
  left: 15px;
  z-index: 10;
  pointer-events: none;
  display: flex;
  align-items: center;
  gap: 10px;
}
.stock-title { font-size: 1.1rem; font-weight: bold; }
.period-badge { background-color: #2b3139; padding: 2px 6px; border-radius: 4px; font-size: 0.8rem; color: #d1d4dc; }
.chart-container { flex: 1; width: 100%; height: 100%; }
</style>
