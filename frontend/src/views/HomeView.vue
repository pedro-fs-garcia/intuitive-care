<script setup lang="ts">
import { ref, defineAsyncComponent } from 'vue'
import DespesasChart from '../components/DespesasChart.vue'

const OperadorasTable = defineAsyncComponent(() => import('../components/OperadorasTable.vue'))
const EstatisticasComplementares = defineAsyncComponent(() => import('../components/EstatisticasComplementares.vue'))
const OperadoraModal = defineAsyncComponent(() => import('../components/OperadoraModal.vue'))

const selectedCnpj = ref<string | null>(null)

function openModal(cnpj: string): void {
  selectedCnpj.value = cnpj
}

function closeModal(): void {
  selectedCnpj.value = null
}
</script>

<template>
  <div>
    <h1 class="text-3xl font-bold text-slate-900 mb-4">Despesas com Eventos / Sinistros</h1>
    <h3 class="text font-semibold text-gray-700 mb-8">Período considerado: últimos 3 trimestres disponibilizados pela ANS</h3>

    <section class="mb-12">
      <h2 class="text-xl font-semibold text-gray-700 mb-4">Estatísticas Gerais</h2>
      <DespesasChart @select-operadora="openModal" />
    </section>

    <section class="mb-12">
      <h2 class="text-xl font-semibold text-gray-700 mb-4">Análises Complementares</h2>
      <EstatisticasComplementares @select-operadora="openModal" />
    </section>

    <section class="mb-12">
      <h2 class="text-xl font-semibold text-gray-700 mb-4">Operadoras</h2>
      <OperadorasTable @select-operadora="openModal" />
    </section>

    <OperadoraModal
      v-if="selectedCnpj"
      :cnpj="selectedCnpj"
      @close="closeModal"
    />
  </div>
</template>
