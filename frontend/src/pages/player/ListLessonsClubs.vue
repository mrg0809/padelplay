<template>
    <q-layout view="hHh lpR fFf" class="bg-dark text-white">
      <q-header elevated class="text-white">
        <div class="header-content">
          <div class="greeting">
            <img src="/src/assets/padelplay.png" alt="Logo" class="logo-icon" />
            Clubs
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
          <div class="search-bar">
            <q-input
              v-model="searchQuery"
              filled
              dense
              placeholder="Buscar por nombre o ubicación"
              @input="searchClubs"
              class="text-dark"
            >
              <template v-slot:prepend>
                <q-icon name="search" class="text-primary" />
              </template>
            </q-input>
          </div>
  
          <!-- Clubs List -->
          <div class="clubs-list">
            <q-list v-if="clubs.length > 0" class="q-mt-md">
              <q-item
                v-for="club in clubs"
                :key="club.id"
                clickable
                @click="viewClubDetails(club.id)"
                class="club-card"
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
            <div v-else class="text-center">No se encontraron clubes.</div>
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
      const clubs = ref([]);
      const router = useRouter();
      const searchQuery = ref("");
      const searching = ref(false);
      const $q = useQuasar();
      let userLocation = null;
  
      onMounted(async () => {
        try {
            const userLocation = await getUserLocation(); // Obtener la ubicación del usuario
            await searchClubs("", userLocation); // Carga inicial con geolocalización
        } catch (error) {
            console.error("Geolocation error:", error.message);
            $q.notify({
            type: "negative",
            message: "No se pudo obtener tu ubicación.",
            });
            await searchClubs(""); // Carga inicial sin geolocalización
        }
        });

// Buscar al escribir
watch(searchQuery, (newQuery) => {
  if (newQuery && newQuery.trim() !== "") {
    searchClubs(newQuery); // Solo búsqueda por texto
  }
});
  
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
  
      const searchClubs = async (query, userLocation = null) => {
      try {
        if (query.trim()) {
          // Buscar por nombre
          const { data, error } = await supabase
            .from("clubs")
            .select("id, name, address, logo_url")
            .ilike("name", `%${query}%`);
          if (error) throw error;
          clubs.value = data.map((club) => ({
            id: club.id,
            name: club.name,
            address: club.address,
            logo_url: club.logo_url,
          }));
        } else if (userLocation) {
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
        console.error("Error fetching clubs:", error.message);
        $q.notify({
          type: "negative",
          message: "Error al buscar clubes: " + error.message,
        });
      }
    };

    const viewClubDetails = (clubId, tabName = "clases") => {
      router.push({ path: `/player/clubs/${clubId}`, query: { tab: tabName } });
    };

    const goBack = () => {
      router.back();
    }

    return {
      clubs,
      searchQuery,
      searching,
      searchClubs,
      viewClubDetails,
      goBack,
    };
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
  .search-bar {
    background-color: white;
    height: 30px;
    width: 100%;
    margin-bottom: 16px;
    border-radius: 80px;
  }
  
  .search-bar q-input {
    width: 100%;
    max-width: 800px;
    margin: 0 auto;
  }

  .clubs-list .club-card {
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
  </style>
  