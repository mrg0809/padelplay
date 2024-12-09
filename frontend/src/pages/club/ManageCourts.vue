<template>
  <q-layout view="hHh lpR fFf" class="bg-light">
    <q-header class="bg-primary text-white">
      <q-toolbar>
        <q-toolbar-title>Administrar Canchas</q-toolbar-title>
        <q-btn flat round icon="add" @click="openCourtDialog" label="Agregar cancha" />
      </q-toolbar>
    </q-header>

    <q-page-container>
      <!-- Lista de canchas -->
      <q-list bordered>
        <q-item
          v-for="court in courts"
          :key="court.id"
          clickable
          @click="editCourt(court)"
        >
          <q-item-section avatar>
            <q-icon name="sports_tennis" />
          </q-item-section>
          <q-item-section>
            <q-item-label>{{ court.name }}</q-item-label>
            <q-item-label caption>
              Precio: ${{ court.price }} | Modalidad: {{ court.modality }}
            </q-item-label>
          </q-item-section>
          <q-item-section side>
            <q-btn flat icon="delete" color="red" @click.stop="deleteCourt(court.id)" />
          </q-item-section>
        </q-item>
      </q-list>
    </q-page-container>

    <!-- Diálogo para agregar/editar cancha -->
    <q-dialog v-model="isDialogOpen">
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">{{ dialogTitle }}</div>
        </q-card-section>

        <q-card-section>
          <q-input
            v-model="form.name"
            label="Nombre de la cancha"
            outlined
            dense
          />
          <q-select
            v-model="form.modality"
            label="Modalidad"
            :options="modalities"
            outlined
            dense
          />
          <q-input
            v-model.number="form.price"
            label="Precio por hora"
            outlined
            dense
            type="number"
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancelar" color="primary" v-close-popup />
          <q-btn flat label="Guardar" color="primary" @click="saveCourt" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-layout>
</template>

<script>
import api from "../../api"; // Ruta al cliente de Axios

export default {
  data() {
    return {
      courts: [], // Lista de canchas
      isDialogOpen: false,
      dialogTitle: "Agregar Cancha",
      form: {
        id: null,
        name: "",
        modality: "",
        price: null,
      },
      modalities: ["Por hora", "Hora y media"], // Opciones para modalidad
    };
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
      this.form = { ...court };
      this.dialogTitle = "Editar Cancha";
      this.isDialogOpen = true;
    },
    async saveCourt() {
      try {
        if (this.form.id) {
          // Editar cancha
          await api.put(`/courts/${this.form.id}`, this.form);
        } else {
          // Agregar nueva cancha
          const response = await api.post("/courts", this.form);
          this.courts.push(response.data); // Agregar a la lista
        }
        this.isDialogOpen = false;
        this.fetchCourts(); // Refrescar la lista
      } catch (error) {
        console.error("Error al guardar la cancha:", error);
      }
    },
    async deleteCourt(id) {
      try {
        await api.delete(`/courts/${id}`);
        this.courts = this.courts.filter((court) => court.id !== id);
      } catch (error) {
        console.error("Error al eliminar la cancha:", error);
      }
    },
    resetForm() {
      this.form = {
        id: null,
        name: "",
        modality: "",
        price: null,
      };
    },
  },
  mounted() {
    this.fetchCourts();
  },
};
</script>

  
  <style scoped>
  </style>
  