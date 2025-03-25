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
            <h3 class="text-white">Pago</h3>
          </q-card-section>
          <q-card-section>
            <p><strong>Total a pagar:</strong> ${{ total }}</p>
            <div id="stripe-payment-element"></div>
          </q-card-section>
          <q-card-actions align="right">
            <q-btn
              :label="`PAGAR $${total.toFixed(2)}`"
              color="green"
              class="full-width"
              @click="confirmPayment"
            />
          </q-card-actions>
        </q-card>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useQuasar } from "quasar";
import { loadStripe } from "@stripe/stripe-js";
import { endtime_calculate } from "src/helpers/hourUtils";
import { createNotification } from "src/services/api/notifications";
import api from "../services/api";

export default {
  setup() {
    const route = useRoute();
    const router = useRouter();
    const $q = useQuasar();

    const total = ref(parseFloat(route.query.total));
    const reservationDetails = ref(JSON.parse(route.query.reservationDetails));
    const paymentOption = ref(route.query.paymentOption);
    const selectedProducts = ref(JSON.parse(route.query.selectedProducts));
    const isPublicMatch = ref(route.query.isPublicMatch === 'true');

    const stripe = ref(null);
    const elements = ref(null);
    const clientSecretRef = ref(null);

    const getClientSecret = async (amount) => {
      try {
        const amountInCents = Math.round(amount * 100);
        const response = await api.post("payments/create-payment-intent", {
          payment_order_id: reservationDetails.value.payment_order_id,
          amount: amountInCents,
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

        let amountToPay = paymentOption.value === "total" ? total.value : total.value / 4;
        clientSecretRef.value = await getClientSecret(amountToPay);

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

    const confirmPayment = async () => {
      try {
        $q.loading.show();

        // 1. Enviar la información de pago del usuario
        const { error: submitError } = await elements.value.submit();

        if (submitError) {
          console.error("Error al enviar la información de pago:", submitError);
          $q.notify({
            type: "negative",
            message: `Error al enviar la información de pago: ${submitError.message}`,
          });
          $q.loading.hide();
          return;
        }

        // 2. Confirmar el pago
        const { paymentIntent, error } = await stripe.value.confirmPayment({
          elements: elements.value,
          clientSecret: clientSecretRef.value,
          redirect: "if_required",
        });

        if (error) {
          console.error("Error al confirmar el pago:", error);
          $q.notify({
            type: "negative",
            message: `Error al confirmar el pago: ${error.message}`,
          });
          $q.loading.hide();
          return;
        }

        if (paymentIntent.status === "succeeded") {
          const paymentMethod = paymentIntent.payment_method;
          await api.post("/payments/process-stripe-payment", {
            payment_order_id: reservationDetails.value.payment_order_id,
            payment_method: paymentMethod,
            payment_status: "succeeded",
            transaction_id: paymentIntent.id,
            is_full_payment: paymentOption.value === "total",
          });

          await processPaymentSuccess();
        } else {
          $q.notify({
            type: "negative",
            message: "Error al confirmar el pago.",
          });
        }
      } catch (error) {
        console.error("Error al confirmar el pago:", error);
        $q.notify({
          type: "negative",
          message: "Error al confirmar el pago.",
        });
      } finally {
        $q.loading.hide();
      }
    };


    const processPaymentSuccess = async () => {
      try {
        await confirmReservation();
      } catch (error) {
        console.error("Error al procesar pago exitoso:", error);
        $q.notify({
          type: "negative",
          message: "Error al procesar el pago.",
        });
      }
    };

    const confirmReservation = async () => {
      try {
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
          end_time: endtime_calculate( reservationDetails.value.time, reservationDetails.value.duration ),
          total_price: total.value,
          pay_total: paymentOption.value === "total",
          club_commission: 0,
          player_commission: 0,
          additional_items: additionalItems,
          payment_order_id: reservationDetails.value.payment_order_id,
          is_public_match: isPublicMatch.value,
        };

        const response = await api.post("/reservations", reservationData);
        const club_user_id = response.data.club_user_id;

        // Notificación para el club
        await createNotification({
            user_id: club_user_id,
            title: "Nueva Reserva",
            message: `Se ha realizado una nueva reserva para el ${reservationDetails.value.date}. a las ${reservationDetails.value.time}`,
          });

        router.push(`/player/match/${response.data.match_id}`);
        $q.notify({
            type: "positive",
            message: "Reserva y pago confirmados.",
          });
      } catch (error) {
        console.error("Error al confirmar la reserva:", error);
        $q.notify({
          type: "negative",
          message: "Error al confirmar la reserva.",
        });
      }
    };

    const goBack = () => {
      router.back()
    }

    onMounted(async () => {
      await setupStripe();
    });

    return {
      total,
      confirmPayment,
      goBack,
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
  background-image: url(src/assets/texturafondo.png);
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