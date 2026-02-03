<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchOperadora, fetchOperadoraDespesas } from '../services/api'
import type { Operadora, Despesa } from '../types'

const route = useRoute()
const router = useRouter()

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
  loading.value = true
  error.value = null

  const cnpj = route.params.cnpj as string

  try {
    operadora.value = await fetchOperadora(cnpj)
    await loadDespesas()
  } catch (e) {
    error.value = 'Operadora não encontrada.'
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function loadDespesas(): Promise<void> {
  const cnpj = route.params.cnpj as string

  try {
    const response = await fetchOperadoraDespesas(cnpj, page.value, limit.value)
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

function goBack(): void {
  router.push('/')
}

onMounted(loadOperadora)
</script>

<template>
  <div class="w-full">
    <button
      class="px-4 py-2 border border-gray-300 rounded hover:bg-gray-100 mb-6"
      @click="goBack"
    >
      &larr; Voltar
    </button>

    <div v-if="loading" class="p-8 text-center text-gray-600">Carregando...</div>

    <div v-else-if="error" class="p-8 text-center text-red-600">{{ error }}</div>

    <template v-else-if="operadora">
      <div class="flex items-center gap-4 mb-6">
        <h1 class="text-2xl font-bold text-slate-900">{{ operadora.razao_social }}</h1>
        <span class="bg-slate-900 text-white px-3 py-1 rounded font-bold text-sm">{{ operadora.uf }}</span>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div class="bg-white p-5 rounded-lg shadow-sm">
          <h3 class="text-sm text-gray-500 mb-2">CNPJ</h3>
          <p class="text-lg text-slate-900">{{ formatCNPJ(operadora.cnpj) }}</p>
        </div>
        <div class="bg-white p-5 rounded-lg shadow-sm">
          <h3 class="text-sm text-gray-500 mb-2">Registro ANS</h3>
          <p class="text-lg text-slate-900">{{ operadora.registro_ans || 'Não informado' }}</p>
        </div>
        <div class="bg-white p-5 rounded-lg shadow-sm">
          <h3 class="text-sm text-gray-500 mb-2">Modalidade</h3>
          <p class="text-lg text-slate-900">{{ operadora.modalidade || 'Não informada' }}</p>
        </div>
      </div>

      <section class="bg-white p-6 rounded-lg shadow-sm">
        <h2 class="text-xl font-semibold mb-4">Histórico de Despesas</h2>

        <div v-if="despesas.length === 0" class="p-8 text-center text-gray-600">
          Nenhuma despesa registrada.
        </div>

        <template v-else>
          <table class="w-full">
            <thead>
              <tr>
                <th class="px-4 py-3 text-left bg-gray-100 font-semibold border-b border-gray-200">Período</th>
                <th class="px-4 py-3 text-left bg-gray-100 font-semibold border-b border-gray-200">Valor</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(d, index) in despesas" :key="index" class="hover:bg-gray-50">
                <td class="px-4 py-3 border-b border-gray-100">{{ formatTrimestre(d.trimestre, d.ano) }}</td>
                <td class="px-4 py-3 border-b border-gray-100">{{ formatCurrency(d.valor_despesa) }}</td>
              </tr>
            </tbody>
          </table>

          <div class="flex justify-center items-center gap-4 mt-4">
            <button
              :disabled="page === 1"
              class="px-4 py-2 border border-gray-300 bg-white rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              @click="goToPage(page - 1)"
            >
              Anterior
            </button>
            <span class="text-gray-600">Página {{ page }} de {{ totalPages }}</span>
            <button
              :disabled="page === totalPages"
              class="px-4 py-2 border border-gray-300 bg-white rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              @click="goToPage(page + 1)"
            >
              Próxima
            </button>
          </div>
        </template>
      </section>
    </template>
  </div>
</template>
