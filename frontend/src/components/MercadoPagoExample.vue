<template>
  <q-card class="q-pa-md">
    <q-card-section>
      <h5>Ejemplo de Integración MercadoPago</h5>
      <p>Esta es una demostración de cómo integrar MercadoPago desde cualquier componente.</p>
    </q-card-section>

    <q-card-section>
      <h6>Datos del Carrito:</h6>
      <div v-for="item in sampleCartItems" :key="item.id" class="q-mb-sm">
        <div class="row justify-between">
          <span>{{ item.title }} (x{{ item.quantity }})</span>
          <span>${{ (item.unit_price * item.quantity).toFixed(2) }}</span>
        </div>
      </div>
      <q-separator class="q-my-md" />
      <div class="row justify-between text-h6">
        <strong>Total: ${{ total }}</strong>
      </div>
    </q-card-section>

    <q-card-actions align="right">
      <q-btn 
        color="primary" 
        label="Método 1: Usar Página de Pago"
        @click="usePaymentPage"
        :loading="loading"
        class="q-mr-sm"
      />
      <q-btn 
        color="secondary" 
        label="Método 2: Integración Directa"
        @click="useDirectIntegration"
        :loading="loading"
      />
    </q-card-actions>

    <q-card-section>
      <q-expansion-item label="Ver código de ejemplo">
        <div class="q-pa-md">
          <pre><code>{{ sampleCode }}</code></pre>
        </div>
      </q-expansion-item>
    </q-card-section>
  </q-card>
</template>

<script>
import { ref, computed } from 'vue';
import { useQuasar } from 'quasar';
import { initiateMercadoPagoPayment, processMercadoPagoPayment } from 'src/helpers/mercadoPagoUtils';

export default {
  name: 'MercadoPagoExample',
  setup() {
    const $q = useQuasar();
    const loading = ref(false);

    const sampleCartItems = ref([
      {
        id: 'reservation_001',
        title: 'Reserva de Cancha - Club ABC',
        quantity: 1,
        unit_price: 5000.00
      },
      {
        id: 'product_001', 
        title: 'Pelota de Pádel Wilson',
        quantity: 2,
        unit_price: 1500.00
      }
    ]);

    const sampleUserInfo = ref({
      email: 'usuario@ejemplo.com',
      name: 'Juan Pérez'
    });

    const total = computed(() => {
      return sampleCartItems.value.reduce((sum, item) => {
        return sum + (item.unit_price * item.quantity);
      }, 0).toFixed(2);
    });

    // Método 1: Usar la página de pago dedicada
    const usePaymentPage = () => {
      try {
        const paymentData = {
          cartItems: sampleCartItems.value,
          userInfo: sampleUserInfo.value,
          externalReference: `example_${Date.now()}`,
          metadata: {
            source: 'example_component',
            timestamp: new Date().toISOString()
          }
        };

        // Esto almacena los datos y redirige a /mercado-payment
        initiateMercadoPagoPayment(paymentData);
        
      } catch (error) {
        console.error('Error:', error);
        $q.notify({
          type: 'negative',
          message: 'Error al iniciar el pago'
        });
      }
    };

    // Método 2: Integración directa con redirección inmediata
    const useDirectIntegration = async () => {
      loading.value = true;
      
      try {
        // Esto llama directamente a la API y redirige a MercadoPago
        await processMercadoPagoPayment(
          sampleCartItems.value,
          sampleUserInfo.value,
          `direct_${Date.now()}`,
          {
            source: 'direct_integration',
            component: 'MercadoPagoExample'
          }
        );

      } catch (error) {
        console.error('Error:', error);
        $q.notify({
          type: 'negative',
          message: error.response?.data?.detail || 'Error al procesar el pago'
        });
      } finally {
        loading.value = false;
      }
    };

    const sampleCode = `
// Método 1: Usar página de pago
import { initiateMercadoPagoPayment } from 'src/helpers/mercadoPagoUtils';

const paymentData = {
  cartItems: [
    {
      id: 'item_1',
      title: 'Producto',
      quantity: 1, 
      unit_price: 5000.00
    }
  ],
  userInfo: {
    email: 'user@example.com',
    name: 'Juan Pérez'
  },
  externalReference: 'order_123'
};

initiateMercadoPagoPayment(paymentData);

// Método 2: Integración directa
import { processMercadoPagoPayment } from 'src/helpers/mercadoPagoUtils';

await processMercadoPagoPayment(
  cartItems,
  userInfo,
  'order_123',
  { metadata: 'example' }
);
    `.trim();

    return {
      loading,
      sampleCartItems,
      total,
      usePaymentPage,
      useDirectIntegration,
      sampleCode
    };
  }
};
</script>

<style scoped>
pre {
  background-color: #f5f5f5;
  padding: 16px;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 12px;
  line-height: 1.4;
}

code {
  font-family: 'Monaco', 'Courier New', monospace;
}
</style>