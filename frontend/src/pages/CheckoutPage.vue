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
            <div id="stripe-payment-element">
            </div>
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
    <PlayerNavigationMenu />
  </q-layout>
</template>

<script>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useQuasar } from "quasar";
import { getProductsByClub } from "src/services/supabase/products";
import { loadStripe } from "@stripe/stripe-js";
import api from "../services/api";
import NotificationBell from "../components/NotificationBell.vue";
import BannerPromoScrolling from "../components/BannerPromoScrolling.vue";
import PlayerNavigationMenu from "src/components/PlayerNavigationMenu.vue";



export default {
  components: {
    NotificationBell,
    BannerPromoScrolling,
    PlayerNavigationMenu,
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

    const stripe = ref(null);
    const elements = ref(null);
    const clientSecretRef = ref(null);


    const getClientSecret = async (reservationData, amount) => {
      try {
        const response = await api.post("payments/create-payment-intent", {
          payment_order_id: reservationData.payment_order_id,
          amount: amount,
        });
        return response.data.clientSecret;
      } catch (error) {
        console.error("Error al obtener clientSecret:", error);
        $q.notify({
          type: "negative",
          message: "Error al obtener clientSecret.",
        });
        return null;
      }
    };

    const setupStripe = async () => {
      try {
        stripe.value = await loadStripe(
          import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY
        );

        const additionalItems = selectedProducts.value.map((item) => ({
          name: item.product.name,
          price: item.product.price,
          quantity: item.quantity,
        }));

        const reservationData = {
          club_id: reservationDetails.value.clubId,
          court_id: reservationDetails.value.courtId,
          reservation_date: reservationDetails.value.date,
          start_time: reservationDetails.value.time,
          end_time: `${
            parseInt(reservationDetails.value.time.split(":")[0]) +
            reservationDetails.value.duration / 60
          }:00`,
          total_price: total.value,
          pay_total: paymentOption.value === "total",
          club_commission: 0,
          player_commission: 0,
          additional_items: additionalItems,
        };

        const response = await api.post("/reservations", reservationData);
        reservationData.payment_order_id = response.data.payment_order_id;

        const amount =
          paymentOption.value === "total"
            ? Math.round(total.value * 100)
            : Math.round((total.value / 4) * 100);

        clientSecretRef.value = await getClientSecret(reservationData, amount);

        if (clientSecretRef.value) {
          elements.value = stripe.value.elements({ clientSecret: clientSecretRef.value });
          const paymentElement = elements.value.create("payment");
          paymentElement.mount("#stripe-payment-element");
        }
      } catch (error) {
        console.error("Error al cargar Stripe:", error);
        $q.notify({
          type: "negative",
          message: "Error al cargar Stripe.",
        });
      }
    };

    onMounted(async () => {
      products.value = await getProductsByClub(reservationDetails.value.clubId);
      products.value.forEach(product => productQuantities.value[product.id] = 0);
      await setupStripe();
    });


    const confirmReservation = async () => {
      try {
        $q.loading.show();

        const additionalItems = selectedProducts.value.map((item) => ({
          name: item.product.name,
          price: item.product.price,
          quantity: item.quantity,
        }));

        const reservationData = {
          club_id: reservationDetails.value.clubId,
          court_id: reservationDetails.value.courtId,
          reservation_date: reservationDetails.value.date,
          start_time: reservationDetails.value.time,
          end_time: `${
            parseInt(reservationDetails.value.time.split(":")[0]) +
            reservationDetails.value.duration / 60
          }:00`,
          total_price: total.value,
          pay_total: paymentOption.value === "total",
          club_commission: 0, // Ajusta según tu lógica
          player_commission: 0, // Ajusta según tu lógica
          additional_items: additionalItems,
        };

        const response = await api.post("/reservations", reservationData);

        const amount =
          paymentOption.value === "total"
            ? Math.round(total.value * 100)
            : Math.round((total.value / 4) * 100);

        const clientSecretResponse = await api.post("payments/create-payment-intent", {
          payment_order_id: response.data.payment_order_id,
          amount: amount,
        });

        const { paymentIntent, error } = await stripe.value.confirmPayment({
          elements: elements.value,
          clientSecret: clientSecretResponse.data.clientSecret,
          redirect: "if_required",
        });

        if (error) {
          console.error("Error al confirmar el pago:", error);
          $q.notify({
            type: "negative",
            message: `Error al confirmar el pago: ${error.message}`,
          });
          return;
        }

        if (paymentIntent.status === "succeeded") {
          $q.notify({
            type: "positive",
            message: "Reserva y pago confirmados.",
          });
          router.push(`/match/${response.data.match.id}`);
        } else {
          $q.notify({
            type: "negative",
            message: "Error al confirmar el pago.",
          });
        }
      } catch (error) {
        console.error("Error al confirmar la reserva:", error);
        $q.notify({
          type: "negative",
          message: `Error al confirmar la reserva: ${error.message}`,
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