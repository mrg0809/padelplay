<template>
  <q-layout view="hHh lpR fFf" class="body text-black">
    <q-header elevated class="bg-primary text-white">
      <div class="header-content">
        <div class="greeting">
          <img src="/src/assets/padelplay.png" alt="Logo" class="logo-icon" />
          Bloquear horarios
        </div>
        <div class="header-icons">
          <q-btn flat round icon="close" @click="goBack" />
        </div>
      </div>
    </q-header>

    <q-page-container>
      <q-page class="q-pa-md">
        <!-- Tabla de bloqueos futuros -->
        <q-card class="transparent-card q-mb-md">
          <q-card-section>
            <div class="text-h6">Bloqueos Futuros</div>
          </q-card-section>
          <q-card-section>
            <!-- Spinner mientras se cargan los datos -->
            <div v-if="loading" class="text-center q-pa-md">
              <q-spinner color="primary" size="xl" />
              <p class="q-mt-sm">Cargando bloqueos...</p>
            </div>

            <!-- Mensaje si no hay bloqueos -->
            <div
              v-else-if="futureBlocks.length === 0"
              class="text-center q-pa-md"
            >
              <q-icon name="o_event_busy" size="2em" />
              <p class="q-mt-sm">No tienes bloqueos programados.</p>
            </div>

            <!-- Tabla si hay datos -->
            <q-table
              v-else
              :rows="futureBlocks"
              :columns="columns"
              row-key="id"
              flat
              bordered
              class="transparent-table"
            >
              <template v-slot:body-cell-actions="props">
                <q-td :props="props">
                  <q-btn
                    flat
                    round
                    color="negative"
                    icon="delete"
                    @click="deleteBlock(props.row.id)"
                  />
                </q-td>
              </template>
            </q-table>
          </q-card-section>
        </q-card>

        <!-- Botón flotante con menú desplegable -->
        <q-btn
          glossy
          round
          size="lg"
          color="black"
          icon="add"
          class="fixed-bottom-right q-mb-xl"
        >
          <q-menu anchor="top end" self="bottom end">
            <q-list style="min-width: 150px">
              <q-item clickable v-close-popup @click="goToBlockClubPage">
                <q-icon name="o_block" size="md" rounded />
                <q-item-section><strong>Bloquear club</strong></q-item-section>
              </q-item>
              <q-item clickable v-close-popup @click="goToBlockCourtPage">
                <q-icon name="o_event_busy" size="md" rounded />
                <q-item-section><strong>Bloquear cancha</strong></q-item-section>
              </q-item>
            </q-list>
          </q-menu>
        </q-btn>

          <!-- bloquear cancha -->
          <q-dialog v-model="blockClubDialogVisible">
            <q-card class="bg-black text-white">
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
                    <q-date v-model="blockClubData.start_date" label="Fecha" dense />
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
            <q-card class="bg-black text-white">
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
                    <q-date v-model="blockCourtData.start_date" label="Fecha" dense color="orange" />
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
import { supabase } from "src/services/supabase";
import { getUserFromToken } from "src/api";

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
      blockType: "Fecha",
      courts: [],
      futureBlocks: [], // Almacena los bloqueos futuros
      loading: false, // Estado de carga
      columns: [
        {
          name: "court_name",
          label: "Cancha",
          field: "court_name",
          align: "left",
        },
        {
          name: "start_date",
          label: "Fecha Inicio",
          field: "start_date",
          align: "left",
        },
        {
          name: "start_time",
          label: "Hora Inicio",
          field: "start_time",
          align: "left",
        },
        {
          name: "end_date",
          label: "Fecha Fin",
          field: "end_date",
          align: "left",
        },
        {
          name: "end_time",
          label: "Hora Fin",
          field: "end_time",
          align: "left",
        },
        {
          name: "reason",
          label: "Razón",
          field: "reason",
          align: "left",
        },
        {
          name: "actions",
          label: "Acciones",
          field: "actions",
          align: "center",
        },
      ],
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
    async fetchFutureBlocks() {
      this.loading = true; // Activar el spinner
      try {
        const user = getUserFromToken(); // Obtener el usuario logueado
        if (!user || !user.club_id) {
          throw new Error("No se pudo obtener el club_id del usuario.");
        }

        const today = new Date().toISOString().split("T")[0]; // Fecha actual en formato YYYY-MM-DD
        const { data, error } = await supabase
          .from("court_blocks")
          .select("*, courts(name)")
          .eq("club_id", user.club_id) // Filtrar por club_id del usuario
          .gte("start_date", today) // Solo bloqueos futuros
          .order("start_date", { ascending: true });

        if (error) throw error;

        
        this.futureBlocks = data.map((block) => ({
          ...block,
          court_name: block.courts.name,
        }));
      } catch (error) {
        console.error("Error al obtener los bloqueos futuros:", error);
        this.$q.notify({
          type: "negative",
          message: "Error al cargar los bloqueos futuros",
        });
      } finally {
        this.loading = false; // Desactivar el spinner
      }
    },
    goToBlockClubPage() {
      this.blockClubDialogVisible = true;
    },
    goToBlockCourtPage() {
      this.blockCourtDialogVisible = true;
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

  async deleteBlock(blockId) {
      try {
        // Llamar al endpoint para eliminar el bloqueo
        await api.delete(`block/delete-block/${blockId}`);

        // Mostrar notificación de éxito
        this.$q.notify({
          type: "positive",
          message: "Bloqueo eliminado exitosamente.",
        });

        // Recargar la lista de bloqueos
        await this.fetchFutureBlocks();
      } catch (error) {
        console.error("Error al eliminar el bloqueo:", error);
        this.$q.notify({
          type: "negative",
          message: "Error al eliminar el bloqueo. Intenta nuevamente.",
        });
      }
    },
 
  },
  mounted() {
    this.fetchCourts();
    this.fetchFutureBlocks(); 
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

.fixed-bottom-right {
  position: fixed;
  bottom: 80px;
  right: 20px;
  z-index: 1000;
}

.transparent-card {
  background-color: rgba(255, 255, 255, 0.3); /* Fondo translúcido */
}

.transparent-table {
  background-color: rgba(255, 255, 255, 0.3); /* Fondo translúcido */
  color: black; /* Texto negro */
}

.q-menu {
  background-color: rgba(255, 255, 255, 0.11);
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.q-item {
  color: black;
  font-size: 14px;
}

.q-item:hover {
  background-color: rgba(255, 255, 255, 0.445);
}

/* Cambiar el fondo del contenedor principal */
.custom-date-picker .q-date__main {
  background-color: #ffcc00; /* Fondo amarillo */
  border-radius: 8px; /* Bordes redondeados */
}

/* Cambiar el fondo del encabezado */
.custom-date-picker .q-date__header {
  background-color: #ff9900; /* Fondo naranja */
  color: #000; /* Texto negro */
}

/* Cambiar el fondo de los días */
.custom-date-picker .q-date__calendar-item {
  background-color: black; /* Fondo blanco para los días */
  color: #000; /* Texto negro */
}

/* Cambiar el fondo de los días seleccionados */
.custom-date-picker .q-date__calendar-item--selected {
  background-color: #00ff00; /* Fondo verde para días seleccionados */
  color: #000; /* Texto negro */
}

/* Cambiar el fondo del día actual */
.custom-date-picker .q-date__today {
  background-color: #ff0000; /* Fondo rojo para el día actual */
  color: #fff; /* Texto blanco */
}
</style>