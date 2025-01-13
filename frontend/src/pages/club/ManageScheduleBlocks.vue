<template>
    <q-layout view="hHh lpR fFf" class="bg-dark text-white">
      <q-header class="bg-primary text-white">
        <q-toolbar>
          <q-toolbar-title>Bloqueo de horarios</q-toolbar-title>
          <q-btn flat round icon="arrow_back" @click="goBack" label="REGRESAR" />
        </q-toolbar>
      </q-header>
  
      <q-page-container>
        <q-page class="q-pa-md">
          <q-card class="bg-dark text-white">
            <h3>Bloqueos:</h3>
            <q-card-section>
                <q-btn
                label="Bloquear club"
                color="deep-orange"
                class="full-width"
                glossy
                @click="goToBlockClubPage"
                />               
            </q-card-section>
            <q-card-section>
                <q-btn
                label="Bloquear cancha"
                color="deep-orange"
                class="full-width"
                glossy
                @click="goToBlockCourtPage"
                />               
            </q-card-section>
            <q-card-section>
                <q-btn
                label="Ver bloqueos"
                color="deep-orange"
                class="full-width"
                glossy
                @click="goToSeeBlockedDays"
                />               
            </q-card-section>
          </q-card>
  
          <!-- Diálogo para bloquear cancha -->
          <q-dialog v-model="blockClubDialogVisible">
            <q-card class="bg-dark text-white">
                <q-card-section>
                <div class="text-h6">Bloquear Club</div>

                <q-select
                    v-model="blockType"
                    :options="['Fecha', 'Rango']"
                    label="Tipo de bloqueo"
                    outlined
                    dense
                    class="q-mb-md"
                />

                <div v-if="blockType === 'Fecha'" class="q-gutter-y-md">
                    <q-date v-model="blockClubData.start_date" label="Fecha" color="orange" dark dense />
                </div>

                <div v-if="blockType === 'Rango'" class="q-gutter-y-md">
                    <q-input v-model="blockClubData.start_date" label="Fecha de Inicio" outlined dense mask="####-##-##">
                    <template v-slot:append>
                        <q-icon name="event" class="cursor-pointer">
                        <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                            <q-date v-model="blockClubData.start_date" mask="YYYY-MM-DD" />
                        </q-popup-proxy>
                        </q-icon>
                    </template>
                    </q-input>
                    <q-input v-model="blockClubData.start_time" label="Hora de Inicio" outlined dense mask="##:##">
                    <template v-slot:append>
                        <q-icon name="access_time" class="cursor-pointer">
                        <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                            <q-time v-model="blockClubData.start_time" mask="HH:mm" format24h />
                        </q-popup-proxy>
                        </q-icon>
                    </template>
                    </q-input>
                    <q-input v-model="blockClubData.end_date" label="Fecha de Fin" outlined dense mask="####-##-##">
                    <template v-slot:append>
                        <q-icon name="event" class="cursor-pointer">
                        <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                            <q-date v-model="blockClubData.end_date" mask="YYYY-MM-DD" />
                        </q-popup-proxy>
                        </q-icon>
                    </template>
                    </q-input>
                    <q-input v-model="blockClubData.end_time" label="Hora de Fin" outlined dense mask="##:##">
                    <template v-slot:append>
                        <q-icon name="access_time" class="cursor-pointer">
                        <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                            <q-time v-model="blockClubData.end_time" mask="HH:mm" format24h />
                        </q-popup-proxy>
                        </q-icon>
                    </template>
                    </q-input>
                </div>


                <q-input v-model="blockClubData.reason" label="Motivo" outlined dense class="q-mt-md" />
                </q-card-section>
                <q-card-actions align="right">
                <q-btn flat label="Cancelar" color="primary" v-close-popup />
                <q-btn flat label="Bloquear" color="negative" @click="blockClub" /> 
                </q-card-actions>
            </q-card>
          </q-dialog>

          <q-dialog v-model="blockCourtDialogVisible">
            <q-card class="bg-dark text-white">
                <q-card-section>
                <div class="text-h6">Bloquear Cancha</div>

                <q-select
                    v-model="blockCourtData.court_id"
                    :options="courts"
                    option-label="name"
                    option-value="id"
                    label="Seleccionar Cancha"
                    outlined
                    dense
                    class="q-mb-md"
                />

                <q-select
                    v-model="blockType"
                    :options="['Fecha', 'Rango']"
                    label="Tipo de bloqueo"
                    outlined
                    dense
                    class="q-mb-md"
                />

                <div v-if="blockType === 'Fecha'" class="q-gutter-y-md">
                    <q-date v-model="blockCourtData.start_date" label="Fecha" color="orange" dark dense />
                </div>

                <div v-if="blockType === 'Rango'" class="q-gutter-y-md">
                    <q-input
                    v-model="blockCourtData.start_date"
                    label="Fecha de Inicio"
                    outlined
                    dense
                    mask="####-##-##"
                    >
                    <template v-slot:append>
                        <q-icon name="event" class="cursor-pointer">
                        <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                            <q-date v-model="blockCourtData.start_date" mask="YYYY-MM-DD" />
                        </q-popup-proxy>
                        </q-icon>
                    </template>
                    </q-input>
                    <q-input
                    v-model="blockCourtData.start_time"
                    label="Hora de Inicio"
                    outlined
                    dense
                    mask="##:##"
                    >
                    <template v-slot:append>
                        <q-icon name="access_time" class="cursor-pointer">
                        <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                            <q-time v-model="blockCourtData.start_time" mask="HH:mm" format24h />
                        </q-popup-proxy>
                        </q-icon>
                    </template>
                    </q-input>
                    <q-input
                    v-model="blockCourtData.end_date"
                    label="Fecha de Fin"
                    outlined
                    dense
                    mask="####-##-##"
                    >
                    <template v-slot:append>
                        <q-icon name="event" class="cursor-pointer">
                        <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                            <q-date v-model="blockCourtData.end_date" mask="YYYY-MM-DD" />
                        </q-popup-proxy>
                        </q-icon>
                    </template>
                    </q-input>
                    <q-input
                    v-model="blockCourtData.end_time"
                    label="Hora de Fin"
                    outlined
                    dense
                    mask="##:##"
                    >
                    <template v-slot:append>
                        <q-icon name="access_time" class="cursor-pointer">
                        <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                            <q-time v-model="blockCourtData.end_time" mask="HH:mm" format24h />
                        </q-popup-proxy>
                        </q-icon>
                    </template>
                    </q-input>
                </div>

                <q-input
                    v-model="blockCourtData.reason"
                    label="Motivo"
                    outlined
                    dense
                    class="q-mt-md"
                />
                </q-card-section>
                <q-card-actions align="right">
                <q-btn flat label="Cancelar" color="primary" v-close-popup />
                <q-btn flat label="Bloquear" color="negative" @click="blockCourt" />
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
     confirmDialogVisible: false,
     blockCourtDialogVisible: false,
     blockClubDialogVisible: false,
     blockClubData: {
       block_type: null, 
       start_date: null,
       start_time: null,
       end_date: null,
       end_time: null,
       reason: "",
     },
     blockCourtData: { 
       block_type: null, 
       court_id: null, 
       start_date: null,
       start_time: null,
       end_date: null,
       end_time: null,
       reason: "",
     },
     blockType: 'Fecha',
     courts: [],
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
         club_id: court.club_id,
       }));
     } catch (error) {
       console.error("Error al obtener las canchas:", error);
     }
   },
   goToBlockClubPage() {
    this.blockClubDialogVisible=true
   },
   goToBlockCourtPage() {
    this.blockCourtDialogVisible=true
   },
   goToSeeBlockedDays() {
    console.log("see blocked days")
   },
   goBack() {
     this.$router.back();
   },
   async blockClub() {
    try {
        // Validar datos antes de enviarlos
        if (this.blockType === "Fecha" && !this.blockClubData.start_date) {
        return this.$q.notify({ type: "negative", message: "Selecciona una fecha" });
        }
        if (
        this.blockType === "Rango" &&
        (!this.blockClubData.start_date || !this.blockClubData.end_date)
        ) {
        return this.$q.notify({
            type: "negative",
            message: "Selecciona un rango de fechas válido",
        });
        } 

        let startDate = this.blockClubData.start_date;
        let endDate = this.blockClubData.end_date;
        let startTime = this.blockClubData.start_time;
        let endTime = this.blockClubData.end_time;

        if (this.blockType === "Fecha") {
            startDate = endDate = this.blockClubData.start_date;
            startTime = "00:00"; // Primer minuto del día
            endTime = "23:59";   // Último minuto del día
        }

        const courts = this.courts

        const payload = {
            courts: courts.map(court => court.id),
            club_id: this.courts[0].club_id, 
            start_date: startDate,
            start_time: startTime,
            end_date: endDate,
            end_time: endTime,
            reason: this.blockClubData.reason,
        };
        
        await api.post("/block/block-club", payload); // Enviar la solicitud al backend
        

        this.$q.notify({ type: "positive", message: "Club bloqueado exitosamente" });

        // Limpiar los datos y cerrar el diálogo
        this.blockClubDialogVisible = false;
        this.blockClubData = {
        club_id: null,
        start_date: null,
        start_time: null,
        end_date: null,
        end_time: null,
        reason: "",
        };
    } catch (error) {
        console.error("Error al bloquear el club:", error);
        this.$q.notify({
        type: "negative",
        message: "Error al bloquear el club. Intenta nuevamente.",
        });
    }
    },
   async blockCourt() {
    try {
      // Validar datos antes de enviarlos
      if (!this.blockCourtData.court_id) {
        return this.$q.notify({ type: "negative", message: "Selecciona una cancha" });
      }
      if (this.blockType === "Fecha" && !this.blockCourtData.start_date) {
        return this.$q.notify({ type: "negative", message: "Selecciona una fecha" });
      }
      if (
        this.blockType === "Rango" &&
        (!this.blockCourtData.start_date || !this.blockCourtData.end_date)
      ) {
        return this.$q.notify({
          type: "negative",
          message: "Selecciona un rango de fechas válido",
        });
      }

      let startDate = this.blockCourtData.start_date;
      let endDate = this.blockCourtData.end_date;
      let startTime = this.blockCourtData.start_time;
      let endTime = this.blockCourtData.end_time;

      if (this.blockType === "Fecha") {
        startDate = endDate = this.blockCourtData.start_date;
        startTime = "00:00";
        endTime = "23:59";
      }
      // Enviar datos al backend
      const payload = {
        court_id: this.blockCourtData.court_id.id,
        club_id: this.courts[0].club_id,
        start_date: startDate,
        start_time: startTime,
        end_date: endDate,
        end_time: endTime,
        reason: this.blockCourtData.reason,
      };

      await api.post("/block/block-court", payload);
      this.$q.notify({ type: "positive", message: "Cancha bloqueada exitosamente" });

      // Limpiar los datos y cerrar el diálogo
      this.blockCourtDialogVisible = false;
      this.blockCourtData = {
        court_id: null,
        club_id: null,
        date: null,
        start_date: null,
        start_time: null,
        end_date: null,
        end_time: null,
        reason: "",
      };
    } catch (error) {
      console.error("Error al bloquear la cancha:", error);
      this.$q.notify({
        type: "negative",
        message: "Error al bloquear la cancha. Intenta nuevamente.",
      });
    }
  },
 },
 mounted() {
   this.fetchCourts();
 },
};


 </script>