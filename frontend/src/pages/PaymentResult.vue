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
      <q-page class="q-pa-md flex flex-center">
        <q-card class="text-center q-pa-lg" style="min-width: 300px;">
          <q-card-section>
            <div v-if="status === 'success'" class="text-positive">
              <q-icon name="check_circle" size="4rem" />
              <h4 class="q-mt-md q-mb-md">¡Pago Exitoso!</h4>
              <p>Tu pago se ha procesado correctamente.</p>
            </div>
            
            <div v-else-if="status === 'failure'" class="text-negative">
              <q-icon name="cancel" size="4rem" />
              <h4 class="q-mt-md q-mb-md">Pago Fallido</h4>
              <p>Hubo un problema con tu pago. Por favor, inténtalo nuevamente.</p>
            </div>
            
            <div v-else-if="status === 'pending'" class="text-warning">
              <q-icon name="access_time" size="4rem" />
              <h4 class="q-mt-md q-mb-md">Pago Pendiente</h4>
              <p>Tu pago está siendo procesado. Te notificaremos cuando se complete.</p>
            </div>
          </q-card-section>
          
          <q-card-actions align="center">
            <q-btn 
              color="primary" 
              label="Volver al Inicio" 
              @click="goHome" 
            />
            <q-btn 
              v-if="status === 'failure'"
              color="secondary" 
              label="Reintentar Pago" 
              @click="retryPayment" 
            />
          </q-card-actions>
        </q-card>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script>
import { onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useQuasar } from 'quasar';

export default {
  name: 'PaymentResult',
  props: {
    status: {
      type: String,
      required: true,
      validator: (value) => ['success', 'failure', 'pending'].includes(value)
    }
  },
  setup(props) {
    const router = useRouter();
    const route = useRoute();
    const $q = useQuasar();

    const goHome = () => {
      router.push('/dashboard/player');
    };

    const retryPayment = () => {
      // Go back to payment page or redirect to appropriate flow
      const paymentData = localStorage.getItem('mercadoPaymentData');
      if (paymentData) {
        router.push('/mercado-payment');
      } else {
        router.push('/dashboard/player');
      }
    };

    onMounted(() => {
      // Show notification based on status
      if (props.status === 'success') {
        $q.notify({
          type: 'positive',
          message: '¡Pago exitoso! Gracias por tu compra.',
          timeout: 5000
        });
      } else if (props.status === 'failure') {
        $q.notify({
          type: 'negative',
          message: 'El pago no pudo ser procesado.',
          timeout: 5000
        });
      } else if (props.status === 'pending') {
        $q.notify({
          type: 'info',
          message: 'Tu pago está siendo procesado.',
          timeout: 5000
        });
      }

      // Get URL parameters for additional payment info
      const paymentId = route.query.payment_id;
      const preferenceId = route.query.preference_id;
      const merchantOrder = route.query.merchant_order_id;
      
      console.log('Payment result:', {
        status: props.status,
        paymentId,
        preferenceId,
        merchantOrder
      });

      // TODO: You might want to send this info to your backend to verify the payment
    });

    return {
      goHome,
      retryPayment
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