<template>
  <q-layout view="hHh lpR fFf" class="bg-dark text-white">
    <q-header elevated class="bg-primary text-white">
      <q-toolbar>
        <q-toolbar-title>Confirmar Reserva</q-toolbar-title>
        <q-btn flat round icon="arrow_back" @click="goBack" label="REGRESAR" />
      </q-toolbar>
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
            <p><strong>Horario:</strong> {{ reservationDetails.time }}</p>
            <p><strong>Duración:</strong> {{ reservationDetails.duration }} minutos</p>
            <p><strong>Precio:</strong> ${{ reservationDetails.price.toFixed(2) }}</p>
            <p><strong>Comisión:</strong> {{ commission }}%</p>
            <p><strong>Subtotal:</strong> ${{ subtotal.toFixed(2) }}</p>
          </q-card-section>

          <q-card-actions align="right">
            <q-btn label="Confirmar y Pagar" color="green" @click="confirmReservation" />
          </q-card-actions>
        </q-card>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script>
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useQuasar } from "quasar";
import { createEspiralPayment } from "../helpers/espiralUtils"; // Importa la utilidad

export default {
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
    };
  },
};
</script>

<style scoped>
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