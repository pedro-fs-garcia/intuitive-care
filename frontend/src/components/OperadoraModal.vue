<script setup lang="ts">
import { ref, watch } from 'vue'
import { fetchOperadora, fetchOperadoraDespesas } from '../services/api'
import type { Operadora, Despesa } from '../types'

const props = defineProps<{
  cnpj: string | null
}>()

const emit = defineEmits<{
  close: []
}>()

const operadora = ref<Operadora | null>(null)
const despesas = ref<Despesa[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

const page = ref(1)
const limit = ref(10)
const total = ref(0)
const totalPages = ref(0)

function formatCNPJ(cnpj: string): string {
  if (cnpj.length !== 14) return cnpj
  return cnpj.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, '$1.$2.$3/$4-$5')
}

function formatCurrency(value: number): string {
  return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

function formatTrimestre(trimestre: number, ano: number): string {
  return `${trimestre}T/${ano}`
}

async function loadOperadora(): Promise<void> {
  if (!props.cnpj) return

  loading.value = true
  error.value = null
  page.value = 1

  try {
    operadora.value = await fetchOperadora(props.cnpj)
    await loadDespesas()
  } catch (e) {
    error.value = 'Operadora não encontrada.'
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function loadDespesas(): Promise<void> {
  if (!props.cnpj) return

  try {
    const response = await fetchOperadoraDespesas(props.cnpj, page.value, limit.value)
    despesas.value = response.data
    total.value = response.total
    totalPages.value = response.total_pages
  } catch (e) {
    console.error('Erro ao carregar despesas:', e)
  }
}

function goToPage(newPage: number): void {
  if (newPage >= 1 && newPage <= totalPages.value) {
    page.value = newPage
    loadDespesas()
  }
}

function closeModal(): void {
  emit('close')
}

function handleBackdropClick(event: MouseEvent): void {
  if (event.target === event.currentTarget) {
    closeModal()
  }
}

watch(() => props.cnpj, (newCnpj) => {
  if (newCnpj) {
    loadOperadora()
  }
}, { immediate: true })
</script>

<template>
  <Teleport to="body">
    <div
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
      @click="handleBackdropClick"
    >
      <div class="bg-white rounded-lg shadow-xl w-full max-w-3xl max-h-[90vh] overflow-hidden flex flex-col">
        <!-- Header -->
        <div class="flex items-center justify-between p-4 border-b border-gray-200">
          <h2 class="text-xl font-bold text-slate-900">Detalhes da Operadora</h2>
          <button
            class="p-2 hover:bg-gray-100 rounded-full transition-colors"
            @click="closeModal"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Content -->
        <div class="flex-1 overflow-y-auto p-6">
          <div v-if="loading" class="p-8 text-center text-gray-600">Carregando...</div>

          <div v-else-if="error" class="p-8 text-center text-red-600">{{ error }}</div>

          <template v-else-if="operadora">
            <div class="flex items-center gap-3 mb-6">
              <h3 class="text-lg font-semibold text-slate-900">{{ operadora.razao_social }}</h3>
              <span class="bg-slate-900 text-white px-2 py-0.5 rounded text-sm font-medium">{{ operadora.uf }}</span>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div class="bg-gray-50 p-4 rounded-lg">
                <h4 class="text-xs text-gray-500 mb-1">CNPJ</h4>
                <p class="text-sm font-medium text-slate-900">{{ formatCNPJ(operadora.cnpj) }}</p>
              </div>
              <div class="bg-gray-50 p-4 rounded-lg">
                <h4 class="text-xs text-gray-500 mb-1">Registro ANS</h4>
                <p class="text-sm font-medium text-slate-900">{{ operadora.registro_ans || 'Não informado' }}</p>
              </div>
              <div class="bg-gray-50 p-4 rounded-lg">
                <h4 class="text-xs text-gray-500 mb-1">Modalidade</h4>
                <p class="text-sm font-medium text-slate-900">{{ operadora.modalidade || 'Não informada' }}</p>
              </div>
            </div>

            <div>
              <h4 class="text-md font-semibold mb-3">Histórico de Despesas</h4>

              <div v-if="despesas.length === 0" class="p-6 text-center text-gray-500 bg-gray-50 rounded-lg">
                Nenhuma despesa registrada.
              </div>

              <template v-else>
                <table class="w-full text-sm">
                  <thead>
                    <tr>
                      <th class="px-3 py-2 text-left bg-gray-100 font-semibold border-b border-gray-200">Período</th>
                      <th class="px-3 py-2 text-right bg-gray-100 font-semibold border-b border-gray-200">Valor do Trimestre</th>
                      <th class="px-3 py-2 text-right bg-gray-100 font-semibold border-b border-gray-200">Acumulado (YTD)</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(d, index) in despesas" :key="index" class="hover:bg-gray-50">
                      <td class="px-3 py-2 border-b border-gray-100">{{ formatTrimestre(d.trimestre, d.ano) }}</td>
                      <td class="px-3 py-2 border-b border-gray-100 text-right font-medium text-emerald-700">{{ formatCurrency(d.valor_despesa) }}</td>
                      <td class="px-3 py-2 border-b border-gray-100 text-right text-gray-500">{{ d.valor_ytd ? formatCurrency(d.valor_ytd) : '-' }}</td>
                    </tr>
                  </tbody>
                </table>
                <p class="text-xs text-gray-500 mt-2">
                  <strong>Valor do Trimestre:</strong> despesa isolada do período. 
                  <strong>Acumulado (YTD):</strong> soma das despesas desde o início do ano.
                </p>

                <div v-if="totalPages > 1" class="flex justify-center items-center gap-3 mt-4">
                  <button
                    :disabled="page === 1"
                    class="px-3 py-1 text-sm border border-gray-300 bg-white rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    @click="goToPage(page - 1)"
                  >
                    Anterior
                  </button>
                  <span class="text-sm text-gray-600">{{ page }} / {{ totalPages }}</span>
                  <button
                    :disabled="page === totalPages"
                    class="px-3 py-1 text-sm border border-gray-300 bg-white rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    @click="goToPage(page + 1)"
                  >
                    Próxima
                  </button>
                </div>
              </template>
            </div>
          </template>
        </div>
      </div>
    </div>
  </Teleport>
</template>
