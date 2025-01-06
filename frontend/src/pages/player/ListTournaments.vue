<template>
    <q-layout view="hHh lpR fFf" class="bg-dark text-white">
      <q-header elevated class="bg-primary text-white">
        <q-toolbar>
          <q-toolbar-title>Listado de Torneos</q-toolbar-title>
          <q-btn flat round icon="arrow_back" @click="goBack" label="REGRESAR" />
        </q-toolbar>
      </q-header>
  
      <q-page-container>
        <q-page class="q-pa-md">
          <!-- Filtros -->
          <div class="filters q-mb-md">
            <q-select
              v-model="filters.city"
              :options="cityOptions"
              label="Ciudad"
              outlined
              dense
              class="q-mb-sm"
            />
            <q-select
              v-model="filters.category"
              :options="categories"
              label="Categoría"
              outlined
              dense
              class="q-mb-sm"
            />
            <q-select
              v-model="filters.gender"
              :options="genders"
              label="Género"
              outlined
              dense
              class="q-mb-sm"
            />
          </div>
  
          <!-- Listado de Torneos -->
          <div v-if="tournaments.length === 0" class="text-center q-mt-md">
            <q-icon name="event_busy" size="64px" />
            <p>No se encontraron torneos.</p>
          </div>
          <div v-else class="tournaments-list">
            <q-card
              v-for="tournament in tournaments"
              :key="tournament.id"
              class="q-mb-md"
              clickable
              bordered
              @click="goToTournamentDetails(tournament.id)"
            >
              <q-card-section>
                <h4 class="tennis-yellow">{{ tournament.name }}</h4>
                <p>
                  <strong>Fecha:</strong> {{ tournament.start_date }} <br />
                  <strong>Ciudad:</strong> {{ tournament.city || "No disponible" }} <br />
                  <strong>Categoría:</strong> {{ tournament.category }} <br />
                  <strong>Género:</strong> {{ tournament.gender }}
                </p>
              </q-card-section>
            </q-card>
          </div>
        </q-page>
      </q-page-container>
      <!-- Menú de Navegación Inferior -->
      <q-footer class="bg-primary text-white">
        <q-tabs
          align="justify"
          class="q-pa-xs"
          active-color="white"
          @update:model-value="onTabChange"
        >
          <q-tab
            v-for="tab in tabs"
            :key="tab.name"
            :name="tab.name"
            :label="tab.label"
            :icon="tab.icon"
            class="text-white"
          />
        </q-tabs>
      </q-footer>
    </q-layout>
  </template>
  
  <script>
  import { ref, onMounted, watch } from "vue";
  import { supabase } from "src/services/supabase";
  import { useRouter } from "vue-router";
  
  export default {
    name: "ListTournaments",
    setup() {
      const router = useRouter();
  
      const tournaments = ref([]);
      const filters = ref({
        city: null,
        category: null,
        gender: null,
      });
  
      const cityOptions = ref([]);
      const categories = ref(["primera", "segunda", "tercera", "cuarta", "quinta", "libre"]);
      const genders = ref(["mixto", "varonil", "femenil"]);
  
      const fetchTournaments = async () => {
        try {
          const { data, error } = await supabase.rpc("get_upcoming_tournaments_with_city");
          if (error) {
            console.error("Error fetching tournaments:", error.message);
            return;
          }
  
          // Aplicar filtros
          tournaments.value = data.filter((tournament) => {
            const cityMatch = !filters.value.city || tournament.city === filters.value.city;
            const categoryMatch = !filters.value.category || tournament.category === filters.value.category;
            const genderMatch = !filters.value.gender || tournament.gender === filters.value.gender;
            return cityMatch && categoryMatch && genderMatch;
          });
        } catch (error) {
          console.error("Unexpected error fetching tournaments:", error.message);
        }
      };
  
      const fetchCities = async () => {
        try {
          const { data, error } = await supabase.rpc("get_unique_cities");
          if (error) {
            console.error("Error fetching cities:", error.message);
            return;
          }
  
          cityOptions.value = data.map((city) => ({
            label: city,
            value: city,
          }));
        } catch (error) {
          console.error("Unexpected error fetching cities:", error.message);
        }
      };
  
      const goToTournamentDetails = (id) => {
        router.push({ name: "TournamentDetails", params: { tournamentId: id } });
      };

      const goBack = () => {
        router.back();
      };

      const onTabChange = (tabName) => {
        router.push(`/player/${tabName}`);
      };
  
      // Watch para los filtros
      watch(filters, fetchTournaments, { deep: true });
  
      onMounted(() => {
        fetchTournaments();
        fetchCities();
      });
  
      return {
        tournaments,
        filters,
        cityOptions,
        categories,
        genders,
        goToTournamentDetails,
        goBack,
        onTabChange,
        tabs: [
          { name: "inicio", label: "Inicio", icon: "home" },
          { name: "torneos", label: "Torneos", icon: "sports_tennis" },
          { name: "asociaciones", label: "Asociaciones", icon: "group" },
          { name: "perfil", label: "Perfil", icon: "account_circle" },
        ],
      };
    },
  };
  </script>
  
  <style scoped>
  .filters {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  
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

  .tennis-yellow {
  color: #f0ff00; /* Color amarillo pelota de tenis */
}
  </style>
  