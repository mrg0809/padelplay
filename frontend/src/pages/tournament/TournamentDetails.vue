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
        <div v-if="loading" class="text-center q-pa-xl">
          <q-spinner-dots color="primary" size="xl" />
          <p class="q-mt-md">Cargando detalles del torneo...</p>
        </div>

        <div v-else-if="tournament">
          <q-card>
            <q-card-section>
              <h4 class="q-mt-none q-mb-md">{{ tournament.name }}</h4>
              <p>
                <strong><q-icon name="mdi-calendar-start" class="q-mr-xs" />Inicio:</strong>
                {{ tournament.start_date }} - {{ tournament.start_time }} hrs.
              </p>
              <p>
                <strong><q-icon name="mdi-domain" class="q-mr-xs" />Club:</strong> {{ tournament.clubs?.name }}
              </p>
              <p>
                <strong><q-icon name="mdi-trophy-variant-outline" class="q-mr-xs" />Categoría:</strong>
                {{ tournament.category }}
              </p>
              <p>
                <strong><q-icon name="mdi-gender-male-female" class="q-mr-xs" />Género:</strong>
                {{ tournament.gender }}
              </p>
              <p>
                <strong><q-icon name="mdi-cash-multiple" class="q-mr-xs" />Precio por Pareja:</strong>
                ${{ tournament.price_per_pair?.toFixed(2) || 'N/A' }}
              </p>
              <p>
                <strong><q-icon name="mdi-gift-outline" class="q-mr-xs" />Premios (Valor):</strong>
                ${{ tournament.prize || 'N/A' }}
              </p>

              <div v-if="enrolledPlayers.length > 0" class="q-mt-md">
                <p>
                  <strong><q-icon name="account-group-outline" class="q-mr-xs" />Jugadores Inscritos:</strong>
                </p>
                <div class="q-gutter-xs row items-center">
                  <template v-for="team in enrolledPlayers" :key="team.player1?.user_id + '-' + team.player2?.user_id">
                    <q-avatar
                      v-if="team.player1"
                      size="48px"
                      color="white"
                      text-color="black"
                      class="overlapping"
                    >
                      <img v-if="team.player1.photo_url" :src="team.player1.photo_url" :alt="team.player1.user_id" />
                      <span v-else>{{ getInitials(team.player1.user_id) }}</span>
                    </q-avatar>
                    <q-avatar
                      v-if="team.player2"
                      size="48px"
                      color="white"
                      text-color="black"
                      class="overlapping"
                    >
                      <img v-if="team.player2.photo_url" :src="team.player2.photo_url" :alt="team.player2.user_id" />
                      <span v-else>{{ getInitials(team.player2.user_id) }}</span>
                    </q-avatar>
                  </template>
                </div>
              </div>

              <div v-if="!isUserEnrolled" class="q-mt-md">
                <q-btn
                  color="primary"
                  label="Elige tu Pareja"
                  icon-right="mdi-account-search"
                  @click="showPlayerSearchDialog = true"
                  class="full-width"
                  size="md"
                  push
                />
                <p v-if="selectedPartner" class="q-mt-sm">
                  Pareja Seleccionada: {{ selectedPartner.first_name }} {{ selectedPartner.last_name }}
                </p>
              </div>
            </q-card-section>

            <q-card-actions align="center" class="q-pa-md">
              <q-btn
                v-if="!isUserEnrolled && selectedPartner"
                label="Inscribir Pareja"
                color="green"
                icon-right="mdi-pencil-plus-outline"
                class="full-width"
                size="lg"
                push
                @click="handleEnrollment"
                :disable="!tournament"
                title="Inscribirse al torneo pagando la mitad del costo de pareja"
              />
            </q-card-actions>
          </q-card>
        </div>
        <div v-else class="q-pa-md text-center text-negative">
          <q-icon name="mdi-alert-circle-outline" size="lg" />
          <p class="q-mt-md">No se pudieron cargar los detalles del torneo.</p>
          <q-btn flat label="Volver" @click="goBack" />
        </div>
      </q-page>
    </q-page-container>
    <PlayerNavigationMenu />

    <PlayerSearch v-model:modelValue="showPlayerSearchDialog" @playerSelected="onPartnerSelected" />
  </q-layout>
</template>

<script setup>
  import { ref, onMounted, computed } from "vue";
  import { useRoute, useRouter } from "vue-router";
  import { useQuasar } from "quasar";
  import { useSummaryStore } from 'src/stores/summaryStore';
  import { useUserStore } from "src/stores/userStore";
  import { fetchTournamentDetails, fetchTournamentPlayers } from "src/services/supabase/tournaments";
  import PlayerNavigationMenu from "src/components/PlayerNavigationMenu.vue";
  import BannerPromoScrolling from "src/components/BannerPromoScrolling.vue";
  import NotificationBell from "src/components/NotificationBell.vue";
  import PlayerSearch from "src/components/PlayerSearch.vue";

  const route = useRoute();
  const router = useRouter();
  const $q = useQuasar();
  const summaryStore = useSummaryStore();
  const tournament = ref(null);
  const loading = ref(false);
  const userStore = useUserStore();

  const tournamentId = route.params.tournamentId;

  // Nuevo estado para controlar el diálogo y la pareja seleccionada
  const showPlayerSearchDialog = ref(false);
  const selectedPartner = ref(null);
  const enrolledPlayers = ref([])

  const loadData = async () => {
    if (!tournamentId) {
      console.error("ID del torneo no encontrado en los parámetros de la ruta.");
      $q.notify({ type: 'negative', message: 'No se pudo identificar el torneo.' });
      loading.value = false;
      return;
    }

    loading.value = true;
    tournament.value = null;
    enrolledPlayers.value = [];

    try {
      const data = await fetchTournamentDetails(tournamentId);

      if (!data || typeof data !== 'object') {
        console.warn(`No se encontraron datos para el torneo ID ${tournamentId} o el formato es incorrecto.`);
        throw new Error("Torneo no encontrado o datos inválidos.");
      }

      tournament.value = data[0];
      console.log("Detalles del torneo cargados:", tournament.value);

      const playersData = await fetchTournamentPlayers(tournamentId);
      enrolledPlayers.value = playersData;
      console.log("Jugadores inscritos:", enrolledPlayers.value);

    } catch (error) {
      console.error("Error al cargar detalles del torneo (desde loadData):", error);
      tournament.value = null;
      $q.notify({
        type: "negative",
        message: error?.message || "Error al cargar la información del torneo.",
      });
    } finally {
      loading.value = false;
    }
  };

  const handleEnrollment = () => {
    if (!tournament.value || !tournament.value.price_per_pair || !selectedPartner.value) {
      console.error("Datos del torneo incompletos o precio/pareja no disponible o pareja no seleccionada", tournament.value, selectedPartner.value);
      $q.notify({ type: 'negative', message: 'No se puede procesar la inscripción, falta información del torneo o la pareja.' });
      return;
    }

    const tournamentData = tournament.value;

    const enrollmentPrice = (tournamentData.price_per_pair || 0) / 2;

    const summaryProps = {
      summaryTitle: 'Resumen de Inscripción a Torneo',
      itemDetails: [
        { label: 'Torneo', value: tournamentData.name || 'No especificado' },
        { label: 'Club', value: tournamentData.clubName || 'No especificado' },
        { label: 'Fecha Inicio', value: tournamentData.start_date || 'No especificada' },
        { label: 'Categoría', value: tournamentData.category || 'No especificada' },
        { label: 'Género', value: tournamentData.gender || 'No especificado' },
        { label: 'Precio Inscripción (Individual)', value: `$${enrollmentPrice.toFixed(2)}` },
        { label: 'Precio Total (Pareja)', value: `$${tournamentData.price_per_pair.toFixed(2)}` },
        { label: 'Pareja', value: `${selectedPartner.value.first_name} ${selectedPartner.value.last_name}` }, // Agregamos la pareja
      ],
      baseData: {
        clubId: tournamentData.clubId,
        price: enrollmentPrice,
        participants: 2,
        type: 'tournament',
        id: tournamentData.id,
        recipient_user_id: tournamentData.club_user_id || null,
        player2_email: selectedPartner.value.email,
      },
      allowPaymentSplit: true,
      showPublicToggle: false,
      commissionRate: 4,
      extraData: {
        tournamentName: tournamentData.name,
        tournament_name: tournamentData.name,
        prize: tournamentData.prize,
        pricePerPair: tournamentData.price_per_pair,
        partnerId: selectedPartner.value.user_id,
        player2_email: selectedPartner.value.email,
      }
    };

    summaryStore.setSummaryDetails(summaryProps);
    console.log('Datos del resumen de TORNEO guardados en Pinia:', summaryProps);

    router.push({ name: 'OrderSummary' });
  };

  const goBack = () => {
    router.back();
  };

  const onPartnerSelected = (player) => {
    selectedPartner.value = player;
    showPlayerSearchDialog.value = false;
  };

  const isUserEnrolled = computed(() => {
    if (!enrolledPlayers.value || !userStore.userId) {
      return false;
    }
    return enrolledPlayers.value.some(team => team.player1?.user_id === userStore.userId || team.player2?.user_id === userStore.userId);
  });

  const getInitials = (userId) => {
    if (!userId) return '??';
    const parts = userId.split('-');
    if (parts.length > 0) {
      return parts[0].substring(0, 2).toUpperCase();
    }
    return userId.substring(0, 2).toUpperCase();
  };

  onMounted(() => {
    loadData();
  });
</script>

  
<style scoped>
  .club-logo {
    width: 300px;
    border-radius: 8px;
    margin-bottom: 16px;
  }

  .logo-icon {
    width: 60px;
    height: 60px;
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
    .q-layout {
      min-height: 100vh;
    }
    
    .q-card {
      background-image: url("../../assets/texturafondo.png");
      background-size: cover;
      max-width: 400px;
      margin: auto;
      color: #fff; 
      border-radius: 8px; 
      box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2); 
      }
    
    ul {
      padding-left: 1.2rem;
    }
    
    ul li {
      list-style-type: disc;
    }

  h4 { margin-top: 0; margin-bottom: 16px; }
  p { margin-bottom: 0.6rem; }
  p strong { color: #b3e5fc; }

  .overlapping {
    position: relative;
    margin-left: -18px;
    border: 1px solid black;
  }

  .q-avatar:first-child {
    margin-left: 0;
  }

</style>
  