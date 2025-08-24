<template>
  <q-layout view="hHh lpR fFf" class="bg-dark text-white">
    <q-header elevated class="text-white">
      <div class="header-content">
        <div class="greeting">
          <img src="/src/assets/padelplay.png" alt="Logo" class="logo-icon" />
        </div>
      </div>
    </q-header>

    <q-page-container>
      <q-page class="q-pa-md">
        <q-card class="text-white">
          <q-card-section>
            <h3 class="text-white">Pago con Mercado Pago</h3>
          </q-card-section>
          
          <q-card-section v-if="loading">
            <div class="text-center">
              <q-spinner color="primary" size="3rem" />
              <p class="q-mt-md">Procesando pago...</p>
            </div>
          </q-card-section>

          <q-card-section v-else-if="error">
            <div class="text-center text-negative">
              <q-icon name="error" size="3rem" />
              <p class="q-mt-md">{{ error }}</p>
              <q-btn 
                color="primary" 
                label="Reintentar" 
                @click="initPayment" 
                class="q-mt-md" 
              />
            </div>
          </q-card-section>

          <q-card-section v-else>
            <div class="row q-col-gutter-md">
              <div class="col-12 col-md-6">
                <h5>Resumen de la compra:</h5>
                <div v-for="item in cartItems" :key="item.id" class="q-mb-sm">
                  <div class="row justify-between">
                    <span>{{ item.title }} (x{{ item.quantity }})</span>
                    <span>${{ (item.unit_price * item.quantity).toFixed(2) }}</span>
                  </div>
                </div>
                <q-separator class="q-my-md" />
                <div class="row justify-between text-h6">
                  <strong>Total: ${{ totalAmount }}</strong>
                </div>
              </div>
            </div>

            <div class="q-mt-lg text-center">
              <q-btn 
                color="primary" 
                size="lg"
                label="Pagar con Mercado Pago" 
                @click="processPayment"
                :loading="processing"
              />
            </div>
            
            <!-- Development mode notice -->
            <div class="q-mt-md text-center text-caption">
              <p class="text-grey-5">
                Después de completar el pago en Mercado Pago, 
                <br>vuelve manualmente a la aplicación.
              </p>
            </div>
          </q-card-section>
        </q-card>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useQuasar } from 'quasar';
import api from 'src/services/api';

export default {
  name: 'MercadoPayment',
  setup() {
    const router = useRouter();
    const route = useRoute();
    const $q = useQuasar();
    
    const loading = ref(true);
    const processing = ref(false);
    const error = ref(null);
    const cartItems = ref([]);
    const userInfo = ref({});
    const externalReference = ref(null);
    const metadata = ref(null);

    const totalAmount = computed(() => {
      return cartItems.value.reduce((total, item) => {
        return total + (item.unit_price * item.quantity);
      }, 0).toFixed(2);
    });

    const initPayment = () => {
      loading.value = true;
      error.value = null;
      
      // Get payment data from route params or localStorage
      try {
        const paymentData = route.params.paymentData || JSON.parse(localStorage.getItem('mercadoPaymentData') || '{}');
        
        if (!paymentData.cartItems || !paymentData.userInfo) {
          throw new Error('Datos de pago incompletos');
        }

        cartItems.value = paymentData.cartItems;
        userInfo.value = paymentData.userInfo;
        externalReference.value = paymentData.externalReference;
        metadata.value = paymentData.metadata;
        
        loading.value = false;
      } catch (err) {
        error.value = 'Error al cargar los datos de pago. Por favor, inténtalo nuevamente.';
        loading.value = false;
      }
    };

    const processPayment = async () => {
      processing.value = true;
      
      try {
        // Call the backend API to create preference
        const response = await api.post('/payments/create_preference', {
          cart_items: cartItems.value,
          user_info: userInfo.value,
          external_reference: externalReference.value,
          metadata: metadata.value
        });

        if (response.data && response.data.init_point) {
          // Redirect to MercadoPago checkout using the init_point
          window.location.href = response.data.init_point;
        } else {
          throw new Error('No se recibió la URL de pago de Mercado Pago');
        }
        
      } catch (err) {
        console.error('Error al procesar el pago:', err);
        error.value = err.response?.data?.detail || 'Error al procesar el pago. Por favor, inténtalo nuevamente.';
        
        $q.notify({
          type: 'negative',
          message: error.value
        });
      } finally {
        processing.value = false;
      }
    };

    onMounted(() => {
      initPayment();
    });

    return {
      loading,
      processing,
      error,
      cartItems,
      totalAmount,
      initPayment,
      processPayment
    };
  }
};
</script>

<style scoped>
.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 20px;
}

.logo-icon {
  height: 40px;
}

.q-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

.text-white {
  color: white !important;
}
</style>