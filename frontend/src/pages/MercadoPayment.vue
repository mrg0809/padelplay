<template>
    <q-layout view="hHh lpR fFf" class="bg-dark text-white">
      <q-header elevated class="text-white">
        <div class="header-content">
          <div class="greeting">
            <img src="/src/assets/padelplay.png" alt="Logo" class="logo-icon" />
          </div>
          <div class="header-icons">
            <q-btn flat round icon="close" @click="goBack" />
          </div>
        </div>
      </q-header>
  
      <q-page-container>
        <q-page class="q-pa-md">
          <q-card class="text-white">
            <q-card-section>
              <h3 class="text-white q-mt-none q-mb-md">Realizar Pago con Mercado Pago</h3>
            </q-card-section>
  
            <q-card-section class="q-pt-none">
              <div id="mercadopago-bricks-container">
                </div>
              <div v-if="paymentError" class="text-negative q-mt-sm">{{ paymentError }}</div>
            </q-card-section>
  
            <q-card-section class="q-pt-none">
              <p class="text-caption text-grey-5">
                Revisa los detalles de tu compra antes de pagar.
              </p>
              <p><strong>Total a pagar:</strong> ${{ totalAmount }}</p>
              </q-card-section>
          </q-card>
        </q-page>
      </q-page-container>
    </q-layout>
  </template>
  
  <script>
  import { ref, onMounted } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import { useQuasar } from 'quasar';
  import api from '../services/api';
  
  export default {
    name: 'MercadoPaymentPage', // Asegúrate que el 'name' coincida con tu router
    setup() {
      const route = useRoute();
      const router = useRouter();
      const $q = useQuasar();
  
      const initPoint = ref(route.query.initPoint);
      const preferenceId = ref(route.query.preferenceId);
      const totalAmount = ref(route.query.total || '0.00');
      const paymentError = ref(null);
      const mp = ref(null);
  
      const loadMercadoPagoSDK = () => {
        return new Promise((resolve, reject) => {
          if (window.MercadoPago) {
            mp.value = new window.MercadoPago(import.meta.env.VITE_MERCADOPAGO_PUBLIC_KEY);
            resolve();
            return;
          }
          const script = document.createElement('script');
          script.src = 'https://sdk.mercadopago.com/js/v2';
          script.onload = () => {
            window.MercadoPago.setPublishableKey = undefined; // Eliminar la función si existe incorrectamente
            mp.value = new window.MercadoPago(import.meta.env.VITE_MERCADOPAGO_PUBLIC_KEY);
            resolve();
          };
          script.onerror = () => {
            paymentError.value = 'Error al cargar la pasarela de pago.';
            reject('Error al cargar SDK de Mercado Pago');
          };
          document.head.appendChild(script);
        });
      };
  
      onMounted(async () => {
        await loadMercadoPagoSDK();
        if (!initPoint.value) {
          $q.notify({
            type: 'negative',
            message: 'Enlace de pago inválido.',
          });
          router.push({ name: 'DashboardPlayer' });
          return;
        }
        await initMercadoPagoBrick();
      });
  
      const initMercadoPagoBrick = async () => {
        try {
          if (!mp.value) {
            console.error('SDK de Mercado Pago no inicializado.');
            paymentError.value = 'Error al iniciar el pago.';
            return;
          }
  
          const paymentBrickController = await mp.value.bricks().create('payment', 'mercadopago-bricks-container', {
            initialization: {
              amount: totalAmount.value,
              preferenceId: preferenceId.value,
              payer: {
                firstName: 'John',
                lastName: 'Doe',
                email: 'prueba@test.com'
              }
            },
            customization: {
              visual: {
                style: {
                  theme: "dark",
                },
              },
              paymentMethods: {
                creditCard: "all",
                debitCard: "all",
                atm: "all",
                maxInstallments: 1
              },
            },
            callbacks: {
              onReady: () => {
                console.log('Payment Brick listo.');
              },
              onSubmit: async ({ selectedPaymentMethod, formData }) => {
                return new Promise(async (resolve, reject) => {
                  try {
                    const response = await api.post(`/payments/process-payment/${route.query.paymentOrderId}`, {
                      formData: formData, // Enviar formData en lugar de cardFormData
                      selectedPaymentMethod: selectedPaymentMethod,
                    });
  
                    if (response.data?.status === 'approved') {
                      $q.notify({
                        type: 'positive',
                        message: 'Pago realizado con éxito. Redirigiendo...',
                        timeout: 2000,
                      });
                      router.push({ name: 'PaymentSuccess', query: { paymentOrderId: route.query.paymentOrderId } });
                      resolve();
                    } else {
                      paymentError.value = response.data?.error || 'Error al procesar el pago.';
                      reject();
                    }
                  } catch (error) {
                    console.error('Error al procesar el pago:', error);
                    paymentError.value = 'Error de conexión al procesar el pago.';
                    reject();
                  }
                });
              },
              onError: (error) => {
                console.error('Error al pagar:', error);
                paymentError.value = 'Ocurrió un error al intentar pagar. Por favor, intenta nuevamente.';
              },
            },
          });
        } catch (error) {
          console.error('Error al inicializar Payment Brick:', error);
          paymentError.value = 'Error al cargar la pasarela de pago.';
        }
      };
  
      const goBack = () => {
        router.back();
      };
  
      return {
        initPoint,
        totalAmount,
        paymentError,
        goBack,
      };
    },
  };
  </script>

<style scoped>
#mercadopago-bricks-container {
  margin-bottom: 20px;
}

.home {
  background-color: #dddddd;
}

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
  width: 60px; /* Ajusta el tamaño del logo */
  height: 60px;
}

.q-card {
background-image: url(../assets/texturafondo.png);
background-size: cover;
max-width: 400px;
margin: auto;
color: #fff; /* Texto blanco para visibilidad */
border-radius: 8px; /* Bordes redondeados */
box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2); /* Sombra para destacar */
}

.text-primary {
color: #4caf50; /* Verde primario */
}

.q-card-section {
padding: 16px;
}
</style>