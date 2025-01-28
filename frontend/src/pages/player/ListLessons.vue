<template>
    <q-layout view="hHh lpR fFf" class="bg-dark text-white">
      <q-header elevated class="text-white">
        <div class="header-content">
          <div class="greeting">
            <img src="/src/assets/padelplay.png" alt="Logo" class="logo-icon" />
          </div>
      
          <div class="header-icons">
            
          </div>
        </div>
        <BannerPromoScrolling />
      </q-header>
  
      <q-page-container>
        <q-page class="q-pa-md">
          <!-- Filtros -->
          <div class="filters q-mb-md">
            <q-select
              v-model="filters.city"
              :options="cityOptions"
              label="Ciudad"
              rounded
              standout
              class="q-mb-sm filter-select"
              bg-color="primary"
            >
            <template v-slot:prepend>
                <q-icon name="location_on" />
            </template>
            </q-select>
            <q-select
              v-model="filters.category"
              :options="categories"
              label="Categoría"
              rounded
              standout
              class="q-mb-sm"
              bg-color="primary"
            >
              <template v-slot:prepend>
                  <q-icon name="category" />
              </template>
            </q-select>
            <q-select
              v-model="filters.gender"
              :options="genders"
              label="Género"
              rounded
              standout
              class="q-mb-sm"
              bg-color="primary"
            >
              <template v-slot:prepend>
                  <q-icon name="wc" />
              </template>
            </q-select>
          </div>
          
          <!-- Listado de Torneos -->
          <div v-if="tournaments.length === 0" class="text-center text-black">
            <q-icon name="event_busy" size="64px" />
            <p>No se encontraron clases.</p>
          </div>
          <div v-else class="lessons-list">
            <q-card
              v-for="tournament in tournaments"
              :key="tournament.id"
              class="q-mb-md tournament-card"
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
      <PlayerNavigationMenu />
    </q-layout>
  </template>
  
  <script>
  import { ref, onMounted, watch } from "vue";
  import { supabase } from "src/services/supabase";
  import { useRouter } from "vue-router";
  import PlayerNavigationMenu from "src/components/PlayerNavigationMenu.vue";
  import BannerPromoScrolling from "src/components/BannerPromoScrolling.vue";
  
  export default {
    name: "ListTournaments",
    components: {
      PlayerNavigationMenu,
      BannerPromoScrolling,
    },
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

      const goToPadelite = (id) => {
        router.push("/padelite");
      };

      const goBack = () => {
        router.back();
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
        goToPadelite,
        goBack,
      };
    },
  };
  </script>
  
  <style scoped>
    .filters {
      display: flex;
      flex-direction: row;
      gap: 10px;
    }

    .filters q-select {
      --q-field-height: 12px !important; /* Ajusta la altura del q-select */
      width: 12px !important; /* Ajusta el ancho del q-select */
      font-size: 14px;
    }

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

    .tournaments-list {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    
    .q-card {
      background-image: url(../../assets/texturafondo.png);
      background-size: cover;
      color: white;
    }
    
    .q-card:hover {
      background-color: #292929;
    }

    .tennis-yellow {
      margin: 0;
    color: #f0ff00; 
    }

    .filter-select {
      max-width: 33%;
      height: 10px;
    }

</style>
  