<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { fetchOperadoras } from '../services/api'
import type { Operadora } from '../types'

const emit = defineEmits<{
  selectOperadora: [cnpj: string]
}>()

const operadoras = ref<Operadora[]>([])
const loading = ref(false)

const page = ref(1)
const limit = ref(10)
const total = ref(0)
const totalPages = ref(0)
const search = ref('')

let searchTimeout: ReturnType<typeof setTimeout> | null = null
let retryTimeout: ReturnType<typeof setTimeout> | null = null

async function loadOperadoras(): Promise<void> {
  loading.value = true
  if (retryTimeout) {
    clearTimeout(retryTimeout)
    retryTimeout = null
  }

  try {
    const response = await fetchOperadoras(page.value, limit.value, search.value)
    operadoras.value = response.data
    total.value = response.total
    totalPages.value = response.total_pages
    loading.value = false
  } catch (e) {
    console.error(e)
    retryTimeout = setTimeout(loadOperadoras, 500)
  }
}

function handleSearch(): void {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    page.value = 1
    loadOperadoras()
  }, 300)
}

function goToPage(newPage: number): void {
  if (newPage >= 1 && newPage <= totalPages.value) {
    page.value = newPage
    loadOperadoras()
  }
}

function viewDetails(cnpj: string): void {
  emit('selectOperadora', cnpj)
}

function formatCNPJ(cnpj: string): string {
  if (cnpj.length !== 14) return cnpj
  return cnpj.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, '$1.$2.$3/$4-$5')
}

watch(search, handleSearch)

onMounted(loadOperadoras)
</script>

<template>
  <div class="w-full">
    <div class="mb-4">
      <input
        v-model="search"
        type="text"
        placeholder="Buscar por razão social ou CNPJ..."
        class="w-full max-w-md px-4 py-3 border border-gray-300 rounded text-base focus:outline-none focus:ring-2 focus:ring-slate-500"
      />
    </div>

    <div v-if="loading" class="p-8 flex flex-col items-center justify-center gap-3">
      <svg class="animate-spin h-8 w-8 text-slate-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <span class="text-gray-600">Carregando...</span>
    </div>

    <div v-else-if="operadoras.length === 0" class="p-8 text-center text-gray-600">
      Nenhuma operadora encontrada.
    </div>

    <template v-else>
      <div class="overflow-x-auto">
        <table class="w-full bg-white shadow-sm rounded">
          <thead>
            <tr>
              <th class="px-4 py-3 text-left bg-gray-100 font-semibold border-b border-gray-200">CNPJ</th>
              <th class="px-4 py-3 text-left bg-gray-100 font-semibold border-b border-gray-200">Razão Social</th>
              <th class="px-4 py-3 text-left bg-gray-100 font-semibold border-b border-gray-200">Registro ANS</th>
              <th class="px-4 py-3 text-left bg-gray-100 font-semibold border-b border-gray-200">Modalidade</th>
              <th class="px-4 py-3 text-left bg-gray-100 font-semibold border-b border-gray-200">UF</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="op in operadoras"
              :key="op.cnpj"
              class="hover:bg-gray-50 cursor-pointer"
              @click="viewDetails(op.cnpj)"
            >
              <td class="px-4 py-3 border-b border-gray-100">{{ formatCNPJ(op.cnpj) }}</td>
              <td class="px-4 py-3 border-b border-gray-100">{{ op.razao_social }}</td>
              <td class="px-4 py-3 border-b border-gray-100">{{ op.registro_ans || '-' }}</td>
              <td class="px-4 py-3 border-b border-gray-100">{{ op.modalidade || '-' }}</td>
              <td class="px-4 py-3 border-b border-gray-100">{{ op.uf }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="flex justify-center items-center gap-4 mt-4 p-4">
        <button
          :disabled="page === 1"
          class="px-4 py-2 border border-gray-300 bg-white rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          @click="goToPage(page - 1)"
        >
          Anterior
        </button>
        <span class="text-gray-600">Página {{ page }} de {{ totalPages }} ({{ total }} registros)</span>
        <button
          :disabled="page === totalPages"
          class="px-4 py-2 border border-gray-300 bg-white rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          @click="goToPage(page + 1)"
        >
          Próxima
        </button>
      </div>
    </template>
  </div>
</template>
