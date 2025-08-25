<template>
    <q-layout view="hHh lpR fFf" class="body text-white">
      <q-header elevated class="bg-primary text-white">
        <div class="header-content">
          <div class="greeting">
            <img src="/src/assets/padelplay.png" alt="Logo" class="logo-icon" />
            Balance de Pagos
          </div>
          <div class="header-icons">
            <q-btn flat round icon="arrow_back" @click="goBack" />
          </div>
        </div>
      </q-header>
  
      <q-page-container>
        <q-page class="q-pa-md">
          <!-- Date Filter -->
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
                @click="fetchPaymentSummary"
                color="primary"
                label="Actualizar"
                :loading="loading"
                dense
              />
            </div>
          </div>

          <!-- Loading State -->
          <div v-if="loading" class="text-center q-my-lg">
            <q-spinner-puff color="primary" size="3em" />
            <p class="q-mt-md">Cargando balance...</p>
          </div>

          <!-- Payment Summary Cards -->
          <div v-else class="row q-gutter-md q-mb-lg">
            <div class="col-12 col-md-6 col-lg-3">
              <q-card class="bg-blue-7 text-white">
                <q-card-section>
                  <div class="text-h6">
                    <q-icon name="payments" class="q-mr-sm" />
                    Total Facturado
                  </div>
                  <div class="text-h4 q-mt-sm">${{ summary.totalAmount.toFixed(2) }}</div>
                  <div class="text-caption">Ingresos brutos del período</div>
                </q-card-section>
              </q-card>
            </div>

            <div class="col-12 col-md-6 col-lg-3">
              <q-card class="bg-orange-7 text-white">
                <q-card-section>
                  <div class="text-h6">
                    <q-icon name="account_balance" class="q-mr-sm" />
                    Comisión Plataforma
                  </div>
                  <div class="text-h4 q-mt-sm">${{ summary.totalCommission.toFixed(2) }}</div>
                  <div class="text-caption">{{ commissionPercentage.toFixed(1) }}% del total</div>
                </q-card-section>
              </q-card>
            </div>

            <div class="col-12 col-md-6 col-lg-3">
              <q-card class="bg-green-7 text-white">
                <q-card-section>
                  <div class="text-h6">
                    <q-icon name="account_balance_wallet" class="q-mr-sm" />
                    Total Recibido
                  </div>
                  <div class="text-h4 q-mt-sm">${{ summary.netAmount.toFixed(2) }}</div>
                  <div class="text-caption">Ingresos netos recibidos</div>
                </q-card-section>
              </q-card>
            </div>

            <div class="col-12 col-md-6 col-lg-3">
              <q-card class="bg-purple-7 text-white">
                <q-card-section>
                  <div class="text-h6">
                    <q-icon name="receipt_long" class="q-mr-sm" />
                    Total Transacciones
                  </div>
                  <div class="text-h4 q-mt-sm">{{ summary.transactionCount }}</div>
                  <div class="text-caption">Pagos procesados</div>
                </q-card-section>
              </q-card>
            </div>
          </div>

          <!-- Payment Breakdown -->
          <div v-if="!loading && summary.totalAmount > 0" class="row q-gutter-md">
            <div class="col-12 col-md-6">
              <q-card class="bg-dark text-white">
                <q-card-section>
                  <div class="text-h6 q-mb-md">Desglose por Tipo de Servicio</div>
                  <div v-for="(item, type) in eventTypeBreakdown" :key="type" class="row q-my-sm">
                    <div class="col-6">
                      <q-chip :color="getEventTypeColor(type)" text-color="white" dense>
                        {{ getEventTypeLabel(type) }}
                      </q-chip>
                    </div>
                    <div class="col-3 text-right">${{ item.amount.toFixed(2) }}</div>
                    <div class="col-3 text-right text-caption">{{ item.count }} transacciones</div>
                  </div>
                </q-card-section>
              </q-card>
            </div>

            <div class="col-12 col-md-6">
              <q-card class="bg-dark text-white">
                <q-card-section>
                  <div class="text-h6 q-mb-md">Métodos de Pago</div>
                  <div v-for="(item, method) in paymentMethodBreakdown" :key="method" class="row q-my-sm">
                    <div class="col-6">
                      <q-chip color="grey-7" text-color="white" dense>
                        {{ getPaymentMethodLabel(method) }}
                      </q-chip>
                    </div>
                    <div class="col-3 text-right">${{ item.amount.toFixed(2) }}</div>
                    <div class="col-3 text-right text-caption">{{ item.count }} pagos</div>
                  </div>
                </q-card-section>
              </q-card>
            </div>
          </div>

          <!-- No Data -->
          <div v-if="!loading && summary.totalAmount === 0" class="text-center q-my-lg">
            <q-icon name="account_balance_wallet" size="4em" color="grey" />
            <p class="text-h6 q-mt-md">No hay pagos en este período</p>
            <p class="text-grey">Ajusta las fechas para ver más resultados</p>
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
  import { getClubPaymentSummary, getClubPaymentOrdersWithFilters } from "src/services/supabase/payments.js";
import { debugPaymentOrders, debugClubPaymentApproaches } from "src/services/supabase/paymentsDebug.js";
  
  const router = useRouter();
  const $q = useQuasar();
  const userStore = useUserStore();
  
  const loading = ref(false);
  const startDate = ref('');
  const endDate = ref('');
  const paymentData = ref([]);
  
  const summary = computed(() => {
    if (paymentData.value.length === 0) {
      return {
        totalAmount: 0,
        totalCommission: 0,
        netAmount: 0,
        transactionCount: 0
      };
    }

    const totalAmount = paymentData.value.reduce((sum, item) => sum + Number(item.total_amount || 0), 0);
    const totalCommission = paymentData.value.reduce((sum, item) => sum + Number(item.club_commission || 0) + Number(item.player_commission || 0), 0);
    
    return {
      totalAmount,
      totalCommission,
      netAmount: totalAmount - totalCommission,
      transactionCount: paymentData.value.length
    };
  });

  const commissionPercentage = computed(() => {
    return summary.value.totalAmount > 0 
      ? (summary.value.totalCommission / summary.value.totalAmount) * 100 
      : 0;
  });

  const eventTypeBreakdown = computed(() => {
    const breakdown = {};
    paymentData.value.forEach(item => {
      const type = item.event_type || 'unknown';
      if (!breakdown[type]) {
        breakdown[type] = { amount: 0, count: 0 };
      }
      breakdown[type].amount += Number(item.total_amount || 0);
      breakdown[type].count += 1;
    });
    return breakdown;
  });

  const paymentMethodBreakdown = computed(() => {
    const breakdown = {};
    paymentData.value.forEach(item => {
      const method = item.payment_method || 'unknown';
      if (!breakdown[method]) {
        breakdown[method] = { amount: 0, count: 0 };
      }
      breakdown[method].amount += Number(item.total_amount || 0);
      breakdown[method].count += 1;
    });
    return breakdown;
  });
  
  const goBack = () => {
    router.back();
  };

  const getEventTypeLabel = (eventType) => {
    const labels = {
      'reservation': 'Reservas',
      'lesson': 'Lecciones',
      'tournament': 'Torneos',
      'product': 'Productos',
      'unknown': 'Otros'
    };
    return labels[eventType] || eventType;
  };

  const getEventTypeColor = (eventType) => {
    const colors = {
      'reservation': 'blue',
      'lesson': 'green',
      'tournament': 'orange',
      'product': 'purple',
      'unknown': 'grey'
    };
    return colors[eventType] || 'grey';
  };

  const getPaymentMethodLabel = (method) => {
    const labels = {
      'credit_card': 'Tarjeta de Crédito',
      'debit_card': 'Tarjeta de Débito',
      'cash': 'Efectivo',
      'bank_transfer': 'Transferencia',
      'mercadopago': 'MercadoPago',
      'stripe': 'Stripe',
      'unknown': 'Otros'
    };
    return labels[method] || method;
  };

  const fetchPaymentSummary = async () => {
    console.log('DEBUG: userStore data:', { 
      userId: userStore.userId, 
      clubId: userStore.clubId, 
      userType: userStore.userType,
      email: userStore.email
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
      // Run comprehensive debugging first
      console.log('=== RUNNING PAYMENT DEBUG ANALYSIS ===');
      await debugPaymentOrders();
      await debugClubPaymentApproaches(userStore.clubId);
      console.log('=== DEBUG ANALYSIS COMPLETE ===');
      
      const data = await getClubPaymentOrdersWithFilters(
        userStore.clubId,
        startDate.value || null,
        endDate.value || null,
        null // No filter by event type for summary
      );
      paymentData.value = data;
    } catch (error) {
      console.error('Error fetching payment summary:', error);
      $q.notify({
        type: 'negative',
        message: 'Error al cargar el balance de pagos'
      });
    } finally {
      loading.value = false;
    }
  };

  onMounted(() => {
    // Set default date range to current month
    const today = new Date();
    const firstDayOfMonth = new Date(today.getFullYear(), today.getMonth(), 1);
    
    startDate.value = firstDayOfMonth.toISOString().split('T')[0];
    endDate.value = today.toISOString().split('T')[0];
    
    fetchPaymentSummary();
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