<template>
  <q-layout view="hHh lpR fFf" class="bg-dark text-white">
    <q-header elevated class="text-white">
        <div class="header-content">
          <div class="greeting">
            <img src="/src/assets/padelplay.png" alt="Logo" class="logo-icon" />
          </div>
      <!-- Iconos de la derecha -->
          <div class="header-icons">
            <NotificationBell />
            <PlayerTopMenu />
          </div>
        </div>
        <BannerPromoScrolling />
      </q-header>

    <q-page-container>
      <q-page class="q-pa-md">
        <div v-if="loading" class="text-center">
          <q-spinner-dots color="primary" size="lg" />
        </div>
        <div v-else>
          <q-card class="text-white q-pa-md match-card">
            <q-card-section>
              <div class="row items-center" style="position: relative; width: 100%; margin-bottom: 20px;">
                <q-btn flat @click="onMenu" style="position: absolute; left: 0;">
                  <q-icon name="o_share" size="lg"/>
                </q-btn>
                <h3 class="text-h5 text-white" style="flex: 1; margin: 0; text-align: center;">Reserva</h3>
                <div class="row" style="position: absolute; right: 0;">
                  <q-btn flat @click="openChat">
                    <q-icon name="o_chat" size="lg"/>
                  </q-btn>
                </div>
              </div>
                <p>
                Juegas en el club {{ matchDetails.club_name || "No disponible" }}
                <q-btn size="xs" flat round color="yellow" @click="goToMaps"><q-icon name="o_location_on" size="xs"/></q-btn>
                el dia {{ formatDate(matchDetails.match_date) }} a
                las {{ matchDetails.match_time.slice(0, 5) }} hrs. En la cancha {{ matchDetails.court_name || "No disponible" }}.
                </p>
                <p>Categoria jugadores: Abierto<br>
                   Tipo de partido: Cerrado<br>
                   Costo: $1215 PP: $405 </p>
            </q-card-section>
          </q-card>

          <q-card class="match-card text-white q-pa-md">
            <!-- Representación de la cancha -->
            <q-card-section class="q-mt-md">
              <h3 class="text-center text-white">Jugadores</h3>
              <div class="court-container">
                <div class="court">
                  <!-- Jugadores o botones de agregar -->
                  <div class="player team1-player1">
                    <div v-if="team1[0]">
                      {{ team1[0] || "Jugador 1 Equipo 1" }}
                    </div>
                    <q-btn
                      v-else
                      flat
                      round
                      icon="o_person_add"
                      @click="openAddPlayerDialog(1, 0)"
                    />
                  </div>
                  <div class="player team1-player2">
                    <div v-if="team1[1]">
                      {{ team1[1] || "Jugador 2 Equipo 1" }}
                    </div>
                    <q-btn
                      v-else
                      flat
                      round
                      icon="o_person_add"
                      @click="openAddPlayerDialog(1, 1)"
                    />
                  </div>
                  <div class="player team2-player1">
                    <div v-if="team2[0]">
                      {{ team2[0] || "Jugador 1 Equipo 2" }}
                    </div>
                    <q-btn
                      v-else
                      flat
                      round
                      icon="o_person_add"
                      @click="openAddPlayerDialog(2, 0)"
                    />
                  </div>
                  <div class="player team2-player2">
                    <div v-if="team2[1]">
                      {{ team2[1] || "Jugador 2 Equipo 2" }}
                    </div>
                    <q-btn
                      v-else
                      flat
                      round
                      icon="o_person_add"
                      @click="openAddPlayerDialog(2, 1)"
                    />
                  </div>
                  
                  <div class="line1">A</div>
                  <div class="net"></div>
                  <div class="line2">B</div>
                  <div class="horizontal-line"></div>
                  
                </div>
              </div>
            </q-card-section>
          </q-card>
            <!-- Marcador -->
          <q-card class="match-card text-white q-pa-md">
            <q-card-section class="score-input">
              <h3 class="text-center text-white">Resultado</h3>
              <div class="score-grid">
                <!-- Encabezado -->
                <div class="header"></div>
                <div class="header" v-for="(set, index) in scoreTable" :key="'header-' + index">
                  Set {{ index + 1 }}
                </div>
                <!-- Equipo 1 -->
                <div class="team-label">Equipo 1</div>
                <div v-for="(set, index) in scoreTable" :key="'team1-' + index" class="score-cell">
                  <q-input
                    v-model.number="set.team1score"
                    dense
                    outlined
                    type="number"
                    :min="0"
                    :max="7"
                    class="text-white"
                    style="max-width: 60px; text-align: center;"
                  />
                </div>
                <!-- Equipo 2 -->
                <div class="team-label">Equipo 2</div>
                <div v-for="(set, index) in scoreTable" :key="'team2-' + index" class="score-cell">
                  <q-input
                    v-model.number="set.team2score"
                    dense
                    outlined
                    type="number"
                    :min="0"
                    :max="7"
                    class="text-white"
                    style="max-width: 60px; text-align: center;"
                  />
                </div>
              </div>
              <q-btn
                label="Guardar Resultado"
                color="primary"
                class="q-mt-md"
                @click="saveScore"
              />
            </q-card-section>
          </q-card>
        </div>
      </q-page>
    </q-page-container>

    <!-- Dialogo para agregar jugadores -->
    <q-dialog v-model="addPlayerDialog">
      <q-card>
        <q-card-section>
          <div class="text-h6">Agregar Jugador</div>
          <q-input v-model="searchInput" label="Buscar por email o teléfono" outlined dense />
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancelar" color="negative" v-close-popup />
          <q-btn flat label="Agregar" color="positive" @click="addPlayer" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Menú de Navegación Inferior -->
    <PlayerNavigationMenu />
  </q-layout>
</template>

<script>
import api from "../../api";
import dayjs from "dayjs";
import 'dayjs/locale/es-mx'
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useQuasar } from "quasar";
import PlayerNavigationMenu from "src/components/PlayerNavigationMenu.vue";
import BannerPromoScrolling from "src/components/BannerPromoScrolling.vue";
import NotificationBell from "src/components/NotificationBell.vue";
import PlayerTopMenu from "src/components/PlayerTopMenu.vue";

export default {
  components: {
    BannerPromoScrolling,
    NotificationBell,
    PlayerNavigationMenu,
    PlayerTopMenu,
  },
  setup() {
    const route = useRoute();
    const router = useRouter();
    const $q = useQuasar();
    const matchDetails = ref(null);
    const team1 = ref([]);
    const team2 = ref([]);
    const loading = ref(true);
    const searchInput = ref("");
    const selectedTeam = ref(null);
    const selectedPosition = ref(null);
    const addPlayerDialog = ref(false);
    const scoreTable = ref([
      { name: "Set 1", team1score: 0, team2score: 0 },
      { name: "Set 2", team1score: 0, team2score: 0 },
      { name: "Set 3", team1score: 0, team2score: 0 },
    ]);

    const fetchMatchDetails = async () => {
      try {
        const response = await api.get(`/matches/match/${route.params.matchId}`);
        matchDetails.value = response.data;
        team1.value = response.data.team1_players || [];
        team2.value = response.data.team2_players || [];
      } catch (error) {
        console.error("Error al cargar los detalles del partido:", error.message);
        $q.notify({
          type: "negative",
          message: "Error al cargar los detalles del partido.",
        });
      } finally {
        loading.value = false;
      }
    };

    const openAddPlayerDialog = (team, position) => {
      selectedTeam.value = team;
      selectedPosition.value = position;
      searchInput.value = "";
      addPlayerDialog.value = true;
    };

    const addPlayer = async () => {
      try {
        const payload = {
          email_or_phone: searchInput.value,
          match_id: route.params.matchId,
          team: selectedTeam.value,
          position: selectedPosition.value,
          club_name: matchDetails.value.club_name || "No especificado",
          player_name: team1.value[0] || "Jugador desconocido",
          match_date: matchDetails.value.match_date || "Fecha desconocida",
          match_time: matchDetails.value.match_time|| "Hora desconocida",
        };

        const response = await api.post("/matches/add-player", payload);

        if (response.data.status === "success") {
          $q.notify({
            type: "positive",
            message: "Jugador agregado exitosamente.",
          });
          fetchMatchDetails();
        } else if (response.data.status === "invited") {
          $q.notify({
            type: "info",
            message: "Jugador invitado a unirse a PadelPlay.",
          });
        }

        addPlayerDialog.value = false;
      } catch (error) {
        console.error("Error al agregar jugador:", error.message);
        $q.notify({
          type: "negative",
          message: "Error al agregar jugador.",
        });
      }
    };

    const saveScore = async () => {
      try {
        await api.put(`/matches/match/${route.params.matchId}`, {
          score: scoreTable.value,
        });
        $q.notify({
          type: "positive",
          message: "Resultado guardado exitosamente.",
        });
      } catch (error) {
        console.error("Error al guardar el resultado:", error.message);
        $q.notify({
          type: "negative",
          message: "Error al guardar el resultado.",
        });
      }
    };

    const goBack = () => {
      router.back();
    };

    onMounted(fetchMatchDetails);

    return {
      matchDetails,
      team1,
      team2,
      loading,
      scoreTable,
      addPlayerDialog,
      searchInput,
      addPlayer,
      openAddPlayerDialog,
      saveScore,
      goBack,
    };
  },
  methods:{
    openChat() {
      this.$router.push(`/matches/${this.$route.params.matchId}/chat`);
    },
    formatDate(date) {
      dayjs.locale("es-mx");
      const formattedDate = dayjs(date).format('dddd, D [de] MMMM [del] YYYY');
      const [day, restOfDate] = formattedDate.split(' de ');
      const capitalizedDay = day.charAt(0).toUpperCase() + day.slice(1);
      const capitalizedMonth = restOfDate.charAt(0).toUpperCase() + restOfDate.slice(1);
      return capitalizedDay + ' de ' + capitalizedMonth;
    },
  }
};
</script>
  
<style scoped>
  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 16px;
    background-color: #000000; /* Fondo del encabezado */
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

.court-container {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  margin-bottom: 10px;
}

.court {
  position: relative;
  background-color: #1976d2;
  border-radius: 10px;
  color: white;
  width: 100%;
  max-width: 400px; /* Tamaño fijo para mantener proporción */
  aspect-ratio: 2 / 1; /* Relación de aspecto de la cancha */
  padding: 0;
}

.match-card {
  background-image: url("../../assets/texturafondo.png");
  margin-bottom: 10px;
  border-radius: 7%;
  padding: 0px;
}

.match-card h3 {
  margin-top: 0px;
  margin-bottom: 15px;
  font-size: x-large;
  font-weight: bold;
}

.player {
  position: absolute;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  transform: translate(-50%, -50%);
}

.team1-player1 {
  top: 25%;
  left: 33%;
}

.team1-player2 {
  top: 75%;
  left: 33%;
}

.team2-player1 {
  top: 25%;
  left: 67%;
}

.team2-player2 {
  top: 75%;
  left: 67%;
}

.net {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 50%;
  width: 1.5px;
  background-color: rgb(194, 194, 194);
  opacity: 0.6;
  transform: translateX(-50%);
  box-shadow: 1px 15px 4px #d1d0d0;
}

.line1 {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 15%;
  width: 1.5px;
  background-color: white;
  opacity: 0.9;
  transform: translateX(-50%);
}

.line2 {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 85%;
  width: 1.5px;
  background-color: white;
  opacity: 0.9;
  transform: translateX(-50%);
}

.horizontal-line {
  position: absolute;
  top: 50%;
  left: 15%;
  width: 70%;
  height: 1.5px; /* Ajusta el grosor de la línea si es necesario */
  background-color: white;
  opacity: 0.7;
  transform: translateY(-50%);
}

/* Marcador */
.set {
  display: flex;
  flex-direction: column;
  align-items: center;
  background-color: #121212;
  padding: 10px;
  border-radius: 10px;
}

.set-label {
  font-size: 16px;
  font-weight: bold;
  color: white;
  margin-bottom: 5px;
}

.team-score {
  margin: 5px 0;
}

.q-input {
  color: white !important;
}

.q-card {
  background-color: #121212 !important;
  color: white !important;
}
.score-grid {
  display: grid;
  grid-template-columns: auto repeat(3, 1fr); /* Una columna para equipos y tres para sets */
  gap: 10px;
  align-items: center;
  justify-content: center;
}

.header {
  text-align: center;
  font-weight: bold;
  color: white;
}

.team-label {
  text-align: center;
  font-weight: bold;
  color: white;
}

.score-cell {
  text-align: center;
}

.score-input {
  --q-input-border-color: rgba(255, 255, 255, 0.6); /* Borde claro */
  --q-input-bg-color: rgba(255, 255, 255, 0.1);     /* Fondo semi-transparente */
  --q-input-text-color: white;                      /* Texto blanco */
  --q-input-placeholder-color: rgba(255, 255, 255, 0.4); /* Placeholder más claro */
  border-radius: 4px;                               /* Bordes redondeados */
  padding: 5px;
  text-align: center;
}

.score-input .q-field {
  background-color: rgba(255, 255, 255, 0.1) !important; /* Fondo del campo */
  color: white !important;                              /* Color del texto */
  border: 1px solid rgba(255, 255, 255, 0.6) !important; /* Borde claro */
}

.vertical-text {
  transform: rotate(-90deg); /* Rota el texto 90 grados a la izquierda */
  transform-origin: left top; /* Establece el punto de origen de la rotación */
}

</style>