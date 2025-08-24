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
        <div class="row q-col-gutter-md">
          <!-- Order Summary -->
          <div class="col-12 col-md-6">
            <q-card class="text-white">
              <q-card-section>
                <h4 class="text-white q-my-none">Resumen de la compra</h4>
              </q-card-section>
              
              <q-card-section>
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
              </q-card-section>
            </q-card>
          </div>
          
          <!-- Payment Form -->
          <div class="col-12 col-md-6">
            <q-card class="text-white" v-if="loading">
              <q-card-section>
                <div class="text-center">
                  <q-spinner color="primary" size="3rem" />
                  <p class="q-mt-md">Cargando formulario de pago...</p>
                </div>
              </q-card-section>
            </q-card>

            <q-card class="text-white" v-else-if="error">
              <q-card-section>
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
            </q-card>

            <CheckoutAPI 
              v-else
              :cart-items="cartItems"
              :user-info="userInfo"
              :total-amount="parseFloat(totalAmount)"
              :external-reference="externalReference"
              :metadata="metadata"
              @payment-success="handlePaymentSuccess"
              @payment-error="handlePaymentError"
            />
          </div>
        </div>

        <!-- Success Dialog -->
        <q-dialog v-model="showSuccessDialog" persistent>
          <q-card class="text-center">
            <q-card-section>
              <q-icon name="check_circle" color="positive" size="4rem" />
              <h4 class="q-my-md">¡Pago exitoso!</h4>
              <p>Tu pago ha sido procesado correctamente.</p>
            </q-card-section>
            <q-card-actions align="center">
              <q-btn 
                color="primary" 
                label="Continuar" 
                @click="navigateToSuccess"
              />
            </q-card-actions>
          </q-card>
        </q-dialog>

        <!-- Error Dialog -->
        <q-dialog v-model="showErrorDialog">
          <q-card class="text-center">
            <q-card-section>
              <q-icon name="error" color="negative" size="4rem" />
              <h4 class="q-my-md">Error en el pago</h4>
              <p>{{ paymentErrorMessage }}</p>
            </q-card-section>
            <q-card-actions align="center">
              <q-btn 
                color="primary" 
                label="Intentar nuevamente" 
                @click="showErrorDialog = false"
              />
            </q-card-actions>
          </q-card>
        </q-dialog>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useQuasar } from 'quasar';
import CheckoutAPI from 'src/components/CheckoutAPI.vue';

export default {
  name: 'MercadoPayment',
  components: {
    CheckoutAPI
  },
  setup() {
    const router = useRouter();
    const route = useRoute();
    const $q = useQuasar();
    
    const loading = ref(true);
    const error = ref(null);
    const cartItems = ref([]);
    const userInfo = ref({});
    const externalReference = ref(null);
    const metadata = ref(null);
    
    const showSuccessDialog = ref(false);
    const showErrorDialog = ref(false);
    const paymentErrorMessage = ref('');

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

    const handlePaymentSuccess = (paymentResult) => {
      console.log('Payment successful:', paymentResult);
      
      // Clear payment data from localStorage
      localStorage.removeItem('mercadoPaymentData');
      
      if (paymentResult.status === 'approved') {
        showSuccessDialog.value = true;
      } else if (paymentResult.status === 'pending') {
        $q.notify({
          type: 'info',
          message: 'Tu pago está siendo procesado. Te notificaremos cuando se complete.',
          timeout: 5000
        });
        
        // Navigate to dashboard after pending payment
        setTimeout(() => {
          router.push('/player/dashboard');
        }, 2000);
      } else {
        handlePaymentError('El pago no fue aprobado. Por favor, intenta con otro método de pago.');
      }
    };

    const handlePaymentError = (errorMessage) => {
      console.error('Payment error:', errorMessage);
      paymentErrorMessage.value = errorMessage;
      showErrorDialog.value = true;
    };

    const navigateToSuccess = () => {
      showSuccessDialog.value = false;
      
      // Navigate back to dashboard or success page
      router.push('/player/dashboard').catch(() => {
        // Fallback if dashboard route doesn't exist
        router.push('/');
      });
    };

    onMounted(() => {
      initPayment();
    });

    return {
      loading,
      error,
      cartItems,
      userInfo,
      externalReference,
      metadata,
      totalAmount,
      showSuccessDialog,
      showErrorDialog,
      paymentErrorMessage,
      initPayment,
      handlePaymentSuccess,
      handlePaymentError,
      navigateToSuccess
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