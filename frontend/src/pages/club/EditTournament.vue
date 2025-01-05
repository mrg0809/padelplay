<template>
    <q-layout view="hHh lpR fFf" class="bg-dark text-white">
      <!-- Header -->
      <q-header class="bg-primary text-white">
        <q-toolbar>
          <q-toolbar-title>Editar Torneo</q-toolbar-title>
          <q-btn flat round icon="arrow_back" @click="goBack" label="REGRESAR" />
        </q-toolbar>
      </q-header>
  
      <!-- Page Content -->
      <q-page-container>
        <q-page class="q-pa-md">
          <q-form @submit.prevent="confirmUpdateTournament">
            <div class="form-group">
              <q-input v-model="form.name" label="Nombre del Torneo" outlined dense required />
            </div>
            <div class="form-group">
              <q-input v-model="form.start_date" label="Fecha de Inicio" type="date" outlined dense required />
            </div>
            <div class="form-group">
              <q-input v-model="form.start_time" label="Hora de Inicio" type="time" outlined dense required />
            </div>
            <div class="form-group">
              <q-select v-model="form.category" :options="categories" label="Categoría" outlined dense required />
            </div>
            <div class="form-group">
              <q-select v-model="form.gender" :options="genders" label="Género" outlined dense required />
            </div>
            <div class="form-group">
              <q-select v-model="form.system" :options="systems" label="Sistema de Competencia" outlined dense required />
            </div>
            <div class="form-group">
              <q-input v-model.number="form.min_pairs" label="Mínimo de Parejas" type="number" outlined dense required />
            </div>
            <div class="form-group">
              <q-input v-model.number="form.max_pairs" label="Máximo de Parejas" type="number" outlined dense required />
            </div>
            <div class="form-group">
              <q-input v-model.number="form.price_per_pair" label="Precio por Pareja" type="number" outlined dense required />
            </div>
            <div class="form-group">
              <q-input v-model="form.prize" label="Premio" outlined dense required />
            </div>
            <div class="form-group">
              Selecciona canchas para el torneo:
              <q-checkbox
                v-for="court in courts"
                :key="court.id"
                v-model="form.courts_used"
                :label="court.name"
                :val="court.id"
                outlined
                dense
              />
            </div>
            <q-btn type="submit" label="Guardar Cambios" color="primary" class="q-mt-md" />
          </q-form>
  
          <!-- Confirm Dialog -->
          <q-dialog v-model="confirmDialogVisible">
            <q-card>
              <q-card-section>
                <div class="text-h6">¿Estás seguro de guardar los cambios?</div>
              </q-card-section>
              <q-card-actions align="right">
                <q-btn flat label="Cancelar" color="negative" v-close-popup />
                <q-btn flat label="Confirmar" color="positive" @click="updateTournament" />
              </q-card-actions>
            </q-card>
          </q-dialog>
        </q-page>
      </q-page-container>
  
      <!-- Footer Navigation Tabs -->
      <q-footer class="bg-primary text-white">
        <q-tabs align="justify" class="q-pa-xs" active-color="white" @update:model-value="onTabChange">
          <q-tab v-for="tab in tabs" :key="tab.name" :name="tab.name" :label="tab.label" :icon="tab.icon" class="text-white" />
        </q-tabs>
      </q-footer>
    </q-layout>
  </template>
  
  <script>
  import { supabase } from "src/services/supabase";
  import { ref, onMounted } from "vue";
  import { useRouter, useRoute } from "vue-router";
  import { useQuasar } from "quasar";
  import api from "../../api";
  
  export default {
    name: "EditTournament",
    setup() {
      const router = useRouter();
      const route = useRoute();
      const $q = useQuasar();
  
      const form = ref({
        name: "",
        start_date: "",
        start_time: "",
        category: "",
        gender: "",
        system: "",
        min_pairs: null,
        max_pairs: null,
        price_per_pair: null,
        prize: "",
        courts_used: [],
      });
  
      const categories = ref(["primera", "segunda", "tercera", "cuarta", "quinta", "libre"]);
      const genders = ref(["mixto", "varonil", "femenil"]);
      const systems = ref(["eliminacion directa", "round robin", "combinado"]);
      const courts = ref([]);
      const tournamentId = route.params.tournamentId;
      const confirmDialogVisible = ref(false);
  
      const fetchTournamentDetails = async () => {
        try {
          const { data, error } = await supabase.from("tournaments").select("*").eq("id", tournamentId).single();
          if (error) throw error;
          form.value = { ...data };
        } catch (err) {
          console.error("Error al obtener detalles del torneo:", err.message);
        }
      };
  
      const fetchCourts = async () => {
        try {
          const token = localStorage.getItem("token");
          if (token) {
            const base64Url = token.split(".")[1];
            const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
            const payload = JSON.parse(atob(base64));
            const clubId = payload.club_id;
  
            const { data, error } = await supabase.from("courts").select("id, name").eq("club_id", clubId);
            if (error) throw error;
            courts.value = data;
          }
        } catch (err) {
          console.error("Error al obtener canchas:", err.message);
        }
      };
  
      const confirmUpdateTournament = () => {
        confirmDialogVisible.value = true;
      };
  
      const updateTournament = async () => {
        try {
          confirmDialogVisible.value = false;

          const response = await api.put(`/tournaments/${tournamentId}`, form.value);

          if (response.status === 200) {
            console.log("200 ok")
            $q.notify({ type: "positive", message: "Torneo actualizado exitosamente." });
            router.push("/dashboard/club");
          } else {
            throw new Error("Error al actualizar el torneo.");
          }
        } catch (err) {
          console.error("Error al actualizar torneo:", err.message);
          $q.notify({ type: "negative", message: "Error al actualizar el torneo." });
        }
      };
  
      const goBack = () => {
        router.back();
      };
  
      const onTabChange = (tabName) => {
        router.push(`/club/${tabName}`);
      };
  
      onMounted(() => {
        fetchTournamentDetails();
        fetchCourts();
      });
  
      return {
        form,
        categories,
        genders,
        systems,
        courts,
        updateTournament,
        confirmUpdateTournament,
        confirmDialogVisible,
        goBack,
        onTabChange,
        tabs: [
          { name: "inicio", label: "Inicio", icon: "home" },
          { name: "torneos", label: "Torneos", icon: "sports_tennis" },
          { name: "perfil", label: "Perfil", icon: "account_circle" },
        ],
      };
    },
  };
  </script>
  
  <style scoped>
  .form-group {
    margin-bottom: 15px;
  }
  
  .q-card:hover {
    background-color: #292929;
  }
  </style>
  