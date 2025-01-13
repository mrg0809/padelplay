<template>
  <q-layout view="hHh lpR fFf" class="bg-dark text-white">
    <q-header class="bg-primary text-white">
      <q-toolbar>
        <q-toolbar-title>Gestionar Horarios</q-toolbar-title>
        <q-btn flat round icon="arrow_back" @click="goBack" label="REGRESAR" />
      </q-toolbar>
    </q-header>

    <q-page-container>
      <q-page class="q-pa-md">
        <q-card class="bg-dark text-white">
          <q-card-section>
            <q-select
              v-model="selectedCourt"
              :options="courts"
              option-label="name"
              option-value="id"
              label="Selecciona una cancha"
              outlined
              dense
              @update:model-value="onCourtChange"
            />
          </q-card-section>

          <q-card-section v-if="selectedCourt">
            <q-list bordered>
              <q-item v-for="(schedule, index) in generalSchedule" :key="index" class="q-mb-md">
                <q-item-section>
                  <div class="text-bold">{{ daysOfWeek[index] }}</div>
                  <q-toggle
                    v-model="generalSchedule[index].is_open"
                    label="¿Abierto?"
                    dense
                    color="orange"
                  />
                </q-item-section>
                <q-item-section v-if="generalSchedule[index].is_open">
                  <q-input
                    v-model="generalSchedule[index].opening_time"
                    label="Hora de Apertura"
                    dense
                    outlined
                  />
                  <q-input
                    v-model="generalSchedule[index].closing_time"
                    label="Hora de Cierre"
                    dense
                    outlined
                  />
                </q-item-section>
              </q-item>
            </q-list>
          </q-card-section>

          <q-card-actions align="right">
            <q-btn label="Guardar Cambios" color="primary" @click="saveOrUpdateSchedules" />
          </q-card-actions>
        </q-card>

        <!-- Botones adicionales -->
        <div class="q-mt-md">
          <q-btn
            label="Establecer bloqueos"
            color="deep-orange"
            class="full-width"
            glossy
            @click="goToBlockPage"
          />
        </div>  
      </q-page>
    </q-page-container>
    <ClubNavigationMenu />
  </q-layout>
</template>

  
  <script>
 import ClubNavigationMenu from "src/components/ClubNavigationMenu.vue";
import api from "../../api";

export default {
  data() {
    return {
      selectedCourt: null,
      courts: [],
      generalSchedule: Array(7).fill(null).map(() => ({
        is_open: false,
        opening_time: "06:00",
        closing_time: "23:00",
      })),
      daysOfWeek: ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"],
      confirmDialogVisible: false,
      blockCourtDialogVisible: false,
      blockCourtData: {
        date: null,
        start_time: null,
        end_time: null,
        reason: "",
      },
      holidayData: {
        date: null,
        reason: "",
      },
    };
  },
  components: {
    ClubNavigationMenu,
  },
  methods: {
    async fetchCourts() {
      try {
        const response = await api.get("/courts");
        this.courts = response.data.map((court) => ({
          id: court.id,
          name: court.name,
        }));
      } catch (error) {
        console.error("Error al obtener las canchas:", error);
      }
    },
    async onCourtChange() {
      this.generalSchedule = Array(7).fill(null).map(() => ({
        is_open: false,
        opening_time: null,
        closing_time: null,
      }));

      if (!this.selectedCourt) return;

      try {
        const response = await api.get("/clubs/schedules", {
          params: { court_id: this.selectedCourt },
        });
        const schedules =response.data.data.filter(schedule => schedule.court_id === this.selectedCourt.id);
        
        if (schedules.length > 0) {
          schedules.forEach((schedule) => {
            const index = schedule.day_of_week;
            this.generalSchedule[index] = {
              is_open: schedule.opening_time !== null && schedule.closing_time !== null,
              opening_time: schedule.opening_time || "06:00",
              closing_time: schedule.closing_time || "23:00",
            };
          });
        }
      } catch (error) {
        console.error("Error al obtener los horarios:", error);
      }
    },

    async saveOrUpdateSchedules() {
      
      if (!this.selectedCourt) {
        this.$q.notify({ type: "negative", message: "Por favor, selecciona una cancha" });
        return;
      }

      try {
        const schedules = this.generalSchedule.map((schedule, index) => ({
          day_of_week: index,
          opening_time: schedule.is_open ? schedule.opening_time : null,
          closing_time: schedule.is_open ? schedule.closing_time : null,
          court_id: this.selectedCourt,
        }));

        // Detectar si hay horarios existentes para la cancha
        const existingSchedules = await api.get("/clubs/schedules", {
          params: { court_id: this.selectedCourt },
        });

        if (existingSchedules.data?.data?.length > 0) {
          // Actualizar horarios existentes (PUT)
          await api.put("/clubs/schedules", {
            court_id: this.selectedCourt,
            schedules: schedules,
          });
          this.$q.notify({ type: "positive", message: "Horarios actualizados exitosamente" });
        } else {
          // Crear nuevos horarios (POST)
          await api.post("/clubs/schedules", {
            schedules: schedules,
          });
          this.$q.notify({ type: "positive", message: "Horarios creados exitosamente" });
        }
      } catch (error) {
        console.error("Error al guardar los horarios:", error.response?.data?.detail || error.message);
        this.$q.notify({ type: "negative", message: "Error al guardar los horarios" });
      }
    },

    goToBlockPage() {
      this.$router.push(`/club/bloqueos`);
    },
    goBack() {
      this.$router.back();
    },
  },
  mounted() {
    this.fetchCourts();
  },
};


  </script>
  