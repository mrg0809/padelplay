<template>
    <q-layout view="hHh lpR fFf" class="bg-dark text-white">
      <!-- Header -->
      <q-header elevated class="bg-primary text-white">
        <q-toolbar>
          <q-toolbar-title>Inscripción al Torneo</q-toolbar-title>
          <q-btn flat round icon="arrow_back" @click="goBack" label="REGRESAR" />
        </q-toolbar>
      </q-header>
  
      <!-- Page Content -->
      <q-page-container>
        <q-page class="q-pa-md">
          <q-card class="q-mb-md">
            <q-card-section>
              <h4>{{ tournament.name }}</h4>
              <p><strong>Fecha:</strong> {{ tournament.start_date }}</p>
              <p><strong>Hora:</strong> {{ tournament.start_time }}</p>
              <p><strong>Club:</strong> {{ tournament.club_name }}</p>
              <p><strong>Precio por pareja:</strong> ${{ tournament.price }}</p>
              <p><strong>Comisión:</strong> ${{ commission }}</p>
              <p><strong>Total a pagar:</strong> ${{ totalPrice }}</p>
            </q-card-section>
          </q-card>
  
          <!-- Player Information -->
          <q-card class="q-mb-md">
            <q-card-section>
              <h5>Jugadores</h5>
              <p><strong>Jugador 1:</strong> {{ player1Name }}</p>
              <q-input
                v-model="player2Email"
                label="Email del Jugador 2"
                type="email"
                outlined
                dense
                class="q-mb-md"
                required
              />
              <q-input
                v-model="player2EmailConfirm"
                label="Confirmar Email del Jugador 2"
                type="email"
                outlined
                dense
                class="q-mb-md"
                required
              />
            </q-card-section>
          </q-card>
  
          <q-btn
            label="Inscribir Pareja"
            color="primary"
            class="full-width q-mt-md"
            @click="registerTeam"
          />
        </q-page>
      </q-page-container>
    </q-layout>
  </template>
  
  <script>
  import { ref, onMounted } from "vue";
  import { useRoute, useRouter } from "vue-router";
  import { useQuasar } from "quasar";
  import api from "../../api";
  
  export default {
    setup() {
      const route = useRoute();
      const router = useRouter();
      const $q = useQuasar();
  
      const tournament = ref({
        name: route.query.tournamentName || "Torneo",
        start_date: route.query.startDate || "",
        start_time: route.query.startTime || "",
        price: route.query.pricePerPair || 0,
        club_name: route.query.clubName || "Club",
      });
  
      const player1Name = ref("");
      const player2Email = ref("");
      const player2EmailConfirm = ref("");
      const commission = ref(10); // Comisión fija en dólares
      const totalPrice = ref(tournament.value.price + commission.value);
  
      const fetchPlayer1Name = () => {
        const token = localStorage.getItem("token");
        if (token) {
          const base64Url = token.split(".")[1];
          const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
          const payload = JSON.parse(atob(base64));
          player1Name.value = payload.email || "Jugador 1";
        }
      };
  
      const registerTeam = async () => {
        if (player2Email.value !== player2EmailConfirm.value) {
          $q.notify({ type: "negative", message: "Los emails del Jugador 2 no coinciden." });
          return;
        }
  
        try {
          const response = await api.post(`/tournaments/${route.query.tournamentId}/register-team`, {
            player1: player1Name.value,
            player2: player2Email.value,
            totalPrice: totalPrice.value,
          });
  
          if (response.status === 200) {
            $q.notify({ type: "positive", message: "Pareja registrada exitosamente." });
            router.push("/dashboard/player");
          } else {
            throw new Error(response.data.message || "Error al registrar la pareja.");
          }
        } catch (err) {
          console.error("Error al registrar pareja:", err.message);
          $q.notify({ type: "negative", message: `Error: ${err.message}` });
        }
      };
  
      const goBack = () => {
        router.back();
      };
  
      onMounted(() => {
        fetchPlayer1Name();
      });
  
      return {
        tournament,
        player1Name,
        player2Email,
        player2EmailConfirm,
        commission,
        totalPrice,
        registerTeam,
        goBack,
      };
    },
  };
  </script>
  
  <style scoped>
  .full-width {
    width: 100%;
  }
  .q-card {
    background-color: #1e1e1e !important;
    color: white !important;
  }
  </style>
  