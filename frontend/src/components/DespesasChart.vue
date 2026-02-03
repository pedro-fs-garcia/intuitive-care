<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  type ChartData,
  type ChartOptions
} from 'chart.js'
import { fetchEstatisticas } from '../services/api'
import type { Estatisticas } from '../types'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const emit = defineEmits<{
  selectOperadora: [cnpj: string]
}>()

const estatisticas = ref<Estatisticas | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)

const chartData = computed<ChartData<'bar'>>(() => {
  if (!estatisticas.value) {
    return { labels: [], datasets: [] }
  }

  const data = estatisticas.value.despesas_por_uf
  return {
    labels: data.map(d => d.uf),
    datasets: [
      {
        label: 'Total de Despesas (R$)',
        data: data.map(d => d.total),
        backgroundColor: '#1e293b'
      }
    ]
  }
})

const chartOptions: ChartOptions<'bar'> = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'top' },
    title: { display: true, text: 'Distribuição de Despesas por UF' }
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        callback: (value) => 'R$ ' + Number(value).toLocaleString('pt-BR')
      }
    }
  }
}

function formatCurrency(value: number): string {
  return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

async function loadEstatisticas(): Promise<void> {
  loading.value = true
  error.value = null

  try {
    estatisticas.value = await fetchEstatisticas()
  } catch (e) {
    error.value = 'Erro ao carregar estatísticas.'
    console.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(loadEstatisticas)
</script>

<template>
  <div class="w-full">
    <div v-if="loading" class="p-8 text-center text-gray-600">Carregando estatísticas...</div>

    <div v-else-if="error" class="p-8 text-center text-red-600">{{ error }}</div>

    <template v-else-if="estatisticas">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div class="bg-white p-6 rounded-lg shadow-sm">
          <h3 class="text-sm text-gray-500 mb-1">Total de Despesas</h3>
          <p class="text-2xl font-bold text-slate-900">{{ formatCurrency(estatisticas.resumo.total_despesas) }}</p>
          <p class="text-xs text-gray-400 mt-2">Soma de todas as despesas com eventos/sinistros registradas nos últimos 3 trimestres</p>
        </div>
        <div class="bg-white p-6 rounded-lg shadow-sm">
          <h3 class="text-sm text-gray-500 mb-1">Média por Registro</h3>
          <p class="text-2xl font-bold text-slate-900">{{ formatCurrency(estatisticas.resumo.media_despesas) }}</p>
          <p class="text-xs text-gray-400 mt-2">Valor médio de despesa trimestral por operadora (últimos 3 trimestres)</p>
        </div>
      </div>

      <div class="bg-white p-6 rounded-lg shadow-sm h-96 mb-8">
        <Bar :data="chartData" :options="chartOptions" />
      </div>

      <div class="bg-white p-6 rounded-lg shadow-sm">
        <h3 class="text-lg font-semibold mb-1">Top 5 Operadoras</h3>
        <p class="text-sm text-gray-500 mb-4">Operadoras com maior volume de despesas com eventos/sinistros no período</p>
        <table class="w-full">
          <thead>
            <tr>
              <th class="px-3 py-2 text-left bg-gray-100 border-b border-gray-200">Razão Social</th>
              <th class="px-3 py-2 text-left bg-gray-100 border-b border-gray-200">UF</th>
              <th class="px-3 py-2 text-left bg-gray-100 border-b border-gray-200">Total Despesas</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="op in estatisticas.top_5_operadoras"
              :key="op.cnpj"
              class="hover:bg-gray-50 cursor-pointer"
              @click="emit('selectOperadora', op.cnpj)"
            >
              <td class="px-3 py-2 border-b border-gray-100">{{ op.razao_social }}</td>
              <td class="px-3 py-2 border-b border-gray-100">{{ op.uf }}</td>
              <td class="px-3 py-2 border-b border-gray-100">{{ formatCurrency(op.total_despesas) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>
