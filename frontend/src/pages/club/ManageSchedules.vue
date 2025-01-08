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
            <q-btn label="Guardar Cambios" color="primary" @click="confirmSave" />
          </q-card-actions>
        </q-card>

        <!-- Botones adicionales -->
        <div class="q-mt-md">
          <q-btn
            label="Bloqueo de cancha"
            color="deep-orange"
            glossy
            rounded
            @click="openBlockDialog"
          />
          <q-btn
            label="Días festivos"
            color="deep-orange"
            glossy
            rounded
            class="q-ml-md"
            @click="openHolidayDialog"
          />
        </div>

        <!-- Diálogo para bloquear cancha -->
        <q-dialog v-model="blockCourtDialogVisible">
          <q-card>
            <q-card-section>
              <div class="text-h6">Bloquear cancha</div>
              <q-date v-model="blockCourtData.date" label="Fecha" color="orange" dark dense />
              <q-time v-model="blockCourtData.start_time" label="Hora de Inicio" dense />
              <q-time v-model="blockCourtData.end_time" label="Hora de Fin" dense />
              <q-input v-model="blockCourtData.reason" label="Motivo" outlined dense />
            </q-card-section>
            <q-card-actions align="right">
              <q-btn flat label="Cancelar" color="primary" v-close-popup />
              <q-btn flat label="Bloquear" color="negative" @click="blockCourt" />
            </q-card-actions>
          </q-card>
        </q-dialog>

        <!-- Diálogo para días festivos -->
        <q-dialog v-model="holidayDialogVisible">
          <q-card>
            <q-card-section>
              <div class="text-h6">Registrar Día Festivo</div>
              <q-date v-model="holidayData.date" label="Fecha" dense />
              <q-input v-model="holidayData.reason" label="Motivo" outlined dense />
            </q-card-section>
            <q-card-actions align="right">
              <q-btn flat label="Cancelar" color="primary" v-close-popup />
              <q-btn flat label="Guardar" color="negative" @click="blockHoliday" />
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
        is_open: true,
        opening_time: "06:00",
        closing_time: "23:00",
      })),
      daysOfWeek: ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"],
      confirmDialogVisible: false,
      blockCourtDialogVisible: false,
      holidayDialogVisible: false,
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
        is_open: true,
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
    confirmSave() {
      this.confirmDialogVisible = true;
    },
    async saveSchedules(applyToAll) {
      this.confirmDialogVisible = false;

      try {
        await api.post("/clubs/schedules", {
          apply_to_all: applyToAll,
          schedules: this.generalSchedule.map((schedule, index) => ({
            day_of_week: index,
            opening_time: schedule.is_open ? schedule.opening_time : null,
            closing_time: schedule.is_open ? schedule.closing_time : null,
            court_id: applyToAll ? null : this.selectedCourt,
          })),
        });
        this.$q.notify({ type: "positive", message: "Horarios guardados exitosamente" });
      } catch (error) {
        console.error("Error al guardar los horarios:", error);
        this.$q.notify({ type: "negative", message: "Error al guardar los horarios" });
      }
    },
    openBlockDialog() {
      this.blockCourtDialogVisible = true;
    },
    openHolidayDialog() {
      this.holidayDialogVisible = true;
    },
    async blockCourt() {
      try {
        await api.post("/clubs/court-blocks", this.blockCourtData);
        this.blockCourtDialogVisible = false;
        this.$q.notify({ type: "positive", message: "Cancha bloqueada exitosamente." });
      } catch (error) {
        console.error("Error al bloquear la cancha:", error);
        this.$q.notify({ type: "negative", message: "Error al bloquear la cancha." });
      }
    },
    async blockHoliday() {
      try {
        await api.post("/clubs/holiday-blocks", this.holidayData);
        this.holidayDialogVisible = false;
        this.$q.notify({ type: "positive", message: "Día festivo registrado exitosamente." });
      } catch (error) {
        console.error("Error al registrar el día festivo:", error);
        this.$q.notify({ type: "negative", message: "Error al registrar el día festivo." });
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
  