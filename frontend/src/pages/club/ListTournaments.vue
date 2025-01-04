<template>
    <q-layout view="hHh lpR fFf" class="bg-dark text-white">
      <q-header elevated class="bg-primary text-white">
        <q-toolbar>
          <q-toolbar-title>Mis Torneos</q-toolbar-title>
          <q-btn flat round icon="arrow_back" @click="goBack" label="REGRESAR" />
        </q-toolbar>
      </q-header>
  
      <q-page-container>
        <q-page class="q-pa-md">
          <!-- Listado de Torneos -->
          <div v-if="tournaments.length === 0" class="text-center q-mt-md">
            <q-icon name="event_busy" size="64px" />
            <p>No has creado torneos todavía.</p>
          </div>
          <div v-else class="tournaments-list">
            <q-card
              v-for="tournament in tournaments"
              :key="tournament.id"
              class="q-mb-md"
              bordered
            >
              <q-card-section>
                <h4>{{ tournament.name }}</h4>
                <p>
                  <strong>Fecha:</strong> {{ tournament.start_date }} <br />
                  <strong>Mínimo de Parejas:</strong> {{ tournament.min_pairs }} <br />
                  <strong>Parejas Inscritas:</strong> {{ tournament.registered_teams }}
                </p>
              </q-card-section>
            </q-card>
          </div>
        </q-page>
      </q-page-container>
    </q-layout>
  </template>
  
  <script>
  import { ref, onMounted } from "vue";
  import { supabase } from "src/services/supabase";
  import { useRouter } from "vue-router";
  
  export default {
    name: "ListTournaments",
    setup() {
      const router = useRouter();
      const tournaments = ref([]);
      const clubId = ref(null);
  
      const fetchTournaments = async () => {
        try {
          if (!clubId.value) {
            console.error("Club ID no encontrado.");
            return;
          }
  
          const { data, error } = await supabase.rpc("get_tournaments_by_club", {
            club_id: clubId.value,
          });
  
          if (error) {
            console.error("Error fetching tournaments:", error.message);
            return;
          }
  
          tournaments.value = data.map((tournament) => ({
            id: tournament.id,
            name: tournament.name,
            start_date: tournament.start_date,
            min_pairs: tournament.min_pairs,
            registered_teams: tournament.registered_teams || 0,
          }));
        } catch (error) {
          console.error("Unexpected error fetching tournaments:", error.message);
        }
      };
  
      const goBack = () => {
        router.back();
      };
  
      onMounted(() => {
        const token = localStorage.getItem("token");
        if (token) {
          const base64Url = token.split(".")[1];
          const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
          const payload = JSON.parse(atob(base64));
          clubId.value = payload.club_id || null;
        }
  
        fetchTournaments();
      });
  
      return {
        tournaments,
        goBack,
      };
    },
  };
  </script>
  
  <style scoped>
  .tournaments-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  
  .q-card {
    background-color: #1e1e1e;
    color: white;
  }
  
  .q-card:hover {
    background-color: #292929;
  }
  </style>
  