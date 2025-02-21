<template>
    <q-layout view="hHh lpR fFf" class="body text-white">
      <q-header elevated class="bg-primary text-white">
        <div class="header-content">
          <div class="greeting">
            <img src="/src/assets/padelplay.png" alt="Logo" class="logo-icon" />
            Reportes
          </div>
          <div class="header-icons">
            <q-btn flat round icon="arrow_back" @click="goBack" />
          </div>
        </div>
      </q-header>
  
      <q-page-container>
        <q-page class="q-pa-md">
          <div v-if="busy">
            <q-spinner-puff color="primary" size="3em" />
            <p>Cargando datos...</p>
          </div>
          <div v-else>
            <div v-if="popularDays.length > 0">
              <h3>Días y Horas Más Concurridos</h3>
              <q-table
                :columns="popularDaysColumns"
                :rows="popularDays"
                row-key="day"
                dense
                class="bg-black"
              />
            </div>
            <div v-else>
              <p>No hay datos suficientes para mostrar los días y horas más concurridos.</p>
            </div>
            <div v-if="chartDataComputed && chartDataComputed.labels.length > 0" class="bg-black">
              <line-chart
                :key="chartDataComputed.labels.length"
                :data="chartDataComputed"
                :options="chartOptions"
              ></line-chart>
            </div>
            <div v-else>
              <p>No hay datos para mostrar el gráfico.</p>
            </div>
          </div>
        </q-page>
      </q-page-container>
      <ClubNavigationMenu />
    </q-layout>
  </template>
  
  <script>
  import { ref, onMounted, computed } from "vue";
  import { supabase } from "src/services/supabase";
  import { useRouter } from "vue-router";
  import { useQuasar } from 'quasar';
  import ClubNavigationMenu from "src/components/ClubNavigationMenu.vue";
  import { useUserStore } from "src/stores/userStore";
  import { Line } from 'vue-chartjs';
  import { Chart, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
  
  // Register the required components
  Chart.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);
  
  export default {
    name: "ClubReporting",
    components: {
      ClubNavigationMenu,
      LineChart: Line
    },
    setup() {
      const router = useRouter();
      const userStore = useUserStore();
      const $q = useQuasar();
      const popularDays = ref([]);
      const popularDaysColumns = ref([
        { name: 'day', label: 'Día', field: 'day', align: 'left' },
        { name: 'hour', label: 'Hora', field: 'hour', align: 'left' },
        { name: 'count', label: 'Reservas', field: 'count', align: 'right' }
      ]);
      const busy = ref(true);
      const chartOptions = ref({
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            type: 'category', // Use the 'category' scale for the x-axis
            title: {
              display: true,
              text: 'Día y Hora'
            }
          },
          y: {
            type: 'linear', // Use the 'linear' scale for the y-axis
            title: {
              display: true,
              text: 'Reservas'
            }
          }
        }
      });
  
      const chartDataComputed = computed(() => {
        if (popularDays.value && popularDays.value.length > 0) {
          const labels = popularDays.value.map(item => `${item.day} - ${item.hour}`);
          const data = popularDays.value.map(item => item.count);
          const chartData = {
            labels: labels,
            datasets: [
              {
                label: 'Reservas por día y hora',
                backgroundColor: '#f87979',
                data: data
              }
            ]
          };
          console.log('Chart Data:', chartData); // Debugging
          return chartData;
        } else {
          return {
            labels: [],
            datasets: []
          };
        }
      });
  
      const goBack = () => {
        router.back();
      };
  
      const fetchPopularDays = async () => {
        try {
          const { data, error } = await supabase.rpc('get_popular_reservation_days_by_club', { club_id_input: userStore.clubId });
          if (error) {
            console.error("Error fetching popular days:", error);
            $q.notify({
              type: 'negative',
              message: 'Error al cargar los datos.'
            });
            return;
          }
          popularDays.value = data;
        } catch (err) {
          console.error("Error:", err);
          $q.notify({
            type: 'negative',
            message: 'Error inesperado al cargar los datos.'
          });
        } finally {
          busy.value = false;
        }
      };
  
      onMounted(() => {
        fetchPopularDays();
      });
  
      return {
        goBack,
        popularDays,
        popularDaysColumns,
        busy,
        chartDataComputed,
        chartOptions
      };
    },
  };
  </script>
  
  <style scoped>
  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 16px;
    background-color: #000000;
  }
  
  .greeting {
    font-size: 1rem;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  .header-icons {
    display: flex;
    gap: 2px;
  }
  
  .logo-icon {
    width: 60px;
    height: 60px;
  }
  
  .body {
    background-image: url(../../assets/menu/padelcourtfloor.jpg);
    background-size: cover;
  }
  
  </style>