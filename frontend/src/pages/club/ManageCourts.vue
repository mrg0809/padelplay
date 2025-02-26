<template>
  <q-layout view="hHh lpR fFf" class="body">
    <q-header elevated class="bg-primary text-white">
      <div class="header-content">
        <div class="greeting">
          <img src="/src/assets/padelplay.png" alt="Logo" class="logo-icon" />
          Listado de canchas
        </div>
        <div class="header-icons">
          <q-btn flat round icon="close" @click="goBack" />
        </div>
      </div>
    </q-header>

    <q-page-container>
      <!-- Espacio entre el header y la lista -->
      <div class="q-mt-xl"></div>

      <!-- Lista de canchas -->
      <q-list class="court-list">
        <q-item
          v-for="(court, index) in courts"
          :key="court.id"
          clickable
          @click="editCourt(court)"
          class="text-black court-item"
        >
          <q-item-section avatar>
            <div class="row-number">{{ index + 1 }}</div>
          </q-item-section>
          <q-item-section>
            <q-item-label>{{ court.name }}</q-item-label>
            <q-item-label caption class="text-black">
              PRECIOS:
              <template v-if="court.price_per_hour">1 hora: ${{ court.price_per_hour }}</template>
              <template v-if="court.price_per_hour_and_half"> | 1 1/2 hora: ${{ court.price_per_hour_and_half }}</template>
              <template v-if="court.price_per_two_hour"> | 2 horas: ${{ court.price_per_two_hour }}</template>
            </q-item-label>
          </q-item-section>
          <q-item-section side>
            <q-btn flat icon="o_delete" color="black" size="lg" @click.stop="confirmDelete(court.id)" />
          </q-item-section>
        </q-item>
      </q-list>

      <q-btn
        glossy
        round
        size="lg"
        color="black"
        icon="add"
        @click="openCourtDialog"
        class="fixed-bottom-right q-mb-xl"
      />
    </q-page-container>

    <!-- Diálogo para agregar/editar cancha -->
    <q-dialog v-model="isDialogOpen">
      <q-card class="bg-black text-white" style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">{{ dialogTitle }}</div>
        </q-card-section>

        <q-card-section>
          <q-input
            v-model="form.name"
            label="Nombre de la cancha"
            outlined
            dense
            color="white"
          />

          <!-- Precio por hora -->
          <q-toggle
            v-model="form.enable_price_per_hour"
            label="¿Habilitar precio por hora?"
            dense
            color="white"
          />
          <q-input
            v-model.number="form.price_per_hour"
            label="Precio por hora"
            outlined
            dense
            type="number"
            :disable="!form.enable_price_per_hour"
            color="white"
          />

          <!-- Precio por hora y media -->
          <q-toggle
            v-model="form.enable_price_per_hour_and_half"
            label="¿Habilitar precio por hora y media?"
            dense
            color="white"
          />
          <q-input
            v-model.number="form.price_per_hour_and_half"
            label="Precio por hora y media"
            outlined
            dense
            type="number"
            :disable="!form.enable_price_per_hour_and_half"
            color="white"
          />

          <!-- Precio por dos horas -->
          <q-toggle
            v-model="form.enable_price_per_two_hour"
            label="¿Habilitar precio por dos horas?"
            dense
            color="white"
          />
          <q-input
            v-model.number="form.price_per_two_hour"
            label="Precio por dos horas"
            outlined
            dense
            type="number"
            :disable="!form.enable_price_per_two_hour"
            color="white"
          />

          <q-toggle
            v-model="form.is_indoor"
            label="¿Es indoor?"
            dense
            color="white"
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancelar" color="red" v-close-popup />
          <q-btn flat label="Guardar" color="green" @click="saveCourt" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="isDeleteDialogOpen">
      <q-card class="bg-dark text-white">
        <q-card-section class="text-h6">
          Confirmar eliminación
        </q-card-section>

        <q-card-section>
          ¿Estás seguro de que deseas eliminar esta cancha? Esta acción no se puede deshacer.
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancelar" color="primary" v-close-popup />
          <q-btn flat label="Eliminar" color="negative" @click="deleteCourt" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <ClubNavigationMenu />
  </q-layout>
</template>

<script>
import { getUserFromToken } from "src/services/api";
import api from "../../services/api";
import ClubNavigationMenu from "src/components/ClubNavigationMenu.vue";

export default {
  data() {
    return {
      courts: [],
      isDialogOpen: false,
      isDeleteDialogOpen: false,
      dialogTitle: "Agregar Cancha",
      form: {
        id: null,
        name: "",
        price_per_hour: null,
        enable_price_per_hour: false,
        price_per_hour_and_half: null,
        enable_price_per_hour_and_half: false,
        price_per_two_hour: null,
        enable_price_per_two_hour: false,
        is_indoor: false,
        club_id: null,
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
        this.courts = response.data;
      } catch (error) {
        console.error("Error al obtener las canchas:", error);
      }
    },
    openCourtDialog() {
      this.resetForm();
      this.dialogTitle = "Agregar Cancha";
      this.isDialogOpen = true;
    },
    editCourt(court) {
      this.form = {
        ...court,
        enable_price_per_hour: court.price_per_hour !== null,
        enable_price_per_hour_and_half: court.price_per_hour_and_half !== null,
        enable_price_per_two_hour: court.price_per_two_hour !== null,
      };
      this.dialogTitle = "Editar Cancha";
      this.isDialogOpen = true;
    },
    async saveCourt() {
      try {
        const payload = {
          name: this.form.name,
          price_per_hour: this.form.enable_price_per_hour ? this.form.price_per_hour : null,
          price_per_hour_and_half: this.form.enable_price_per_hour_and_half ? this.form.price_per_hour_and_half : null,
          price_per_two_hour: this.form.enable_price_per_two_hour ? this.form.price_per_two_hour : null,
          is_indoor: this.form.is_indoor,
          club_id: this.form.club_id, 
        };

        if (this.form.id) {
          // Editar cancha
          await api.put(`/courts/${this.form.id}`, payload);
        } else {
          // Agregar nueva cancha
          await api.post("/courts", payload);
        }
        this.isDialogOpen = false;

        // Refrescar la lista completa desde el backend
        await this.fetchCourts();
      } catch (error) {
        console.error("Error al guardar la cancha:", error);
      }
    },

    confirmDelete(courtId) {
      this.courtToDelete = courtId; // Guarda el ID de la cancha
      this.isDeleteDialogOpen = true; // Abre el diálogo
    },

    async deleteCourt() {
      try {
        // Llamar al backend para eliminar la cancha
        await api.delete(`/courts/${this.courtToDelete}`);
        // Actualizar la lista de canchas localmente
        this.courts = this.courts.filter((court) => court.id !== this.courtToDelete);
        this.isDeleteDialogOpen = false; // Cerrar el diálogo de confirmación

        // Mostrar mensaje de éxito
        this.$q.notify({
          type: "positive",
          message: "La cancha ha sido eliminada con éxito.",
          position: "top",
        });
      } catch (error) {
        console.error("Error al eliminar la cancha:", error);

        // Manejar errores del backend y mostrar un mensaje de error
        const errorMessage = error.response?.data?.detail || "No se pudo eliminar la cancha. Inténtalo nuevamente.";
        this.$q.notify({
          type: "negative",
          message: errorMessage,
          position: "bottom",
        });
      }
    },

    resetForm() {
      const user = getUserFromToken();
      this.form = {
        id: null,
        name: "",
        price_per_hour: null,
        enable_price_per_hour: false,
        price_per_hour_and_half: null,
        enable_price_per_hour_and_half: false,
        price_per_two_hour: null,
        enable_price_per_two_hour: false,
        is_indoor: false,
        club_id: user ? user.club_id : null,
      };
    },
    goBack() {
      this.$router.back();
    },
  },
  mounted() {
    const user = getUserFromToken();
    if (user) {
      this.form.club_id = user.club_id;
    }
    this.fetchCourts();
  },
};
</script>

<style scoped>
.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  background-color: #000000; /* Fondo del encabezado */
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
  width: 60px; /* Ajusta el tamaño del logo */
  height: 60px;
}

.body {
  background-image: url(../../assets/menu/padelcourtfloor.jpg);
  background-size: cover;
}

.court-list {
  font-size: large;
}

.court-item {
  border-bottom: 1px solid rgba(0, 0, 0, 0.12); /* Línea divisoria sutil */
  background-color: rgba(255, 255, 255, 0.3); /* Fondo translúcido */
  margin-bottom: 8px; /* Espacio entre elementos */
  border-radius: 4px; /* Bordes redondeados */
}

.row-number {
  font-size: 1.2rem;
  font-weight: bold;
  color: #000000;
}

.fixed-bottom-right {
  position: fixed;
  bottom: 80px; /* Ajusta la posición para que esté arriba del ClubNavigationMenu */
  right: 20px;
  z-index: 1000; /* Asegura que el botón esté por encima de otros elementos */
}
</style>