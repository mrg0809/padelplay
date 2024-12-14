<template>
    <q-layout view="hHh lpR fFf" class="bg-light">
      <q-header class="bg-primary text-white">
        <q-toolbar>
          <q-toolbar-title>Gestionar Horarios</q-toolbar-title>
        </q-toolbar>
      </q-header>
  
      <q-page-container>
        <q-page class="q-pa-md">
          <q-card>
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
              <q-table
                :rows="generalSchedule"
                :columns="columns"
                row-key="day_of_week"
                dense
                bordered
                flat
                hide-bottom
              >
                <template v-slot:body-cell-day="{ index }">
                  {{ daysOfWeek[index] }}
                </template>
                <template v-slot:body-cell-opening_time="{ index }">
                  <q-input
                    v-model="generalSchedule[index].opening_time"
                    type="time"
                    dense
                    outlined
                  />
                </template>
                <template v-slot:body-cell-closing_time="{ index }">
                  <q-input
                    v-model="generalSchedule[index].closing_time"
                    type="time"
                    dense
                    outlined
                  />
                </template>
              </q-table>
            </q-card-section>
  
            <q-card-actions align="right">
              <q-btn label="Guardar Cambios" color="primary" @click="saveSchedules" />
            </q-card-actions>
          </q-card>
        </q-page>
      </q-page-container>
    </q-layout>
  </template>
  
  <script>
  import api from "../../api";
  
  export default {
  data() {
    return {
      selectedCourt: null,
      courts: [],
      generalSchedule: Array(7).fill(null).map(() => ({ 
        opening_time: "", 
        closing_time: "", 
      })), 
      columns: [
        { name: "day", label: "Día", field: "day", align: "left" },
        { name: "opening_time", label: "Hora de Apertura", field: "opening_time", align: "center" },
        { name: "closing_time", label: "Hora de Cierre", field: "closing_time", align: "center" },
      ],
      daysOfWeek: ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"],
    };
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
      if (!this.selectedCourt) return;

      try {
        const response = await api.get("/clubs/schedules", {
          params: { court_id: this.selectedCourt },
        });

        if (response.data?.data?.length > 0) {
          response.data.data.forEach((schedule) => {
            const index = schedule.day_of_week;
            this.generalSchedule[index] = {
              opening_time: schedule.opening_time || "",
              closing_time: schedule.closing_time || "",
            };
          });
        } else {
          // Handle case where no data is received
          this.generalSchedule = Array(7).fill(null).map(() => ({
            opening_time: "",
            closing_time: "",
          })); 
        }
      } catch (error) {
        console.error("Error al obtener los horarios:", error);
      }
    },
    async saveSchedules() {
      // ... (your existing saveSchedules method)
    },
  },
  mounted() {
    this.fetchCourts();
  },
};
</script>