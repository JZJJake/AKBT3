import { createRouter, createWebHistory } from 'vue-router'
import TerminalView from '../views/TerminalView.vue'
import DataView from '../views/DataView.vue'
import StrategyView from '../views/StrategyView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'terminal',
      component: TerminalView
    },
    {
      path: '/data',
      name: 'data',
      component: DataView
    },
    {
      path: '/strategy',
      name: 'strategy',
      component: StrategyView
    }
  ]
})

export default router
