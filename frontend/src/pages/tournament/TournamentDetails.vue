<template>
    <q-layout view="hHh lpR fFf" class="bg-dark text-white">
      <q-header class="bg-primary text-white">
        <q-toolbar>
          <q-toolbar-title>Torneo</q-toolbar-title>
          <q-btn flat round icon="arrow_back" @click="goBack" label="Regresar" />
        </q-toolbar>
      </q-header>
  
      <q-page-container>
        <q-page class="q-pa-md">
          <div v-if="loading" class="text-center">
            <q-spinner-dots color="primary" size="lg" />
          </div>
  
          <div v-else-if="tournament">
            <q-card>
              <q-card-section>
                <h4>{{ tournament.name }}</h4>
                <p><strong>Fecha de inicio:</strong> {{ tournament.start_date }}</p>
                <p><strong>Categoría:</strong> {{ tournament.category }}</p>
                <p><strong>Género:</strong> {{ tournament.gender }}</p>
                <p><strong>Sistema de competencia:</strong> {{ tournament.system }}</p>
                <p><strong>Precio por pareja:</strong> ${{ tournament.price_per_pair }}</p>
                <p><strong>Premio:</strong> {{ tournament.prize }}</p>
              </q-card-section>
  
              <q-card-actions align="center">
                <q-btn
                  label="Inscribirme"
                  color="primary"
                  icon="check_circle"
                  @click="handleEnrollment"
                />
              </q-card-actions>
            </q-card>
          </div>
        </q-page>
      </q-page-container>
    </q-layout>
  </template>
  
  <script>
  import { ref, onMounted } from "vue";
  import { supabase } from "../../services/supabase";
  import { useRoute, useRouter } from "vue-router";
  import { useQuasar } from "quasar";
  
  export default {
    setup() {
      const route = useRoute();
      const router = useRouter();
      const $q = useQuasar();
      const tournament = ref(null);
      const loading = ref(false);
  
      const tournamentId = route.params.tournamentId;
  
      const fetchTournamentDetails = async () => {
        try {
          loading.value = true;
          const { data, error } = await supabase
            .from("tournaments")
            .select("*")
            .eq("id", tournamentId)
            .single();
  
          if (error) throw error;
  
          tournament.value = data;
        } catch (error) {
          console.error("Error al obtener detalles del torneo:", error.message);
          $q.notify({
            type: "negative",
            message: "Error al cargar detalles del torneo.",
          });
        } finally {
          loading.value = false;
        }
      };
  
      const handleEnrollment = () => {
        if (!tournament.value) return;
  
        const enrollmentDetails = {
          tournamentId: tournament.value.id,
          tournamentName: tournament.value.name,
          pricePerPair: tournament.value.price_per_pair,
        };
  
        router.push({
          name: "CheckoutPage",
          query: enrollmentDetails,
        });
      };
  
      const goBack = () => {
        router.back();
      };
  
      onMounted(fetchTournamentDetails);
  
      return {
        tournament,
        loading,
        handleEnrollment,
        goBack,
      };
    },
  };
  </script>
  
  <style scoped>
  .q-layout {
    min-height: 100vh;
  }
  
  .q-card {
    background-color: #1e1e1e !important;
    color: white !important;
  }
  
  .q-btn {
    width: 100%;
  }
  
  ul {
    padding-left: 1.2rem;
  }
  
  ul li {
    list-style-type: disc;
  }
  </style>
  