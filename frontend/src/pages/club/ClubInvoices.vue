<template>
    <q-layout view="hHh lpR fFf" class="body text-white">
      <q-header elevated class="bg-primary text-white">
        <div class="header-content">
          <div class="greeting">
            <img src="/src/assets/padelplay.png" alt="Logo" class="logo-icon" />
            Facturas
          </div>
          <div class="header-icons">
            <q-btn flat round icon="arrow_back" @click="goBack" />
          </div>
        </div>
      </q-header>
  
      <q-page-container>
        <q-page class="q-pa-md">
          <!-- Filters -->
          <div class="row q-gutter-md q-mb-md">
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
            <div class="col-12 col-md-3">
              <q-select
                v-model="selectedEventType"
                :options="eventTypeOptions"
                label="Tipo de Reserva"
                outlined
                dense
                dark
                color="white"
                clearable
              />
            </div>
            <div class="col-12 col-md-3 flex items-end">
              <q-btn
                @click="fetchPaymentOrders"
                color="primary"
                label="Filtrar"
                :loading="loading"
                dense
              />
            </div>
          </div>

          <!-- Loading State -->
          <div v-if="loading" class="text-center q-my-lg">
            <q-spinner-puff color="primary" size="3em" />
            <p class="q-mt-md">Cargando facturas...</p>
          </div>

          <!-- Payment Orders Table -->
          <div v-else-if="paymentOrders.length > 0">
            <q-table
              :columns="columns"
              :rows="paymentOrders"
              row-key="id"
              dense
              class="bg-black text-white"
              :rows-per-page-options="[10, 25, 50]"
              rows-per-page-label="Filas por página:"
              no-data-label="No hay facturas disponibles"
            >
              <template v-slot:body-cell-order_date="props">
                <q-td :props="props">
                  {{ formatDate(props.value) }}
                </q-td>
              </template>
              <template v-slot:body-cell-total_amount="props">
                <q-td :props="props">
                  ${{ Number(props.value).toFixed(2) }}
                </q-td>
              </template>
              <template v-slot:body-cell-club_commission="props">
                <q-td :props="props">
                  ${{ Number(props.value || 0).toFixed(2) }}
                </q-td>
              </template>
              <template v-slot:body-cell-player_commission="props">
                <q-td :props="props">
                  ${{ Number(props.value || 0).toFixed(2) }}
                </q-td>
              </template>
              <template v-slot:body-cell-net_amount="props">
                <q-td :props="props" class="text-green">
                  ${{ calculateNetAmount(props.row) }}
                </q-td>
              </template>
              <template v-slot:body-cell-event_type="props">
                <q-td :props="props">
                  <q-chip 
                    :color="getEventTypeColor(props.value)"
                    text-color="white" 
                    dense
                  >
                    {{ getEventTypeLabel(props.value) }}
                  </q-chip>
                </q-td>
              </template>
            </q-table>

            <!-- Summary -->
            <div class="row q-gutter-md q-mt-lg">
              <div class="col-12 col-md-3">
                <q-card class="bg-primary text-white">
                  <q-card-section>
                    <div class="text-h6">Total Facturado</div>
                    <div class="text-h4">${{ totalAmount.toFixed(2) }}</div>
                  </q-card-section>
                </q-card>
              </div>
              <div class="col-12 col-md-3">
                <q-card class="bg-orange text-white">
                  <q-card-section>
                    <div class="text-h6">Comisión Plataforma</div>
                    <div class="text-h4">${{ totalCommission.toFixed(2) }}</div>
                  </q-card-section>
                </q-card>
              </div>
              <div class="col-12 col-md-3">
                <q-card class="bg-green text-white">
                  <q-card-section>
                    <div class="text-h6">Total Recibido</div>
                    <div class="text-h4">${{ totalNet.toFixed(2) }}</div>
                  </q-card-section>
                </q-card>
              </div>
            </div>
          </div>

          <!-- No Data -->
          <div v-else class="text-center q-my-lg">
            <q-icon name="receipt" size="4em" color="grey" />
            <p class="text-h6 q-mt-md">No hay facturas para mostrar</p>
            <p class="text-grey">Ajusta los filtros para ver más resultados</p>
          </div>
        </q-page>
      </q-page-container>
      <ClubNavigationMenu />
    </q-layout>
  </template>
  
  <script setup>
  import { ref, onMounted, computed } from "vue";
  import { useRouter } from "vue-router";
  import { useQuasar } from 'quasar';
  import { useUserStore } from "src/stores/userStore";
  import ClubNavigationMenu from "src/components/ClubNavigationMenu.vue";
  import { getClubPaymentOrdersWithFilters } from "src/services/supabase/payments.js";
  
  const router = useRouter();
  const $q = useQuasar();
  const userStore = useUserStore();
  
  const paymentOrders = ref([]);
  const loading = ref(false);
  const startDate = ref('');
  const endDate = ref('');
  const selectedEventType = ref('');
  
  const eventTypeOptions = ref([
    { label: 'Reservas', value: 'reservation' },
    { label: 'Lecciones', value: 'lesson' },
    { label: 'Torneos', value: 'tournament' },
    { label: 'Productos', value: 'product' }
  ]);
  
  const columns = ref([
    { name: 'order_date', label: 'Fecha', field: 'order_date', align: 'left', sortable: true },
    { name: 'customer', label: 'Cliente', field: row => row.profiles?.full_name || 'N/A', align: 'left' },
    { name: 'event_type', label: 'Tipo', field: 'event_type', align: 'center' },
    { name: 'payment_method', label: 'Método de Pago', field: 'payment_method', align: 'center' },
    { name: 'total_amount', label: 'Monto Total', field: 'total_amount', align: 'right', sortable: true },
    { name: 'club_commission', label: 'Comisión Club', field: 'club_commission', align: 'right' },
    { name: 'player_commission', label: 'Comisión Jugador', field: 'player_commission', align: 'right' },
    { name: 'net_amount', label: 'Monto Neto', field: 'net_amount', align: 'right' }
  ]);

  const totalAmount = computed(() => {
    return paymentOrders.value.reduce((sum, order) => sum + Number(order.total_amount || 0), 0);
  });

  const totalCommission = computed(() => {
    return paymentOrders.value.reduce((sum, order) => sum + Number(order.club_commission || 0) + Number(order.player_commission || 0), 0);
  });

  const totalNet = computed(() => {
    return paymentOrders.value.reduce((sum, order) => {
      const total = Number(order.total_amount || 0);
      const commission = Number(order.club_commission || 0) + Number(order.player_commission || 0);
      return sum + (total - commission);
    }, 0);
  });
  
  const goBack = () => {
    router.back();
  };

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const calculateNetAmount = (row) => {
    const total = Number(row.total_amount || 0);
    const commission = Number(row.club_commission || 0) + Number(row.player_commission || 0);
    return (total - commission).toFixed(2);
  };

  const getEventTypeLabel = (eventType) => {
    const labels = {
      'reservation': 'Reserva',
      'lesson': 'Lección',
      'tournament': 'Torneo',
      'product': 'Producto'
    };
    return labels[eventType] || eventType;
  };

  const getEventTypeColor = (eventType) => {
    const colors = {
      'reservation': 'blue',
      'lesson': 'green',
      'tournament': 'orange',
      'product': 'purple'
    };
    return colors[eventType] || 'grey';
  };

  const fetchPaymentOrders = async () => {
    console.log('DEBUG ClubInvoices: userStore data:', { 
      userId: userStore.userId, 
      clubId: userStore.clubId, 
      userType: userStore.userType 
    });
    
    if (!userStore.clubId) {
      $q.notify({
        type: 'negative',
        message: 'No se encontró información del club'
      });
      return;
    }

    loading.value = true;
    try {
      const data = await getClubPaymentOrdersWithFilters(
        userStore.clubId,
        startDate.value || null,
        endDate.value || null,
        selectedEventType.value || null
      );
      paymentOrders.value = data;
    } catch (error) {
      console.error('Error fetching payment orders:', error);
      $q.notify({
        type: 'negative',
        message: 'Error al cargar las facturas'
      });
    } finally {
      loading.value = false;
    }
  };

  onMounted(() => {
    // Set default date range to last 30 days
    const today = new Date();
    const thirtyDaysAgo = new Date(today);
    thirtyDaysAgo.setDate(today.getDate() - 30);
    
    startDate.value = thirtyDaysAgo.toISOString().split('T')[0];
    endDate.value = today.toISOString().split('T')[0];
    
    fetchPaymentOrders();
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
  
  </style>