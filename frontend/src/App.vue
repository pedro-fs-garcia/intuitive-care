<script setup lang="ts">
import { RouterView, RouterLink } from 'vue-router'
</script>

<template>
  <div class="min-h-screen flex flex-col bg-gray-100">
    <header class="bg-slate-900 px-8 py-4">
      <nav class="max-w-6xl mx-auto">
        <RouterLink to="/" class="text-white text-2xl font-bold no-underline hover:no-underline">
          IntuitiveCare
        </RouterLink>
      </nav>
    </header>
    <main class="flex-1 p-8 max-w-6xl mx-auto w-full">
      <RouterView />
    </main>
  </div>
</template>
