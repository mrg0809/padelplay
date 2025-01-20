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
          </div>
        </div>
        <BannerPromoScrolling />
      </q-header>
      <q-page-container class="home">
        <q-page class="q-pa-md">
          <!-- Search Bar -->
          <div class="filter-options">
            <q-select
                color="white"
                bg-color="black"
                v-model="selectedCity"
                :options="cityOptions"
                label="Ciudad"
                emit-value
                map-options
                rounded
                standout
            >
            <template v-slot:prepend>
                <q-icon name="location_on" />
            </template>
        </q-select>


            <q-select
                v-model="selectedDates"
                :options="dateOptions"
                label="Fechas"
                color="white"
                bg-color="black"
                multiple
                emit-value
                map-options
                rounded
                standout
            >
                <template v-slot:prepend>
                    <q-icon name="calendar_month" />
                </template>
            </q-select>

            <q-select
                v-model="selectedGenre"
                :options="genreOptions"
                label="Tipo"
                color="white"
                bg-color="black"
                multiple
                emit-value
                map-options
                rounded
                standout
            >
                <template v-slot:prepend>
                    <q-icon name="wc" />
                </template>
            </q-select>
          </div>
  
          <!-- Games List -->
          <div class="games-list">
            <q-list v-if="games.length > 0" class="q-mt-md">
              <q-item
                v-for="game in games"
                :key="game.id"
                clickable
                @click="viewGameDetails(game.id)"
                class="game-card"
              >
                <q-item-section avatar>
                  <img
                    :src="club.logo_url || '/src/assets/logo.jpeg'"
                    alt="Club Logo"
                    class="club-logo"
                  />
                </q-item-section>
                <q-item-section>
                  <q-item-label class="club-name">{{ club.name }}</q-item-label>
                  <q-item-label caption>{{ club.address }}</q-item-label>
                  <q-item-label caption v-if="club.distance">
                    Distancia: {{ (club.distance / 1000).toFixed(2) }} km
                  </q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
            <div v-else-if="searching" class="text-center">Buscando...</div>
            <div v-else class="text-center">No se encontraron juegos.</div>
          </div>
        </q-page>
      </q-page-container>
      <PlayerNavigationMenu />
    </q-layout>
  </template>
  
  <script>
  import { ref, onMounted, watch } from "vue";
  import { useRouter } from "vue-router";
  import { supabase } from "../../services/supabase";
  import { useQuasar } from "quasar";
  import PlayerNavigationMenu from "src/components/PlayerNavigationMenu.vue";
  import NotificationBell from "src/components/NotificationBell.vue";
  import BannerPromoScrolling from "src/components/BannerPromoScrolling.vue";
  
  export default {
    components:{
      PlayerNavigationMenu,
      BannerPromoScrolling,
      NotificationBell,
    },
    setup() {
      const cityOptions = ref([]);
      const games = []
      const router = useRouter();
      const searchQuery = ref("");
      const searching = ref(false);
      const $q = useQuasar();
      let userLocation = null;
      const genreOptions = ref([
        { label: 'Femenil', value: 'femenil' },
        { label: 'Varonil', value: 'varonil' },
        { label: 'Mixto', value: 'mixto' },
        ]);
  
      onMounted(async () => {
        fetchCities();
        });

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

      const getUserLocation = () => {
        return new Promise((resolve, reject) => {
          if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
              (position) => {
                const { latitude, longitude } = position.coords;
                if (latitude && longitude) {
                  resolve({ latitude, longitude });
                } else {
                  reject(new Error("Invalid geolocation data"));
                }
              },
              (error) => {
                reject(error);
              }
            );
          } else {
            reject(new Error("Geolocation is not supported by your device."));
          }
        });
      };
  
      const searchOpenGames = async (userLocation = null) => {
      try {
        if (userLocation) {
          // Buscar por geolocalización
          const { latitude, longitude } = userLocation;
          const { data, error } = await supabase.rpc("calculate_distance", {
            lat: latitude,
            lng: longitude,
          });
          if (error) throw error;
          clubs.value = data.map((club) => ({
            id: club.club_id,
            name: club.name,
            address: club.address,
            logo_url: club.logo_url,
            distance: club.distance,
          }));
        } else {
          clubs.value = [];
        }
      } catch (error) {
        console.error("Error fetching games:", error.message);
        $q.notify({
          type: "negative",
          message: "Error al buscar partidos: " + error.message,
        });
      }
    };

    const viewClubDetails = (clubId) => {
      router.push(`/club/${clubId}`); 
    };

    return {
      games,
      searchQuery,
      searching,
      genreOptions,
      viewClubDetails,
      cityOptions, 
    };
  },


  
    methods: {
      goBack() {
        this.$router.back();
      },
    },
  };
  </script>
  
  <style>

.home {
    background-color: #dddddd;
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

  .games-list .game-card {
    padding: 16px;
    border-radius: 8px;
    background-image: url("../../assets/texturafondo.png");
    background-size: cover;
    margin-bottom: 16px;
  }
  
  .club-logo {
    width: 64px;
    height: 64px;
    border-radius: 50%;
    object-fit: cover;
  }
  
  .club-name {
    font-size: 1.2em;
    font-weight: bold;
  }

  .filter-options {
  display: flex;
  flex-direction: row; /* Alinea los elementos en fila */
  justify-content: space-around; /* Distribuye espacio alrededor de los elementos */
}

.filter-options q-select {
  height: 10px;
  width: 40%;
}

.filter-options q-select ::v-deep .q-field__label,
.filter-options q-select ::v-deep .q-item__label {
  font-size: 0.5em; 
}
  </style>
  