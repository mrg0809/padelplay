<template>
    <q-layout view="hHh lpR fFf" class="bg-dark text-white">
      <q-header elevated class="text-white">
        <div class="header-content">
          <div class="greeting">
            <img src="/src/assets/padelplay.png" alt="Logo" class="logo-icon" />
          </div>
          <div class="header-icons">
            <NotificationBell />
          </div>
        </div>
        <BannerPromoScrolling />
      </q-header>
  
      <q-page-container>
        <q-page class="q-pa-md">
          <div v-if="loading" class="text-center">
            <q-spinner-dots color="primary" size="xl" />
          </div>
          <div v-else>
            <div class="q-mb-md text-center">
              <img
                v-if="clubDetails?.logo_url"
                :src="clubDetails.logo_url"
                alt="Club Logo"
                style="max-width: 150px; border-radius: 8px;"
              />
            </div>
            <q-card class="tabs-section">
              <q-card-section>
                <q-tabs v-model="selectedTab" align="justify" class="text-white">
                  <q-tab name="info" label="Info" icon="o_info" />
                  <q-tab name="publiclessons" label="Sesiones" icon="event" />
                  <q-tab name="privatelessons" label="Coaches" icon="o_school" />
                </q-tabs>
              </q-card-section>
            </q-card>
            <q-separator />
            <ClubInfoComponent
              v-if="selectedTab === 'info'"
              :clubDetails="clubDetails"
              :coordinates="coordinates"
            />
            <LessonsComponent
              v-if="selectedTab === 'publiclessons'"
              :clubDetails="clubDetails"
            />
            <CoachesComponent
              v-if="selectedTab === 'privatelessons'"
              :clubDetails="clubDetails"
            />
          </div>
        </q-page>
      </q-page-container>
      <PlayerNavigationMenu />
    </q-layout>
  </template>
  
  
  <script>
  import { ref, onMounted, watchEffect, watch } from "vue";
  import { supabase } from "../../services/supabase";
  import { useRoute, useRouter } from "vue-router";
  import { useQuasar } from "quasar";
  import "leaflet/dist/leaflet.css";
  import L from "leaflet";
  import BannerPromoScrolling from "src/components/BannerPromoScrolling.vue";
  import NotificationBell from "src/components/NotificationBell.vue";
  import PlayerNavigationMenu from "src/components/PlayerNavigationMenu.vue";
  import ClubInfoComponent from "src/components/ClubInfoComponent.vue";
  import LessonsComponent from "src/components/LessonsComponent.vue";
  import CoachesComponent from "src/components/CoachesComponent.vue";
  import { useUserStore } from "src/stores/userStore";

  
  export default {
    components: {
      BannerPromoScrolling,
      NotificationBell,
      PlayerNavigationMenu,
      ClubInfoComponent,
      LessonsComponent,
      CoachesComponent,
    },
    setup() {
      const route = useRoute();
      const router = useRouter();
      const $q = useQuasar();
      const clubDetails = ref(null);
      const coordinates = ref(null);
      const loading = ref(false);
      const userStore = useUserStore();
      const days = ref([]);
      const selectedDay = ref("");
      const availableTimes = ref([]);
      const consolidatedTimes = ref([]);
      const selectedTime = ref(null);
      const selectedTab = ref("privatelessons");
      const availableCourts = ref([]);
      const menuVisible = ref(false);
  
      const clubId = route.params.clubId;
  
      onMounted(async () => {
        if (!clubId) {
          console.error("Club ID is undefined");
          return;
        }
  
        try {
          loading.value = true;
          const { data, error } = await supabase
            .from("clubs")
            .select("*, geolocation, latitude, longitude, city, state, country")
            .eq("id", clubId)
            .single();
  
          if (error) {
            throw error;
          }
  
          clubDetails.value = data;
  
          if (data?.geolocation?.coordinates) {
            coordinates.value = {
              lat: data.geolocation.coordinates[1],
              lng: data.geolocation.coordinates[0],
            };
          } else if (data.latitude && data.longitude) {
            coordinates.value = {
              lat: data.latitude,
              lng: data.longitude,
            };
          } else {
            console.error("No valid coordinates available");
          }
  
          if (route.params.tab) {
            selectedTab.value = route.params.tab;
          } else if (route.query.tab){
            selectedTab.value = route.query.tab;
          }
  
  
          if (selectedTab.value === "info" && coordinates.value) {
            setTimeout(() => {
              const mapElement = document.getElementById("map");
              if (mapElement && !mapElement._leaflet_id) {
                initMap(coordinates.value);
              }
            }, 100); // Espera a que el contenedor esté completamente renderizado
          }
          
        } catch (error) {
          console.error("Error al obtener detalles del club:", error.message);
          $q.notify({
            type: "negative",
            message: "Error al cargar detalles del club.",
          });
        } finally {
          loading.value = false;
        }
      });

  
      const initMap = ({ lat, lng }) => {
        const mapElement = document.getElementById("map");
        if (!mapElement || mapElement._leaflet_id) {
          return; // Si el mapa ya está inicializado, no lo reinicialices
        }
  
        const map = L.map("map").setView([lat, lng], 15);
  
        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
          attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        }).addTo(map);
  
        L.marker([lat, lng]).addTo(map)
          .bindPopup(clubDetails.value.name)
          .openPopup();
      };

      const goBack = () => {
        router.back()
      };

      watch(selectedTab, (newTab) => {
        if (newTab === "info" && coordinates.value) {
          setTimeout(() => {
            const mapElement = document.getElementById("map");
            if (mapElement && !mapElement._leaflet_id) {
              initMap(coordinates.value);
            }
          }, 100);
        }
      });

  
      return {
        clubDetails,
        coordinates,
        loading,
        days,
        selectedDay,
        availableTimes,
        consolidatedTimes,
        selectedTime,
        availableCourts,
        selectedTab,
        menuVisible,
        userStore,
      };
    },
  };
  </script>
  
  <style scoped>
  .club-logo {
    width: 300px;
    border-radius: 8px;
    margin-bottom: 16px;
  }
  .court-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
    gap: 8px;
    justify-content: center;
    margin-top: 16px;
  }
  
  .logo-icon {
      width: 60px; /* Ajusta el tamaño del logo */
      height: 60px;
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
  
  .tabs-section {
    margin-bottom: 10px;
    background-image: url(../../assets/texturafondo.png);
    background-size: cover;
    border-radius: 20px;
  }
  
  </style>
  