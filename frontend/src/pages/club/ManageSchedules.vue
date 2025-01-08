<template>
    <q-layout view="hHh lpR fFf" class="bg-light">
      <q-header class="bg-primary text-white">
        <q-toolbar>
          <q-toolbar-title>Gestionar Horarios</q-toolbar-title>
          <q-btn flat round icon="arrow_back" @click="goBack" label="REGRESAR" />
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
              <q-list bordered>
                <q-item v-for="(schedule, index) in generalSchedule" :key="index" class="q-mb-md">
                  <q-item-section>
                    <div class="text-bold">{{ daysOfWeek[index] }}</div>
                  </q-item-section>
                  <q-item-section>
                    <q-input
                      v-model="generalSchedule[index].opening_time"
                      label="Hora de Apertura"
                      dense
                      outlined
                    />
                  </q-item-section>
                  <q-item-section>
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
              <q-btn label="Guardar Cambios" color="primary" @click="confirmSave" />
            </q-card-actions>
          </q-card>
  
          <!-- Diálogo de confirmación -->
          <q-dialog v-model="confirmDialogVisible">
            <q-card>
              <q-card-section>
                <div class="text-h6">¿Deseas replicar los horarios en todas las canchas del club?</div>
              </q-card-section>
  
              <q-card-actions align="around">
                <q-btn flat label="Solo esta cancha" color="primary" @click="saveSchedules(false)" />
                <q-btn flat label="Todas las canchas" color="primary" @click="saveSchedules(true)" />
              </q-card-actions>
            </q-card>
          </q-dialog>
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
          opening_time: "06:00",
          closing_time: "23:00",
        })),
        columns: [
          { name: "day", label: "Día", field: "day", align: "left" },
          { name: "opening_time", label: "Hora de Apertura", field: "opening_time", align: "center" },
          { name: "closing_time", label: "Hora de Cierre", field: "closing_time", align: "center" },
        ],
        daysOfWeek: ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"],
        confirmDialogVisible: false, // Controla la visibilidad del diálogo
      };
    },
    components: {
      ClubNavigationMenu
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
          opening_time: "06:00",
          closing_time: "23:00",
        }));
  
        if (!this.selectedCourt) return;
  
        try {
          const response = await api.get("/clubs/schedules", {
            params: { court_id: this.selectedCourt },
          });
  
          if (response.data?.data?.length > 0) {
            response.data.data.forEach((schedule) => {
              const index = schedule.day_of_week;
              this.generalSchedule[index] = {
                opening_time: schedule.opening_time || "06:00",
                closing_time: schedule.closing_time || "23:00",
              };
            });
          }
        } catch (error) {
          console.error("Error al obtener los horarios:", error);
        }
      },
      confirmSave() {
        // Mostrar el diálogo de confirmación
        this.confirmDialogVisible = true;
      },
      async saveSchedules(applyToAll) {
        // Cerrar el diálogo
        this.confirmDialogVisible = false;
  
        try {
          await api.post("/clubs/schedules", {
            apply_to_all: applyToAll,
            schedules: this.generalSchedule.map((schedule, index) => ({
              ...schedule,
              day_of_week: index,
              court_id: applyToAll ? null : this.selectedCourt,
            })),
          });
          this.$q.notify({ type: "positive", message: "Horarios guardados exitosamente" });
        } catch (error) {
          console.error("Error al guardar los horarios:", error);
          this.$q.notify({ type: "negative", message: "Error al guardar los horarios" });
        }
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
  