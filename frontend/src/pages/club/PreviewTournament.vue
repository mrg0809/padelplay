<template>
    <q-layout view="hHh lpR fFf" class="body text-white">
        <q-header elevated class="bg-primary text-white">
            <div class="header-content">
                <div class="greeting">
                <img src="/src/assets/padelplay.png" alt="Logo" class="logo-icon" />
                Mis Torneos
                </div>
                <div class="header-icons">
                <q-btn flat round icon="arrow_back" @click="goBack" />
                </div>
            </div>
        </q-header>
        <q-page-container>
            <q-page>
            <q-card v-if="tournament && matches">  <q-card-section>
                <h5>Preview del Torneo: {{ tournament.name }}</h5>
                <p>
                    Fecha de inicio: {{ tournament.start_date }}
                </p>
                </q-card-section>

                <q-card-section>
                <div v-if="matches.length === 0" class="text-negative">
                    <q-icon name="warning" class="q-mr-sm" />
                    No hay suficientes parejas inscritas para cerrar el torneo.
                </div>

                <q-list bordered v-else>
                    <q-item v-for="(match, index) in matches" :key="index">
                    <q-item-section>
                        <q-item-label>{{ getTeamName(match.team1) }} vs {{ getTeamName(match.team2) }}</q-item-label>
                        <q-item-label caption>
                        Fecha:
                        <q-input v-model="match.match_date" type="date" dense />
                        Hora:
                        <q-input v-model="match.match_time" type="time" dense />
                        </q-item-label>
                    </q-item-section>
                    </q-item>
                </q-list>
                </q-card-section>

                <q-card-actions align="right" v-if="matches.length > 0">
                <q-btn label="Guardar" color="green" @click="saveMatches" />
                <q-btn label="Cancelar" color="red" @click="closePreview" />
                </q-card-actions>
            </q-card>
            <div v-else>
                <q-card>
                <q-card-section class="text-center">
                    <q-spinner-puff color="primary" size="3em" />
                    <p>Cargando datos del torneo...</p>
                </q-card-section>
                </q-card>
            </div>
            </q-page>
        </q-page-container>
    </q-layout>

  </template>
  
  <script>
  import { supabase } from "src/services/supabase";
  import api from "src/services/api";
  import { useRoute, useRouter } from "vue-router"; 
  import { ref, onMounted } from 'vue';
  import { useQuasar } from 'quasar'; 
  
  const componentName = "PreviewTournament";
  
  export default {
    setup() {
      const route = useRoute();
      const router = useRouter(); 
      const $q = useQuasar(); 
      const tournament = ref(null);
      const matches = ref(null);
      const teams = ref([]);
  
      onMounted(async () => {
        console.log("Route state:", route.state);
        if (route.state && route.state.tournament && route.state.matches) {
          console.log("Received tournament:", route.state.tournament);
          console.log("Received matches:", route.state.matches);
          tournament.value = route.state.tournament;
          matches.value = route.state.matches;
  
          try {
            await fetchTeams(); // Call fetchTeams here
          } catch (error) {
            console.error("Error fetching teams:", error);
            $q.notify({
              type: 'negative',
              message: 'Error al cargar los equipos.'
            });
          }
  
        } else {
          console.error("Tournament or matches data not found in route state.");
          // Redirect or show an error message
          $q.notify({
              type: 'negative',
              message: 'Datos del torneo no encontrados.'
            });
        }
      });
  
      const fetchTeams = async () => {
        const { data, error } = await supabase
          .from("tournament_teams")
          .select("id, player1_id, player2_id")
          .eq("tournament_id", tournament.value.id); // Use tournament.value.id
  
        if (error) {
          console.error("Error fetching teams:", error);
          return;
        }
  
        teams.value = data;
      };
  
      const getTeamName = (teamId) => {
        const team = teams.value.find((t) => t.id === teamId);
        return team ? `Equipo ${team.player1_id}` : "Equipo desconocido";
      };
  
      const saveMatches = async () => {
        try {
          await api.post(`/tournaments/${tournament.value.id}/save-matches`, matches.value); // Use tournament.value.id and matches.value
          $q.notify({
            type: "positive",
            message: "Partidos guardados exitosamente.",
          });
          closePreview();
        } catch (error) {
          console.error("Error saving matches:", error);
          $q.notify({
            type: "negative",
            message: "Error al guardar los partidos.",
          });
        }
      };
  
      const closePreview = () => {
        router.push('/club/your-tournaments-route'); // Or wherever you want to redirect
      };

      const goBack = () => {
        router.back();
      };
  
      return { tournament, matches, teams, getTeamName, saveMatches, closePreview, goBack };
    },
  };
  </script>
  
  <style scoped>
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
  width: 60px;
  height: 60px;
}

.body {
  background-image: url(../../assets/menu/padelcourtfloor.jpg);
  background-size: cover;
}
  .q-input {
    margin-left: 10px;
    width: 150px;
  }
  .text-negative {
  color: #c10015; /* Color rojo de Quasar para errores */
  font-weight: bold;
  display: flex;
  align-items: center;
}
  </style>