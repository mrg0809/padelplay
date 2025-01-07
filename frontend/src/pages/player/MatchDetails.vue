<template>
    <q-layout view="hHh lpR fFf" class="bg-dark text-white">
      <q-header elevated class="bg-primary text-white">
        <q-toolbar>
          <q-toolbar-title>Detalles del Partido</q-toolbar-title>
          <q-btn flat round icon="arrow_back" @click="goBack" label="REGRESAR" />
        </q-toolbar>
      </q-header>
  
      <q-page-container>
        <q-page class="q-pa-md">
          <div v-if="loading" class="text-center">
            <q-spinner-dots color="primary" size="lg" />
          </div>
          <div v-else>
            <q-card class="bg-dark text-white q-pa-md">
              <q-card-section>
                <h3 class="text-center text-white">Partido</h3>
                <p><strong>Fecha:</strong> {{ matchDetails.match_date }}</p>
                <p><strong>Hora:</strong> {{ matchDetails.match_time }}</p>
                <p><strong>Club:</strong> {{ matchDetails.club_name || "No disponible" }}</p>
                <p><strong>Cancha:</strong> {{ matchDetails.court_name || "No disponible" }}</p>
              </q-card-section>
  
              <!-- Representación de la cancha -->
              <q-card-section class="q-mt-md">
                <div class="court-container">
                  <div class="court">
                    <!-- Jugadores o botones de agregar -->
                    <div class="player team1-player1">
                      <div v-if="team1[0]">
                        {{ team1[0] || "Jugador 1 Equipo 1" }}
                      </div>
                      <q-btn
                        v-else
                        outline
                        round
                        icon="add"
                        dense
                        color="orange"
                        @click="addPlayerToTeam(1)"
                      />
                    </div>
                    <div class="player team1-player2">
                      <div v-if="team1[1]">
                        {{ team1[1] || "Jugador 2 Equipo 1" }}
                      </div>
                      <q-btn
                        v-else
                        outline
                        round
                        icon="add"
                        dense
                        color="orange"
                        @click="addPlayerToTeam(1)"
                      />
                    </div>
                    <div class="player team2-player1">
                      <div v-if="team2[0]">
                        {{ team2[0] || "Jugador 1 Equipo 2" }}
                      </div>
                      <q-btn
                        v-else
                        outline
                        round
                        icon="add"
                        dense
                        color="orange"
                        @click="addPlayerToTeam(2)"
                      />
                    </div>
                    <div class="player team2-player2">
                      <div v-if="team2[1]">
                        {{ team2[1] || "Jugador 2 Equipo 2" }}
                      </div>
                      <q-btn
                        v-else
                        outline
                        round
                        icon="add"
                        dense
                        color="orange"
                        @click="addPlayerToTeam(2)"
                      />
                    </div>
                    <div class="net"></div>
                  </div>
                </div>
              </q-card-section>
  
              <!-- Marcador -->
              <q-card-section class="score-input">
                <h4 class="text-center text-white">Marcador</h4>
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
      <!-- Menú de Navegación Inferior -->
      <PlayerNavigationMenu />
    </q-layout>
  </template>
  
  
  
  <script>
  import api from "../../api";
  import { ref, onMounted } from "vue";
  import { useRoute, useRouter } from "vue-router";
  import { useQuasar } from "quasar";
  import PlayerNavigationMenu from "src/components/PlayerNavigationMenu.vue";
  
  export default {
    components: {
      PlayerNavigationMenu,
    },
    setup() {
      const route = useRoute();
      const router = useRouter();
      const $q = useQuasar();
  
      const matchDetails = ref(null);
      const team1 = ref([]);
      const team2 = ref([]);
      const loading = ref(true);
      const scoreTable = ref([
        { name: "Set 1", team1score: 0, team2score: 0 }, 
        { name: "Set 2", team1score: 0, team2score: 0 },
        { name: "Set 3", team1score: 0, team2score: 0 },
        ]);
        const scoreColumns = ref([
        { name: "name", required: true, label: "Set", align: "left", field: "name" }, 
        { name: "team1score", label: "Equipo 1", align: "center", field: "team1score" }, 
        { name: "team2score", label: "Equipo 2", align: "center", field: "team2score" }, 
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
  
      const addPlayerToTeam = (team) => {
        // Lógica para agregar jugador al equipo
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
        scoreColumns,
        addPlayerToTeam,
        saveScore,
        goBack,
      };
    },
  };
  </script>
  
  <style scoped>
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
  left: 25%;
}

.team1-player2 {
  top: 75%;
  left: 25%;
}

.team2-player1 {
  top: 25%;
  left: 75%;
}

.team2-player2 {
  top: 75%;
  left: 75%;
}

.net {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 50%;
  width: 2px;
  background-color: white;
  opacity: 0.7;
  transform: translateX(-50%);
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
</style>