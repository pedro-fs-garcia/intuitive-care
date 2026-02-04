<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { fetchEstatisticasComplementares } from '../services/api'
import type { EstatisticasComplementares } from '../types'

const emit = defineEmits<{
  selectOperadora: [cnpj: string]
}>()

const estatisticas = ref<EstatisticasComplementares | null>(null)
const loading = ref(false)

let retryTimeout: ReturnType<typeof setTimeout> | null = null

function formatCurrency(value: number): string {
  return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

function formatPercent(value: number): string {
  const sign = value >= 0 ? '+' : ''
  return `${sign}${value.toFixed(2)}%`
}

async function loadEstatisticas(): Promise<void> {
  loading.value = true
  if (retryTimeout) {
    clearTimeout(retryTimeout)
    retryTimeout = null
  }

  try {
    estatisticas.value = await fetchEstatisticasComplementares()
    loading.value = false
  } catch (e) {
    console.error(e)
    retryTimeout = setTimeout(loadEstatisticas, 500)
  }
}

onMounted(loadEstatisticas)
</script>

<template>
  <div class="w-full">
    <div v-if="loading" class="p-8 flex flex-col items-center justify-center gap-3">
      <svg class="animate-spin h-8 w-8 text-slate-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <span class="text-gray-600">Carregando estatísticas complementares...</span>
    </div>

    <template v-else-if="estatisticas">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        <!-- Query 1: Top 5 Crescimento -->
        <div class="bg-white p-6 rounded-lg shadow-sm">
          <h3 class="text-lg font-semibold mb-1">Top 5 Maior Crescimento</h3>
          <p class="text-sm text-gray-500 mb-4">Operadoras com maior crescimento percentual de despesas entre o primeiro e último trimestre</p>
          
          <div v-if="estatisticas.top_5_crescimento.length === 0" class="text-center text-gray-500 py-4">
            Dados insuficientes para calcular crescimento
          </div>
          
          <table v-else class="w-full text-sm">
            <thead>
              <tr>
                <th class="px-2 py-2 text-left bg-gray-100 border-b border-gray-200">Operadora</th>
                <th class="px-2 py-2 text-right bg-gray-100 border-b border-gray-200">Inicial</th>
                <th class="px-2 py-2 text-right bg-gray-100 border-b border-gray-200">Final</th>
                <th class="px-2 py-2 text-right bg-gray-100 border-b border-gray-200">Crescimento</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="op in estatisticas.top_5_crescimento"
                :key="op.cnpj"
                class="hover:bg-gray-50 cursor-pointer"
                @click="emit('selectOperadora', op.cnpj)"
              >
                <td class="px-2 py-2 border-b border-gray-100 truncate max-w-[150px]" :title="op.razao_social">
                  {{ op.razao_social }}
                </td>
                <td class="px-2 py-2 border-b border-gray-100 text-right text-xs">
                  {{ formatCurrency(op.despesa_inicial) }}
                </td>
                <td class="px-2 py-2 border-b border-gray-100 text-right text-xs">
                  {{ formatCurrency(op.despesa_final) }}
                </td>
                <td class="px-2 py-2 border-b border-gray-100 text-right font-semibold"
                    :class="op.crescimento_percentual >= 0 ? 'text-red-600' : 'text-green-600'">
                  {{ formatPercent(op.crescimento_percentual) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Query 2: Distribuição por UF -->
        <div class="bg-white p-6 rounded-lg shadow-sm">
          <h3 class="text-lg font-semibold mb-1">Top 5 Estados por Despesas</h3>
          <p class="text-sm text-gray-500 mb-4">Estados com maiores despesas totais e média por operadora</p>
          
          <table class="w-full text-sm">
            <thead>
              <tr>
                <th class="px-2 py-2 text-left bg-gray-100 border-b border-gray-200">UF</th>
                <th class="px-2 py-2 text-right bg-gray-100 border-b border-gray-200">Operadoras</th>
                <th class="px-2 py-2 text-right bg-gray-100 border-b border-gray-200">Total</th>
                <th class="px-2 py-2 text-right bg-gray-100 border-b border-gray-200">Média/Operadora</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="uf in estatisticas.top_5_uf" :key="uf.uf" class="hover:bg-gray-50">
                <td class="px-2 py-2 border-b border-gray-100">
                  <span class="bg-slate-900 text-white px-2 py-0.5 rounded text-xs font-medium">{{ uf.uf }}</span>
                </td>
                <td class="px-2 py-2 border-b border-gray-100 text-right">
                  {{ uf.qtd_operadoras }}
                </td>
                <td class="px-2 py-2 border-b border-gray-100 text-right text-xs">
                  {{ formatCurrency(uf.total_despesas) }}
                </td>
                <td class="px-2 py-2 border-b border-gray-100 text-right text-xs">
                  {{ formatCurrency(uf.media_por_operadora) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Query 3: Operadoras acima da média -->
        <div class="bg-white p-6 rounded-lg shadow-sm lg:col-span-2">
          <h3 class="text-lg font-semibold mb-1">Operadoras Consistentemente Acima da Média</h3>
          <p class="text-sm text-gray-500 mb-4">{{ estatisticas.operadoras_acima_media.criterio }}</p>
          
          <div class="flex flex-col md:flex-row gap-6">
            <div class="flex-1 bg-slate-50 p-6 rounded-lg text-center">
              <p class="text-4xl font-bold text-slate-900">{{ estatisticas.operadoras_acima_media.total }}</p>
              <p class="text-sm text-gray-600 mt-2">operadoras</p>
            </div>
            <div class="flex-1 bg-gray-50 p-6 rounded-lg">
              <p class="text-sm text-gray-500 mb-1">Média geral de referência</p>
              <p class="text-2xl font-bold text-slate-900">{{ formatCurrency(estatisticas.operadoras_acima_media.media_geral_referencia) }}</p>
              <p class="text-xs text-gray-400 mt-2">Valor médio de despesa por registro trimestral considerando todas as operadoras</p>
            </div>
          </div>
        </div>

      </div>
    </template>
  </div>
</template>
