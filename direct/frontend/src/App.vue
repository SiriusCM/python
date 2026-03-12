<template>
  <router-view />
</template>

<script setup>
import { onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const updateBodyClass = () => {
  if (route.path === '/index') {
    document.body.classList.add('app-body')
  } else {
    document.body.classList.remove('app-body')
  }
}

onMounted(updateBodyClass)
watch(() => route.path, updateBodyClass)
</script>