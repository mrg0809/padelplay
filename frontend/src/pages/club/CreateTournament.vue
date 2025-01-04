<template>
  <q-layout view="hHh lpR fFf" class="bg-dark text-white">
    <q-header class="bg-primary text-white">
      <q-toolbar>
        <q-toolbar-title>Crear Torneo</q-toolbar-title>
        <q-btn flat round icon="arrow_back" @click="goBack" label="REGRESAR" />
      </q-toolbar>
    </q-header>

    <q-page-container>
      <q-page class="q-pa-md">
        <q-form @submit.prevent="createTournament">
          <!-- Sección de Detalles del Torneo -->
          <q-card flat bordered class="q-mb-lg bg-dark text-white">
            <q-card-section>
              <h3>Detalles del Torneo</h3>
            </q-card-section>
            <q-card-section>
              <q-input v-model="form.name" label="Nombre del Torneo" outlined dense class="q-mb-md" />
              <q-input v-model="form.start_date" label="Fecha de Inicio" type="date" outlined dense class="q-mb-md" />
              <q-input v-model="form.start_time" label="Hora de Inicio" type="time" outlined dense class="q-mb-md" />
              <q-select v-model="form.category" :options="categories" label="Categoría" outlined dense class="q-mb-md" />
              <q-select v-model="form.gender" :options="genders" label="Género" outlined dense class="q-mb-md" />
              <q-select v-model="form.system" :options="systems" label="Sistema de Competencia" outlined dense class="q-mb-md" />
              <q-input v-model.number="form.min_pairs" label="Mínimo de Parejas" type="number" outlined dense class="q-mb-md" />
              <q-input v-model.number="form.max_pairs" label="Máximo de Parejas" type="number" outlined dense class="q-mb-md" />
            </q-card-section>
          </q-card>

          <!-- Sección de Canchas -->
          <q-card flat bordered class="q-mb-lg bg-dark text-white">
            <q-card-section>
              <h3>Canchas</h3>
              <div class="q-mb-sm">
                <q-checkbox
                  v-model="selectAllCourts"
                  label="Seleccionar todas las canchas"
                  @update:model-value="toggleSelectAll"
                />
              </div>
            </q-card-section>
            <q-card-section>
              <q-checkbox
                v-for="court in courts"
                :key="court.id"
                v-model="form.courts_used"
                :label="court.name"
                :val="court.id"
                outlined
                dense
                class="q-mb-sm"
              />
            </q-card-section>
          </q-card>

          <!-- Sección de Detalles Financieros -->
          <q-card flat bordered class="q-mb-lg bg-dark text-white">
            <q-card-section>
              <h3>Detalles Financieros</h3>
            </q-card-section>
            <q-card-section>
              <q-input
                v-model.number="form.price_per_pair"
                label="Precio por Pareja"
                type="number"
                outlined
                dense
                class="q-mb-md"
              />
              <q-input
                v-model="form.prize"
                label="Premio"
                outlined
                dense
                class="q-mb-md"
              />
              <div class="q-pa-sm text-white">
                <p><strong>Ganancias Potenciales:</strong> {{ potentialEarnings }} MXN</p>
              </div>
            </q-card-section>
          </q-card>

          <q-btn type="submit" label="Crear Torneo" color="primary" class="q-mt-md full-width" />
        </q-form>
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
import api from "../../api"; // Asegúrate de importar tu configuración de API
import { supabase } from "src/services/supabase";

export default {
  name: "CreateTournament",
  data() {
    return {
      form: {
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
      },
      categories: ["primera", "segunda", "tercera", "cuarta", "quinta", "libre"],
      genders: ["mixto", "varonil", "femenil"],
      systems: ["eliminacion directa", "round robin", "combinado"],
      courts: [],
      selectAllCourts: false,
      tabs: [
          { name: "inicio", label: "Inicio", icon: "home" },
          { name: "torneos", label: "Torneos", icon: "sports_tennis" },
          { name: "perfil", label: "Perfil", icon: "account_circle" },
        ],
    };
  },
  async mounted() {
    const token = localStorage.getItem("token");
    if (token) {
      const base64Url = token.split(".")[1];
      const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
      const payload = JSON.parse(atob(base64));
      this.clubId = payload.club_id || null;
    }

    const { data, error } = await supabase.from("courts").select("id, name").eq("club_id", this.clubId);
    if (!error) this.courts = data;
  },
  methods: {
    toggleSelectAll(selected) {
      this.form.courts_used = selected ? this.courts.map(court => court.id) : [];
    },
    async createTournament() {
      try {
        // Enviar datos al backend
        const response = await api.post("/tournaments/", {
          ...this.form,
          club_id: this.clubId,
        });

        if (response.status === 201) {
          this.$q.notify({ type: "positive", message: "Torneo creado exitosamente" });
          this.$router.push("/dashboard/club");
        } else {
          throw new Error(response.data.detail || "Error al crear el torneo");
        }
      } catch (err) {
        this.$q.notify({ type: "negative", message: `Error: ${err.message}` });
      }
    },
    onTabChange(tabName) {
        this.$router.push(`/club/${tabName}`);
      },
      goBack() {
      this.$router.back();
    },
  },
  computed: {
    potentialEarnings() {
      const { price_per_pair, max_pairs, prize } = this.form;
      return price_per_pair && max_pairs
        ? price_per_pair * max_pairs - parseFloat(prize || 0)
        : 0;
    },
  },
};
</script>


<style scoped>
.q-layout {
  min-height: 100vh;
}
.q-input,
.q-select,
.q-checkbox {
  color: white;
}
.q-input__bottom {
  border-color: white;
}
</style>
