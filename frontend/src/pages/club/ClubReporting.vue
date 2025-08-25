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
            <!-- Date Filter for Reports -->
            <div class="row q-gutter-md q-mb-lg">
              <div class="col-12 col-md-3">
                <q-input
                  v-model="startDate"
                  type="date"
                  label="Fecha Inicio"
                  outlined
                  dense
                  dark
                  color="white"
                />
              </div>
              <div class="col-12 col-md-3">
                <q-input
                  v-model="endDate"
                  type="date"
                  label="Fecha Fin"
                  outlined
                  dense
                  dark
                  color="white"
                />
              </div>
              <div class="col-12 col-md-3 flex items-end">
                <q-btn
                  @click="refreshReports"
                  color="primary"
                  label="Actualizar"
                  :loading="busy"
                  dense
                />
              </div>
            </div>

            <!-- Popular Days and Hours -->
            <div v-if="popularDays.length > 0" class="q-mb-lg">
              <h3>Días y Horas Más Concurridos</h3>
              <q-table
                :columns="popularDaysColumns"
                :rows="popularDays"
                row-key="day"
                dense
                class="bg-black"
              />
            </div>
            <div v-else class="q-mb-lg">
              <p>No hay datos suficientes para mostrar los días y horas más concurridos.</p>
            </div>

            <!-- Reservation Types Chart -->
            <div v-if="reservationTypesData.length > 0" class="q-mb-lg">
              <h3>Tipos de Reserva Más Frecuentes</h3>
              <div class="row q-gutter-md q-mb-md">
                <div v-for="type in reservationTypesData" :key="type.type" class="col-12 col-md-6 col-lg-3">
                  <q-card :class="`bg-${type.color} text-white`">
                    <q-card-section>
                      <div class="text-h6">{{ type.label }}</div>
                      <div class="text-h4 q-mt-sm">{{ type.count }}</div>
                      <div class="text-caption">{{ type.percentage.toFixed(1) }}% del total</div>
                    </q-card-section>
                  </q-card>
                </div>
              </div>
            </div>

            <!-- Chart Visualization -->
            <div v-if="chartDataComputed && chartDataComputed.labels.length > 0" class="bg-black chart-container">
              <h3 class="q-mb-md">Tendencia de Reservas por Día y Hora</h3>
              <div class="chart-wrapper">
                <line-chart
                  :key="chartDataComputed.labels.length"
                  :data="chartDataComputed"
                  :options="chartOptions"
                ></line-chart>
              </div>
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
  
  <script setup>
  import { ref, onMounted, computed } from "vue";
  import { supabase } from "src/services/supabase";
  import { useRouter } from "vue-router";
  import { useQuasar } from 'quasar';
  import ClubNavigationMenu from "src/components/ClubNavigationMenu.vue";
  import { useUserStore } from "src/stores/userStore";
  import { getReservationTypeStats } from "src/services/supabase/reservations.js";
  import { Line as LineChart } from 'vue-chartjs';
  import { Chart, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
  
  // Register the required components
  Chart.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);
  
  const router = useRouter();
  const userStore = useUserStore();
  const $q = useQuasar();
  const popularDays = ref([]);
  const reservationStats = ref([]);
  const busy = ref(true);
  const startDate = ref('');
  const endDate = ref('');
  
  const popularDaysColumns = ref([
    { name: 'day', label: 'Día', field: 'day', align: 'left' },
    { name: 'hour', label: 'Hora', field: 'hour', align: 'left' },
    { name: 'count', label: 'Reservas', field: 'count', align: 'right' }
  ]);
  
  const chartOptions = ref({
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      intersect: false,
      mode: 'index'
    },
    plugins: {
      legend: {
        labels: {
          color: 'white'
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: 'white',
        bodyColor: 'white'
      }
    },
    scales: {
      x: {
        type: 'category',
        title: {
          display: true,
          text: 'Día y Hora',
          color: 'white'
        },
        ticks: {
          color: 'white',
          maxRotation: 45,
          minRotation: 0
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        }
      },
      y: {
        type: 'linear',
        title: {
          display: true,
          text: 'Reservas',
          color: 'white'
        },
        ticks: {
          color: 'white',
          beginAtZero: true
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        }
      }
    }
  });

  const reservationTypesData = computed(() => {
    if (!reservationStats.value || reservationStats.value.length === 0) {
      return [];
    }

    // Count different types of reservations
    const typeCount = {
      regular: 0,
      tournament: 0,
      lesson: 0,
      match: 0
    };

    reservationStats.value.forEach(reservation => {
      // Determine type based on matches data and other factors
      if (reservation.matches && reservation.matches.length > 0) {
        const match = reservation.matches[0];
        if (match.event_type === 'tournament') {
          typeCount.tournament++;
        } else if (match.event_type === 'lesson') {
          typeCount.lesson++;
        } else {
          typeCount.match++;
        }
      } else {
        typeCount.regular++;
      }
    });

    const total = Object.values(typeCount).reduce((sum, count) => sum + count, 0);
    
    if (total === 0) return [];

    return [
      {
        type: 'regular',
        label: 'Reservas Regulares',
        count: typeCount.regular,
        percentage: (typeCount.regular / total) * 100,
        color: 'blue-7'
      },
      {
        type: 'match',
        label: 'Partidos',
        count: typeCount.match,
        percentage: (typeCount.match / total) * 100,
        color: 'green-7'
      },
      {
        type: 'tournament',
        label: 'Torneos',
        count: typeCount.tournament,
        percentage: (typeCount.tournament / total) * 100,
        color: 'orange-7'
      },
      {
        type: 'lesson',
        label: 'Lecciones',
        count: typeCount.lesson,
        percentage: (typeCount.lesson / total) * 100,
        color: 'purple-7'
      }
    ].filter(item => item.count > 0).sort((a, b) => b.count - a.count);
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
            borderColor: '#f87979',
            data: data,
            tension: 0.1
          }
        ]
      };
      console.log('Chart Data:', chartData);
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
      const { data, error } = await supabase.rpc('get_popular_reservation_days_by_club', { 
        club_id_input: userStore.clubId 
      });
      if (error) {
        console.error("Error fetching popular days:", error);
        $q.notify({
          type: 'negative',
          message: 'Error al cargar los días populares.'
        });
        return;
      }
      popularDays.value = data || [];
    } catch (err) {
      console.error("Error:", err);
      $q.notify({
        type: 'negative',
        message: 'Error inesperado al cargar los días populares.'
      });
    }
  };

  const fetchReservationTypes = async () => {
    try {
      const data = await getReservationTypeStats(
        userStore.clubId,
        startDate.value || null,
        endDate.value || null
      );
      reservationStats.value = data || [];
    } catch (error) {
      console.error("Error fetching reservation types:", error);
      $q.notify({
        type: 'negative',
        message: 'Error al cargar estadísticas de reservas.'
      });
    }
  };

  const refreshReports = async () => {
    busy.value = true;
    try {
      await Promise.all([
        fetchPopularDays(),
        fetchReservationTypes()
      ]);
    } finally {
      busy.value = false;
    }
  };

  onMounted(() => {
    // Set default date range to last 30 days
    const today = new Date();
    const thirtyDaysAgo = new Date(today);
    thirtyDaysAgo.setDate(today.getDate() - 30);
    
    startDate.value = thirtyDaysAgo.toISOString().split('T')[0];
    endDate.value = today.toISOString().split('T')[0];
    
    refreshReports();
  });
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
  
  /* Fix chart height for mobile display */
  .chart-container {
    border-radius: 8px;
    padding: 16px;
  }
  
  .chart-wrapper {
    position: relative;
    height: 400px; /* Fixed height to prevent stretching */
    width: 100%;
  }
  
  /* Mobile responsive heights */
  @media (max-width: 768px) {
    .chart-wrapper {
      height: 300px; /* Smaller height for mobile */
    }
  }
  
  @media (max-width: 480px) {
    .chart-wrapper {
      height: 250px; /* Even smaller for very small screens */
    }
  }
  </style>