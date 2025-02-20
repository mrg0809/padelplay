<template>
  <q-layout view="hHh lpR fFf" class="body text-white">
    <q-header elevated class="bg-primary text-white">
      <div class="header-content">
        <div class="greeting">
          <img src="/src/assets/padelplay.png" alt="Logo" class="logo-icon" />
          Crear Torneo
        </div>
        <div class="header-icons">
          <q-btn flat round icon="arrow_back" @click="goBack" />
        </div>
      </div>
    </q-header>

    <q-page-container>
      <q-page class="q-pa-md">
        <q-form @submit.prevent="createTournament">
          <!-- Sección de Detalles del Torneo -->
          <q-card flat bordered class="q-mb-lg bg-transparent text-white">
            <q-card-section>
              <h3>Detalles del Torneo</h3>
            </q-card-section>
            <q-card-section>
              <q-input v-model="form.name" label="Nombre del Torneo" outlined dense class="q-mb-md" />
              <q-input v-model="form.start_date" label="Fecha de Inicio" type="date" outlined dense class="q-mb-md" />
              <q-input v-model="form.start_time" label="Hora de Inicio" type="time" outlined dense class="q-mb-md" />
              <q-input v-model="form.end_date" label="Fecha de Fin" type="date" outlined dense class="q-mb-md" />
              <q-input v-model="form.end_time" label="Hora de Fin" type="time" outlined dense class="q-mb-md" />
              <q-select v-model="form.category" :options="categories" label="Categoría" outlined dense class="q-mb-md" />
              <q-select v-model="form.gender" :options="genders" label="Género" outlined dense class="q-mb-md" />
              <q-select v-model="form.system" :options="systems" label="Sistema de Competencia" outlined dense class="q-mb-md" />
              <q-input v-model.number="form.min_pairs" label="Mínimo de Parejas" type="number" outlined dense class="q-mb-md" />
              <q-input v-model.number="form.max_pairs" label="Máximo de Parejas" type="number" outlined dense class="q-mb-md" />
            </q-card-section>
          </q-card>

          <!-- Sección de Canchas -->
          <q-card flat bordered class="q-mb-lg bg-transparent text-white">
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
          <q-card flat bordered class="q-mb-lg bg-transparent text-white">
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
    <ClubNavigationMenu />
  </q-layout>
</template>

<script>
import ClubNavigationMenu from "src/components/ClubNavigationMenu.vue";
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
        end_date: "",
        end_time: "",
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
      systems: ["combinado", "eliminacion directa", "liga", "round-robin"],
      courts: [],
      selectAllCourts: false,
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
  components:{
    ClubNavigationMenu,
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
.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  background-color: #000000;
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
  width: 60px;
  height: 60px;
}

.body {
  background-image: url(../../assets/menu/padelcourtfloor.jpg);
  background-size: cover;
}
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
