<template>
  <q-layout view="hHh lpR fFf" class="body text-white">
    <q-header elevated class="bg-primary text-white">
      <div class="header-content">
        <div class="greeting">
          <img src="/src/assets/padelplay.png" alt="Logo" class="logo-icon" />
          Cuadro Propuesto del Torneo
        </div>
        <div class="header-icons">
          <q-btn flat round icon="arrow_back" @click="goBack" />
        </div>
      </div>
    </q-header>
    <q-page-container>
      <q-page class="q-pa-md">
        
        <!-- Loading State -->
        <div v-if="loading" class="text-center q-mt-md">
          <q-spinner-puff color="primary" size="3em" />
          <p>Generando cuadro del torneo...</p>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="text-center q-mt-md">
          <q-icon name="warning" color="negative" size="3em" />
          <p class="text-negative">{{ error }}</p>
          <q-btn label="Volver" color="primary" @click="goBack" />
        </div>

        <!-- Tournament Preview -->
        <div v-else-if="tournamentData">
          <!-- Tournament Info Header -->
          <q-card class="q-mb-md tournament-info-card">
            <q-card-section>
              <div class="row items-center q-gutter-md">
                <div class="col">
                  <h4 class="q-my-none">{{ tournamentData.tournament?.name || 'Torneo' }}</h4>
                  <p class="q-mb-none text-subtitle2">
                    Sistema: {{ getSystemName(tournamentData.system) }} |
                    Total de Partidos: {{ tournamentData.matches?.length || 0 }}
                  </p>
                </div>
                <div class="col-auto">
                  <q-chip 
                    :color="tournamentData.system === 'eliminacion directa' ? 'red' : 
                           tournamentData.system === 'round-robin' ? 'blue' :
                           tournamentData.system === 'combinado' ? 'purple' : 'green'"
                    text-color="white"
                    :label="getSystemName(tournamentData.system)"
                    icon="emoji_events"
                  />
                </div>
              </div>
            </q-card-section>
          </q-card>

          <!-- Round-Robin Structure -->
          <div v-if="tournamentData.system === 'round-robin'" class="tournament-structure">
            <div v-if="tournamentData.structure.groups" class="groups-container">
              <div v-for="group in tournamentData.structure.groups" :key="group.name" class="group-section q-mb-lg">
                <q-card class="group-card">
                  <q-card-section class="bg-blue-8 text-white">
                    <h6 class="q-my-none">{{ group.name }}</h6>
                    <div class="teams-list">
                      <q-chip
                        v-for="team in group.teams"
                        :key="team.id"
                        color="white"
                        text-color="blue-8"
                        size="sm"
                        class="q-ma-xs"
                      >
                        {{ getTeamName(team) }}
                      </q-chip>
                    </div>
                  </q-card-section>
                  
                  <q-card-section class="matches-section">
                    <h6 class="q-mt-none q-mb-md">Partidos del Grupo</h6>
                    <div v-if="tournamentData.structure.group_matches[group.name]" class="group-matches">
                      <q-card
                        v-for="match in tournamentData.structure.group_matches[group.name]"
                        :key="match.id"
                        class="match-card q-mb-sm"
                        flat
                        bordered
                      >
                        <q-card-section class="q-pa-sm">
                          <div class="match-details">
                            <div class="match-teams">
                              <span class="team-name">{{ match.team1.name }}</span>
                              <q-icon name="sports" class="vs-icon" />
                              <span class="team-name">{{ match.team2.name }}</span>
                            </div>
                            <div class="match-schedule q-mt-sm">
                              <div class="schedule-inputs row q-gutter-sm">
                                <q-input
                                  v-model="match.match_date"
                                  type="date"
                                  dense
                                  outlined
                                  label="Fecha"
                                  class="col"
                                />
                                <q-input
                                  v-model="match.match_time"
                                  type="time"
                                  dense
                                  outlined
                                  label="Hora"
                                  class="col"
                                />
                                <q-select
                                  v-model="match.court_id"
                                  :options="courtOptions"
                                  option-value="value"
                                  option-label="label"
                                  dense
                                  outlined
                                  label="Cancha"
                                  class="col"
                                  emit-value
                                  map-options
                                />
                              </div>
                            </div>
                          </div>
                        </q-card-section>
                      </q-card>
                    </div>
                  </q-card-section>
                </q-card>
              </div>
            </div>
          </div>

          <!-- Elimination Bracket Structure -->
          <div v-else-if="tournamentData.system === 'eliminacion directa'" class="tournament-structure">
            <div class="bracket-container">
              <div v-for="(roundMatches, roundName) in tournamentData.structure.bracket" :key="roundName" class="bracket-round">
                <q-card class="round-card q-mb-lg">
                  <q-card-section class="bg-red-8 text-white">
                    <h6 class="q-my-none">{{ roundName }}</h6>
                  </q-card-section>
                  
                  <q-card-section>
                    <div class="round-matches">
                      <q-card
                        v-for="match in roundMatches"
                        :key="match.id"
                        class="match-card q-mb-sm"
                        flat
                        bordered
                      >
                        <q-card-section class="q-pa-sm">
                          <div class="match-details">
                            <div class="match-teams">
                              <span class="team-name" :class="{ 'tbd-team': !match.team1.player1 }">
                                {{ match.team1.name }}
                              </span>
                              <q-icon name="sports" class="vs-icon" />
                              <span class="team-name" :class="{ 'tbd-team': !match.team2.player1 }">
                                {{ match.team2.name }}
                              </span>
                            </div>
                            <div class="match-schedule q-mt-sm">
                              <div class="schedule-inputs row q-gutter-sm">
                                <q-input
                                  v-model="match.match_date"
                                  type="date"
                                  dense
                                  outlined
                                  label="Fecha"
                                  class="col"
                                />
                                <q-input
                                  v-model="match.match_time"
                                  type="time"
                                  dense
                                  outlined
                                  label="Hora"
                                  class="col"
                                />
                                <q-select
                                  v-model="match.court_id"
                                  :options="courtOptions"
                                  option-value="value"
                                  option-label="label"
                                  dense
                                  outlined
                                  label="Cancha"
                                  class="col"
                                  emit-value
                                  map-options
                                />
                              </div>
                            </div>
                          </div>
                        </q-card-section>
                      </q-card>
                    </div>
                  </q-card-section>
                </q-card>
              </div>
            </div>
          </div>

          <!-- Combined System Structure -->
          <div v-else-if="tournamentData.system === 'combinado'" class="tournament-structure">
            <!-- Group Phase -->
            <q-card class="q-mb-lg">
              <q-card-section class="bg-purple-8 text-white">
                <h5 class="q-my-none">Fase de Grupos</h5>
              </q-card-section>
            </q-card>
            
            <div v-if="tournamentData.structure.groups" class="groups-container q-mb-xl">
              <div v-for="group in tournamentData.structure.groups" :key="group.name" class="group-section q-mb-lg">
                <q-card class="group-card">
                  <q-card-section class="bg-blue-6 text-white">
                    <h6 class="q-my-none">{{ group.name }}</h6>
                    <div class="teams-list">
                      <q-chip
                        v-for="team in group.teams"
                        :key="team.id"
                        color="white"
                        text-color="blue-8"
                        size="sm"
                        class="q-ma-xs"
                      >
                        {{ getTeamName(team) }}
                      </q-chip>
                    </div>
                  </q-card-section>
                  
                  <q-card-section class="matches-section">
                    <div v-if="tournamentData.structure.group_matches[group.name]" class="group-matches">
                      <q-card
                        v-for="match in tournamentData.structure.group_matches[group.name]"
                        :key="match.id"
                        class="match-card q-mb-sm"
                        flat
                        bordered
                      >
                        <q-card-section class="q-pa-sm">
                          <div class="match-details">
                            <div class="match-teams">
                              <span class="team-name">{{ match.team1.name }}</span>
                              <q-icon name="sports" class="vs-icon" />
                              <span class="team-name">{{ match.team2.name }}</span>
                            </div>
                            <div class="match-schedule q-mt-sm">
                              <div class="schedule-inputs row q-gutter-sm">
                                <q-input
                                  v-model="match.match_date"
                                  type="date"
                                  dense
                                  outlined
                                  label="Fecha"
                                  class="col"
                                />
                                <q-input
                                  v-model="match.match_time"
                                  type="time"
                                  dense
                                  outlined
                                  label="Hora"
                                  class="col"
                                />
                                <q-select
                                  v-model="match.court_id"
                                  :options="courtOptions"
                                  option-value="value"
                                  option-label="label"
                                  dense
                                  outlined
                                  label="Cancha"
                                  class="col"
                                  emit-value
                                  map-options
                                />
                              </div>
                            </div>
                          </div>
                        </q-card-section>
                      </q-card>
                    </div>
                  </q-card-section>
                </q-card>
              </div>
            </div>

            <!-- Playoff Phase -->
            <q-card class="q-mb-lg">
              <q-card-section class="bg-purple-8 text-white">
                <h5 class="q-my-none">Fase de Playoffs</h5>
              </q-card-section>
            </q-card>
            
            <div v-if="tournamentData.structure.playoffs" class="playoffs-container">
              <div v-for="(roundMatches, roundName) in tournamentData.structure.playoffs" :key="roundName" class="bracket-round">
                <q-card class="round-card q-mb-lg">
                  <q-card-section class="bg-red-6 text-white">
                    <h6 class="q-my-none">{{ roundName }}</h6>
                  </q-card-section>
                  
                  <q-card-section>
                    <div class="round-matches">
                      <q-card
                        v-for="match in roundMatches"
                        :key="match.id"
                        class="match-card q-mb-sm"
                        flat
                        bordered
                      >
                        <q-card-section class="q-pa-sm">
                          <div class="match-details">
                            <div class="match-teams">
                              <span class="team-name tbd-team">{{ match.team1.name }}</span>
                              <q-icon name="sports" class="vs-icon" />
                              <span class="team-name tbd-team">{{ match.team2.name }}</span>
                            </div>
                            <div class="match-schedule q-mt-sm">
                              <div class="schedule-inputs row q-gutter-sm">
                                <q-input
                                  v-model="match.match_date"
                                  type="date"
                                  dense
                                  outlined
                                  label="Fecha"
                                  class="col"
                                />
                                <q-input
                                  v-model="match.match_time"
                                  type="time"
                                  dense
                                  outlined
                                  label="Hora"
                                  class="col"
                                />
                                <q-select
                                  v-model="match.court_id"
                                  :options="courtOptions"
                                  option-value="value"
                                  option-label="label"
                                  dense
                                  outlined
                                  label="Cancha"
                                  class="col"
                                  emit-value
                                  map-options
                                />
                              </div>
                            </div>
                          </div>
                        </q-card-section>
                      </q-card>
                    </div>
                  </q-card-section>
                </q-card>
              </div>
            </div>
          </div>

          <!-- Liga System Structure -->
          <div v-else-if="tournamentData.system === 'liga'" class="tournament-structure">
            <q-card class="q-mb-lg">
              <q-card-section class="bg-green-8 text-white">
                <h5 class="q-my-none">Liga - Todos contra Todos</h5>
                <p class="q-mb-none">{{ tournamentData.structure.total_matches }} partidos programados</p>
              </q-card-section>
            </q-card>
            
            <div class="liga-matches">
              <q-card
                v-for="match in tournamentData.matches"
                :key="match.id"
                class="match-card q-mb-sm"
                flat
                bordered
              >
                <q-card-section class="q-pa-sm">
                  <div class="match-details">
                    <div class="match-teams">
                      <span class="team-name">{{ match.team1.name }}</span>
                      <q-icon name="sports" class="vs-icon" />
                      <span class="team-name">{{ match.team2.name }}</span>
                    </div>
                    <div class="match-schedule q-mt-sm">
                      <div class="schedule-inputs row q-gutter-sm">
                        <q-input
                          v-model="match.match_date"
                          type="date"
                          dense
                          outlined
                          label="Fecha"
                          class="col"
                        />
                        <q-input
                          v-model="match.match_time"
                          type="time"
                          dense
                          outlined
                          label="Hora"
                          class="col"
                        />
                        <q-select
                          v-model="match.court_id"
                          :options="courtOptions"
                          option-value="value"
                          option-label="label"
                          dense
                          outlined
                          label="Cancha"
                          class="col"
                          emit-value
                          map-options
                        />
                      </div>
                    </div>
                  </div>
                </q-card-section>
              </q-card>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="actions-section q-mt-xl">
            <div class="row q-gutter-md justify-center">
              <q-btn
                label="Guardar Cuadro"
                color="green"
                size="lg"
                icon="save"
                @click="saveMatches"
                :loading="saving"
                class="save-btn"
              />
              <q-btn
                label="Cancelar"
                color="red"
                size="lg"
                icon="cancel"
                @click="cancelPreview"
                outline
                class="cancel-btn"
              />
            </div>
            <p class="text-center q-mt-sm text-caption">
              Al guardar el cuadro, se cerrarán las inscripciones y se bloquearán las canchas para los horarios programados
            </p>
          </div>
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
import { getTournamentSystemName, formatTeamName, getTournamentSystemColor } from 'src/helpers/tournamentUtils';

export default {
  name: "PreviewTournament",
  setup() {
    const route = useRoute();
    const router = useRouter();
    const $q = useQuasar();
    
    const tournamentData = ref(null);
    const loading = ref(false);
    const saving = ref(false);
    const error = ref(null);
    const courtOptions = ref([]);

    onMounted(async () => {
      await loadTournamentPreview();
      await loadCourts();
    });

    const loadTournamentPreview = async () => {
      loading.value = true;
      error.value = null;
      
      try {
        // Get tournament ID from route params
        const tournamentId = route.params.tournamentId;
        if (!tournamentId) {
          throw new Error("ID del torneo no encontrado");
        }

        // Generate tournament preview
        const response = await api.get(`/tournaments/${tournamentId}/preview`);
        tournamentData.value = response.data;
        
        console.log("Tournament preview loaded:", tournamentData.value);
      } catch (err) {
        console.error("Error loading tournament preview:", err);
        error.value = err.response?.data?.detail || err.message || "Error al cargar el preview del torneo";
      } finally {
        loading.value = false;
      }
    };

    const loadCourts = async () => {
      try {
        // Get court information for the select options
        if (tournamentData.value?.tournament_id) {
          const tournament = await supabase
            .from("tournaments")
            .select("courts_used, club_id")
            .eq("id", tournamentData.value.tournament_id)
            .single();

          if (tournament.data?.courts_used) {
            const courts = await supabase
              .from("courts")
              .select("id, name")
              .in("id", tournament.data.courts_used);

            if (courts.data) {
              courtOptions.value = courts.data.map(court => ({
                label: court.name,
                value: court.id
              }));
            }
          }
        }
      } catch (err) {
        console.error("Error loading courts:", err);
      }
    };

    const getSystemName = (system) => {
      return getTournamentSystemName(system);
    };

    const getTeamName = (team) => {
      return formatTeamName(team);
    };

    const saveMatches = async () => {
      saving.value = true;
      
      try {
        if (!tournamentData.value?.matches) {
          throw new Error("No hay partidos para guardar");
        }

        const response = await api.post(
          `/tournaments/${tournamentData.value.tournament_id}/save-matches`,
          tournamentData.value.matches
        );

        $q.notify({
          type: "positive",
          message: `${response.data.matches_saved} partidos guardados exitosamente. Torneo cerrado.`,
          timeout: 3000
        });

        // Navigate back to tournament list
        setTimeout(() => {
          router.push('/club/tournaments');
        }, 1500);
        
      } catch (err) {
        console.error("Error saving matches:", err);
        $q.notify({
          type: "negative",
          message: err.response?.data?.detail || "Error al guardar los partidos",
          timeout: 3000
        });
      } finally {
        saving.value = false;
      }
    };

    const cancelPreview = () => {
      router.back();
    };

    const goBack = () => {
      router.back();
    };

    return {
      tournamentData,
      loading,
      saving,
      error,
      courtOptions,
      getSystemName,
      getTeamName,
      saveMatches,
      cancelPreview,
      goBack
    };
  }
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

.tournament-info-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
}

.tournament-structure {
  max-width: 1200px;
  margin: 0 auto;
}

.group-card, .round-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 8px;
  margin-bottom: 16px;
}

.match-card {
  background: rgba(255, 255, 255, 0.98);
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.match-card:hover {
  border-color: #2196f3;
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.match-details {
  width: 100%;
}

.match-teams {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.team-name {
  font-weight: 600;
  color: #1976d2;
  font-size: 0.9rem;
  flex: 1;
  text-align: center;
  padding: 0 8px;
}

.tbd-team {
  color: #9e9e9e;
  font-style: italic;
}

.vs-icon {
  color: #ff5722;
  font-size: 1.2rem;
  margin: 0 8px;
}

.schedule-inputs {
  gap: 8px;
}

.teams-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 8px;
}

.groups-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 20px;
}

.bracket-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.actions-section {
  background: rgba(255, 255, 255, 0.9);
  padding: 20px;
  border-radius: 12px;
  text-align: center;
}

.save-btn, .cancel-btn {
  min-width: 150px;
}

@media (max-width: 768px) {
  .groups-container {
    grid-template-columns: 1fr;
  }
  
  .schedule-inputs {
    flex-direction: column;
  }
  
  .match-teams {
    flex-direction: column;
    gap: 8px;
  }
  
  .team-name {
    text-align: center;
  }
}
</style>