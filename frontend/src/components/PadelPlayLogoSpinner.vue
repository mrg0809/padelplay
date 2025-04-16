<template>
    <div class="my-logo-spinner column items-center justify-center">
      <q-img
        :src="logoUrl"
        alt="Cargando..."
        style="width: 200px; height: 200px; margin-bottom: 15px;"
        fit="contain"
      />
  
      <q-spinner-facebook
        :color="spinnerColor"
        :size="spinnerSize"
      />
  
      <div v-if="loadingText" class="q-mt-md text-center">
        {{ loadingText }}
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue';
  
  // Define las props que tu componente puede recibir
  const props = defineProps({
    logoUrl: {
      type: String,
      default: '/src/assets/padelplay.png' // Cambia esto a la ruta real de tu logo
                                        // Puede ser una ruta en /public o importada
    },
    spinnerColor: {
      type: String,
      default: 'yellow' // Usa un color de tu tema Quasar o un color CSS
    },
    spinnerSize: {
      type: String,
      default: '120' // Ajusta el tamaño del spinner estándar
    },
    loadingText: {
      type: String,
      default: 'Cargando, por favor espera...' // Texto opcional
    },
  })
  
  // Si necesitas importar el logo directamente (asegúrate que tu bundler lo soporte)
  // import logoPath from '@/assets/logo.png';
  // const logoUrl = ref(logoPath);
  // O si está en la carpeta /public
  const logoUrl = ref(props.logoUrl);
  
  </script>
  
  <style scoped>
  .my-logo-spinner {
    /* Estilos adicionales si son necesarios */
    min-height: 150px; /* Para asegurar espacio vertical */
  }
  </style>