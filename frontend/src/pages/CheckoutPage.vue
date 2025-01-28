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
import api from "../api";

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

    const commission = ref(4); // Comision porcentaje
    const subtotal = ref(reservationDetails.value.price + (commission.value*reservationDetails.value.price/100));

    const confirmReservation = async () => {
  try {
    $q.loading.show();

    const reservationData = {
      court_id: reservationDetails.value.courtId,
      reservation_date: reservationDetails.value.date,
      start_time: reservationDetails.value.time,
      end_time: calculateEndTime(
        reservationDetails.value.time,
        reservationDetails.value.duration
      ),
      total_price: parseFloat(reservationDetails.value.price),
      club_id: reservationDetails.value.clubId,
    };

    const response = await api.post("/reservations", reservationData);

    // Verifica si la respuesta es correcta
    if (response.status === 200 && response.data) {
      const match = response.data.match?.[0]; // Obtener el primer elemento de la lista de matches

      if (match?.id) {
        $q.notify({
          type: "positive",
          message: response.data.message || "Reserva confirmada exitosamente.",
        });

        // Redirigir al detalle del partido
        router.push(`/player/match/${match.id}`);
      } else {
        throw new Error("No se pudo obtener el ID del partido.");
      }
    } else {
      throw new Error(response.data.message || "Error desconocido.");
    }
  } catch (error) {
    console.error("Error al confirmar la reserva:", error);
    $q.notify({
      type: "negative",
      message: error.response?.data?.detail || "Error al confirmar la reserva.",
    });
  } finally {
    $q.loading.hide();
  }
};


    const calculateEndTime = (startTime, duration) => {
      const [hours, minutes] = startTime.split(":").map(Number);
      const totalMinutes = hours * 60 + minutes + Number(duration);
      const endHours = Math.floor(totalMinutes / 60);
      console.log(endHours)
      const endMinutes = totalMinutes % 60;
      console.log(endMinutes)
      console.log(`${String(endHours).padStart(2, "0")}:${String(endMinutes).padStart(2, "0")}`);
      return `${String(endHours).padStart(2, "0")}:${String(endMinutes).padStart(2, "0")}`;
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
