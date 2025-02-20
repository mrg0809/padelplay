<template>
    <q-page>
      <q-card>
        <q-card-section>
          <h5>Preview del Torneo: {{ tournament.name }}</h5>
          <p>
            Sistema: {{ tournament.system }} | Fecha de inicio: {{ tournament.start_date }} | Fecha de fin:
            {{ tournament.end_date }}
          </p>
        </q-card-section>
  
        <q-card-section>
          <!-- Mensaje si no hay suficientes parejas -->
          <div v-if="matches.length === 0" class="text-negative">
            <q-icon name="warning" class="q-mr-sm" />
            No hay suficientes parejas inscritas para cerrar el torneo.
          </div>
  
          <!-- Lista de partidos (solo se muestra si hay matches) -->
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
  
        <!-- Botones de acción (solo se muestran si hay matches) -->
        <q-card-actions align="right" v-if="matches.length > 0">
          <q-btn label="Guardar" color="primary" @click="saveMatches" />
          <q-btn label="Cancelar" color="negative" @click="closePreview" />
        </q-card-actions>
      </q-card>
    </q-page>
  </template>
  
  <script>
  import { supabase } from "src/services/supabase";
  import api from "src/api";
  
  export default {
    props: {
      tournament: {
        type: Object,
        required: true,
      },
      matches: {
        type: Array,
        required: true,
      },
    },
    data() {
      return {
        teams: [], // Para almacenar los nombres de los equipos
      };
    },
    async created() {
      // Obtener los nombres de los equipos
      await this.fetchTeams();
    },
    methods: {
      async fetchTeams() {
        // Obtener los equipos inscritos en el torneo
        const { data, error } = await supabase
          .from("tournament_teams")
          .select("id, player1_id, player2_id")
          .eq("tournament_id", this.tournament.id);
  
        if (error) {
          console.error("Error fetching teams:", error);
          return;
        }
  
        this.teams = data;
      },
      getTeamName(teamId) {
        // Obtener el nombre del equipo (simplificado)
        const team = this.teams.find((t) => t.id === teamId);
        return team ? `Equipo ${team.player1_id}` : "Equipo desconocido";
      },
      async saveMatches() {
        try {
          // Guardar los partidos en Supabase
          await api.post(`/tournaments/${this.tournament.id}/save-matches`, this.matches);
          this.$q.notify({
            type: "positive",
            message: "Partidos guardados exitosamente.",
          });
          this.closePreview();
        } catch (error) {
          console.error("Error saving matches:", error);
          this.$q.notify({
            type: "negative",
            message: "Error al guardar los partidos.",
          });
        }
      },
      closePreview() {
        this.$emit("close");
      },
    },
  };
  </script>
  
  <style scoped>
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