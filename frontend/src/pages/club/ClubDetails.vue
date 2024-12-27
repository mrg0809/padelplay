<template>
    <q-layout view="hHh lpR fFf" class="bg-dark text-white">
      <q-header elevated class="bg-primary text-white">
        <q-toolbar>
          <q-btn flat round dense icon="arrow_back" @click="goBack" />
          <q-toolbar-title>{{ clubDetails?.name || "Detalles del Club" }}</q-toolbar-title>
        </q-toolbar>
      </q-header>
  
      <q-page-container>
        <q-page class="q-pa-md">
          <div v-if="loading" class="text-center">
            <q-spinner-dots color="primary" size="lg" />
          </div>
          <div v-else>
            <div class="q-mb-md text-center">
              <img
                v-if="clubDetails?.logo_url"
                :src="clubDetails.logo_url"
                alt="Club Logo"
                class="q-mb-md"
                style="max-width: 200px; border-radius: 8px;"
              />
              <p><strong>Dirección:</strong> {{ clubDetails?.address || "No disponible" }}</p>
              <p v-if="clubDetails?.city"><strong>Ciudad:</strong> {{ clubDetails.city }}</p>
              <p v-if="clubDetails?.state"><strong>Estado:</strong> {{ clubDetails.state }}</p>
              <p v-if="clubDetails?.country"><strong>País:</strong> {{ clubDetails.country }}</p>
            </div>
  
            <q-btn
              v-if="coordinates"
              label="Cómo llegar"
              color="primary"
              class="full-width q-mt-md"
              icon="navigation"
              @click="openMaps(coordinates)"
            />
          </div>
        </q-page>
      </q-page-container>
    </q-layout>
  </template>
  
  <script>
  import { ref, onMounted } from "vue";
  import { supabase } from "../../services/supabase";
  import { useRoute } from "vue-router";
  import { useQuasar } from "quasar";
  
  export default {
    setup() {
      const route = useRoute();
      const $q = useQuasar();
      const clubDetails = ref(null);
      const coordinates = ref(null);
      const loading = ref(false);
  
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
  
          // Extraer coordenadas de geolocation o lat/lng
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
  
      const openMaps = ({ lat, lng }) => {
        if (!lat || !lng) {
          console.error("Invalid coordinates:", { lat, lng });
          return;
        }
        const mapsUrl = `https://www.google.com/maps?q=${lat},${lng}`;
        window.open(mapsUrl, "_blank");
      };
  
      return {
        clubDetails,
        coordinates,
        loading,
        openMaps,
      };
    },
    methods: {
      goBack() {
        this.$router.back();
      },
    },
  };
  </script>
  
  
  
  <style scoped>
  .club-logo {
    max-width: 150px;
    border-radius: 8px;
    margin-bottom: 16px;
  }
  .content {
    text-align: center;
  }
  </style>
  