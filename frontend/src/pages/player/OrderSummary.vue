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
  import { useSummaryStore } from 'src/stores/summaryStore'; 
  import OrderComponent from 'src/components/OrderComponent.vue'; 
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
        if (!summaryStore.hasActiveSummary) {
          console.warn('No hay datos de resumen en el store. Redirigiendo...');
          // Redirigir a una página anterior o a la home
          router.replace({ name: 'DashboardPlayer' }); 
        } else {
           console.log('ReservationSummaryPage mounted with data:', summaryData.value);
        }
      });
  
      onUnmounted(() => {
        summaryStore.clearSummaryDetails();
      });
  
      return {
        summaryData,
      };
    },
  });
  </script>