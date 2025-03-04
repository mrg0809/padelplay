<template>
  <q-layout view="hHh lpR fFf" class="bg-dark text-white">
    <q-header elevated class="text-white">
      <div class="header-content">
        <div class="greeting">
          <img src="/src/assets/padelplay.png" alt="Logo" class="logo-icon" />
        </div>
        <div class="header-icons">
          <NotificationBell />
        </div>
      </div>
      <BannerPromoScrolling />
    </q-header>

    <q-page-container>
      <q-page class="q-pa-md">
        <q-card class="text-white">
          <q-card-section>
            <h3 class="text-white">Resumen de Reserva</h3>
          </q-card-section>
          <q-card-section>
            <p><strong>Club:</strong> {{ reservationDetails.clubName }}</p>
            <p><strong>Cancha:</strong> {{ reservationDetails.courtName }}</p>
            <p><strong>Fecha:</strong> {{ reservationDetails.date }}</p>
            <p><strong>Horario:</strong> {{ reservationDetails.time }} hrs.</p>
            <p><strong>Duración:</strong> {{ reservationDetails.duration }} minutos</p>
            <p><strong>Precio:</strong> ${{ reservationDetails.price.toFixed(2) }}</p>
            <p><strong>Subtotal:</strong> ${{ subtotal.toFixed(2) }}</p>
            <p><strong>Productos:</strong></p>
            <ul>
              <li v-for="item in selectedProducts" :key="item.product.id">
                {{ item.product.name }} x {{ item.quantity }} - ${{ (item.product.price * item.quantity).toFixed(2) }}
              </li>
            </ul>
            <p><strong>Total:</strong> ${{ total.toFixed(2) }}</p>
          </q-card-section>

          <q-card-section>
            <q-toggle v-model="isPublicMatch" label="Partido Público" />
            <q-option-group v-model="paymentOption" :options="paymentOptions" />
          </q-card-section>

          <q-card-actions align="right">
            <q-btn label="Agregar Productos" color="primary" @click="showProductDialog" />
            <q-btn label="Confirmar y Pagar" color="green" @click="confirmReservation" />
          </q-card-actions>
        </q-card>
      </q-page>
    </q-page-container>

    <q-dialog v-model="productDialog">
      <q-card>
        <q-card-section>
          <div v-for="product in products" :key="product.id" class="q-mb-md">
            <q-item>
              <q-item-section>
                <q-item-label>{{ product.name }} - ${{ product.price.toFixed(2) }}</q-item-label>
              </q-item-section>
              <q-item-section side>
                <q-input v-model="productQuantities[product.id]" type="number" min="0" />
              </q-item-section>
            </q-item>
          </div>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn label="Aceptar" color="primary" @click="addProductToOrder" />
          <q-btn label="Cancelar" color="grey-dark" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-layout>
</template>

<script>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useQuasar } from "quasar";
import { createEspiralPayment } from "../helpers/espiralUtils"; // Importa la utilidad
import { getProductsByClub } from "src/services/supabase/products";
import NotificationBell from "../components/NotificationBell.vue";
import BannerPromoScrolling from "../components/BannerPromoScrolling.vue";


export default {
  components: {
    NotificationBell,
    BannerPromoScrolling,
  },
  setup() {
    const route = useRoute();
    const router = useRouter();
    const $q = useQuasar();

    const reservationDetails = ref({
      clubId: route.query.clubId || "",
      clubName: route.query.clubName || "Club no especificado",
      courtId: route.query.courtId || "",
      courtName: route.query.courtName || "Cancha no especificada",
      date: route.query.date || "Fecha no especificada",
      time: route.query.time || "Hora no especificada",
      duration: route.query.duration || 0,
      price: parseFloat(route.query.price) || 0,
    });

    const commission = ref(4); // Comisión porcentaje
    const subtotal = ref(
      reservationDetails.value.price + (commission.value * reservationDetails.value.price) / 100
    );

    const products = ref([]);
    const productQuantities = ref({});
    const selectedProducts = ref([]);
    const productDialog = ref(false);
    const isPublicMatch = ref(false);
    const paymentOption = ref("partial");
    const paymentOptions = ref([
      { label: "Pagar mi parte", value: "partial" },
      { label: "Pagar el total", value: "total" },
    ]);

    const total = computed(() => {
      let productTotal = selectedProducts.value.reduce((acc, item) => acc + (item.product.price * item.quantity), 0);
      return subtotal.value + productTotal;
    });

    onMounted(async () => {
      products.value = await getProductsByClub(reservationDetails.value.clubId);
      products.value.forEach(product => productQuantities.value[product.id] = 0);
    });

    const showProductDialog = () => {
      productDialog.value = true;
    };

    const addProductToOrder = () => {
      selectedProducts.value = products.value.filter(product => productQuantities.value[product.id] > 0).map(product => ({
        product: product,
        quantity: productQuantities.value[product.id]
      }));
      productDialog.value = false;
    };

    const confirmReservation = async () => {
      try {
        $q.loading.show();

        // Datos del pago
        const paymentData = {
          cardHolder: {
            name: "Nombre del titular", // Obtén estos datos del formulario
            email: "titular@example.com",
            phone: "+521234567890",
          },
          address: {
            country: "MX", // Código de país
            state: "JA", // Estado
            city: "Zapopan", // Ciudad
            numberExt: "123", // Número exterior
            numberInt: "", // Número interior (opcional)
            zipCode: "45180", // Código postal
            street: "Calle Falsa 123", // Calle
          },
          transaction: {
            items: [
              {
                name: "Reserva de cancha",
                price: subtotal.value.toFixed(2),
                description: `Reserva en ${reservationDetails.value.clubName}`,
                quantity: 1,
              },
            ],
            total: subtotal.value.toFixed(2),
            currency: "MXN",
          },
          linkDetails: {
            name: "Reserva de cancha",
            email: "cliente@example.com",
            reusable: false,
            enableCard: true,
            enableReference: true,
            securityType3D: true,
            bank: 1, // 1 para tarjeta, 2 para transferencia
          },
          webhook: {
            redirectUrl: `${window.location.origin}/payment-success`, // URL de éxito
            redirectErrorUrl: `${window.location.origin}/payment-error`, // URL de error
            backPage: `${window.location.origin}/`, // Página de regreso
            redirectData: {
              url: `${window.location.origin}/api/webhook/espiral`, // URL para guardar datos
              redirectMethod: "POST",
            },
            redirectErrorData: {
              url: `${window.location.origin}/api/webhook/espiral`, // URL para guardar datos de error
              redirectMethod: "POST",
            },
          },
          metadata: {
            reservationId: reservationDetails.value.clubId, // Metadatos adicionales
          },
        };

        // Crear el pago a través de tu backend
        const espiralResponse = await createEspiralPayment(paymentData);

        // Redirigir al usuario a la página de pago de Espiral
        window.location.href = espiralResponse.url;
      } catch (error) {
        console.error("Error al confirmar la reserva:", error);
        $q.notify({
          type: "negative",
          message: "Error al confirmar la reserva.",
        });
      } finally {
        $q.loading.hide();
      }
    };

    const goBack = () => {
      router.back();
    };

    return {
      reservationDetails,
      commission,
      subtotal,
      confirmReservation,
      goBack,
      products,
      productQuantities,
      selectedProducts,
      productDialog,
      isPublicMatch,
      paymentOption,
      paymentOptions,
      total,
      showProductDialog,
      addProductToOrder,
    };
  },
};
</script>

<style scoped>

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