<template>
    <div> <OrderComponent
        v-if="summaryData"
        v-bind="summaryData"
      />
      <div v-else class="fullscreen bg-dark text-white text-center q-pa-md flex flex-center">
         <div>
           <q-spinner-cube color="orange" size="xl" />
           <div class="q-mt-md text-h6">Cargando resumen...</div>
           <q-btn class="q-mt-xl" color="white" text-color="black" unelevated @click="$router.go(-1)" label="Volver" no-caps />
         </div>
      </div>
    </div>
  </template>
  
  <script>
  import { defineComponent, onMounted, onUnmounted, computed, ref } from 'vue';
  import { useRouter } from 'vue-router';
  import { useSummaryStore } from 'src/stores/summaryStore'; // Importa el store
  import OrderComponent from 'src/components/OrderComponent.vue'; // Importa el componente genérico
  
  export default defineComponent({
    name: 'OrderSummary',
    components: {
      OrderComponent,
    },
    setup() {
      const summaryStore = useSummaryStore();
      const router = useRouter();
  
      // Usamos computed para que sea reactivo si el store cambiara (aunque aquí no debería)
      // o simplemente acceder directamente: const summaryData = summaryStore.getSummaryDetails;
      const summaryData = computed(() => summaryStore.getSummaryDetails);
  
      onMounted(() => {
        // Verificar si hay datos al montar la página
        if (!summaryStore.hasActiveSummary) {
          console.warn('No hay datos de resumen en el store. Redirigiendo...');
          // Opcional: Mostrar un mensaje al usuario antes de redirigir
          // alert('No se encontraron detalles de la reserva. Por favor, inténtalo de nuevo.');
          // Redirigir a una página anterior o a la home
          router.replace({ name: 'HomePage' }); // Reemplaza 'HomePage' con tu ruta de inicio
        } else {
           console.log('ReservationSummaryPage mounted with data:', summaryData.value);
        }
      });
  
      onUnmounted(() => {
        // ¡MUY IMPORTANTE! Limpiar el store cuando el usuario sale de esta página
        summaryStore.clearSummaryDetails();
      });
  
      return {
        summaryData,
        // No necesitas retornar summaryStore si solo lo usas en setup
      };
    },
  });
  </script>