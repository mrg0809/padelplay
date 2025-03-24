<template>
  <q-layout view="hHh lpR fFf" class="bg-dark text-white">
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
            <q-btn label="Confirmar Pago" color="green" @click="confirmPayment" />
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
          end_time: `${
            parseInt(reservationDetails.value.time.split(":")[0]) +
            reservationDetails.value.duration / 60
          }:00`,
          total_price: total.value,
          pay_total: paymentOption.value === "total",
          club_commission: 0,
          player_commission: 0,
          additional_items: additionalItems,
          payment_order_id: reservationDetails.value.payment_order_id,
        };

        const response = await api.post("/reservations", reservationData);
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

    onMounted(async () => {
      await setupStripe();
    });

    return {
      total,
      confirmPayment,
    };
  },
};
</script>