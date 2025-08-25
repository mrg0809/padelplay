<template>
  <q-layout view="hHh lpR fFf" class="bg-dark text-white">
    <q-header elevated class="text-white">
      <div class="header-content">
        <div class="greeting">
          <img src="/src/assets/padelplay.png" alt="Logo" class="logo-icon" />
        </div>
        <div class="header-icons">
        </div>
      </div>
    </q-header>

    <q-page-container class="home">
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
    
    <PlayerNavigationMenu />
  </q-layout>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useQuasar } from 'quasar';
import CheckoutAPI from 'src/components/CheckoutAPI.vue';
import PlayerNavigationMenu from 'src/components/PlayerNavigationMenu.vue';

export default {
  name: 'MercadoPayment',
  components: {
    CheckoutAPI,
    PlayerNavigationMenu
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
.home {
  min-height: calc(100vh - 50px);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  background-color: #000000;
}

.greeting { 
  display: flex; 
  align-items: center; 
  gap: 8px; 
}

.header-icons { 
  display: flex; 
  gap: 2px; 
  align-items: center; 
}

.logo-icon { 
  width: 60px; 
  height: 60px; 
}

.q-card {
  background-image: url(../assets/texturafondo.png);
  background-size: cover;
  background-position: center center;
  background-color: rgba(0, 0, 0, 0.6); 
  background-blend-mode: overlay;
  max-width: 450px; 
  margin: 16px auto;
  color: #fff;
  border-radius: 8px;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);
}

.text-white {
  color: white !important;
}

h3, h4 { 
  color: #FFF; 
  margin-bottom: 1rem; 
  font-weight: 500; 
}

p { 
  margin-bottom: 0.5rem; 
  line-height: 1.5; 
}

p strong { 
  color: #b3e5fc;
}

.q-separator--dark { 
  background: rgba(255, 255, 255, 0.3); 
}
</style>