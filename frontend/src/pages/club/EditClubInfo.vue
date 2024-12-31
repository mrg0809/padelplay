<template>
  <q-layout view="hHh lpR fFf" class="bg-dark text-white">
    <q-header class="bg-primary text-white">
      <q-toolbar>
        <q-toolbar-title>Editar Club</q-toolbar-title>
        <q-btn flat round icon="arrow_back" @click="goBack" label="REGRESAR" />
      </q-toolbar>
    </q-header>
    <q-page-container>
      <q-page class="bg-dark text-white q-pa-md">
        <q-card class="q-pa-lg bg-dark text-white">
          <q-card-section>
            <div class="text-h6">Editar Información del Club</div>
          </q-card-section>

          <!-- Mostrar logo o ícono con botón a un lado -->
          <q-card-section class="q-py-md flex items-center">
            <q-img
              v-if="form.logo_url"
              :src="form.logo_url"
              alt="Logo del Club"
              style="max-width: 150px; max-height: 150px; border-radius: 8px;"
            />
            <q-icon
              v-else
              name="image_not_supported"
              size="xl"
              color="grey"
              style="font-size: 64px;"
            />
            <q-btn
              label="Subir Logo"
              color="primary"
              class="q-ml-md"
              @click="triggerFileUpload"
            />
            <input
              type="file"
              ref="fileInput"
              style="display: none;"
              @change="handleFileUpload"
            />
          </q-card-section>

          <!-- Formulario de edición -->
          <q-card-section>
            <q-input
              v-model="form.name"
              label="Nombre del Club"
              outlined
              dense
              class="q-mb-md text-white"
              label-color="white"
            />
            <q-input
              v-model="form.address"
              label="Dirección"
              outlined
              dense
              class="q-mb-md text-white"
              label-color="white"
            />
            <q-input
              v-model="form.city"
              label="Ciudad"
              outlined
              dense
              class="q-mb-md text-white"
              label-color="white"
            />
            <q-input
              v-model="form.state"
              label="Estado"
              outlined
              dense
              class="q-mb-md text-white"
              label-color="white"
            />
            <q-input
              v-model="form.postal_code"
              label="Código Postal"
              outlined
              dense
              class="q-mb-md text-white"
              label-color="white"
            />
            <q-select
              v-model="form.country"
              label="País"
              :options="countries"
              outlined
              dense
              map-options
              emit-value
              class="q-mb-md text-white"
              label-color="white"
            />
            <q-input
              v-model="form.contact_phone"
              label="Teléfono de Contacto"
              outlined
              dense
              class="q-mb-md text-white"
              label-color="white"
            />
            <q-input
              v-model="form.contact_email"
              label="Email de Contacto"
              outlined
              dense
              type="email"
              class="q-mb-md text-white"
              label-color="white"
            />
            <q-input
              v-model="form.facebook_url"
              label="Facebook URL"
              outlined
              dense
              class="q-mb-md text-white"
              label-color="white"
            />
            <q-input
              v-model="form.instagram_url"
              label="Instagram URL"
              outlined
              dense
              class="q-mb-md text-white"
              label-color="white"
            />
            <q-input
              v-model="form.tiktok_url"
              label="TikTok URL"
              outlined
              dense
              class="q-mb-md text-white"
              label-color="white"
            />
            <q-input
              v-model="form.whatsapp_number"
              label="WhatsApp Número"
              outlined
              dense
              class="q-mb-md text-white"
              label-color="white"
            />
            <q-input
              v-model.number="form.latitude"
              label="Latitud (Maps)"
              type="number"
              outlined
              dense
              class="q-mb-md text-white"
              label-color="white"
            />
            <q-input
              v-model.number="form.longitude"
              label="Longitud (Maps)"
              type="number"
              outlined
              dense
              class="q-mb-md text-white"
              label-color="white"
            />
          </q-card-section>

          <q-card-actions align="right">
            <q-btn label="Guardar Cambios" color="primary" @click="saveClubInfo" />
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
      form: {
        name: "",
        address: "",
        city: "",
        state: "",
        postal_code: "",
        country: "México", // Valor predeterminado
        contact_phone: "",
        contact_email: "",
        logo_url: "",
        facebook_url: "",
        instagram_url: "",
        whatsapp_number: "",
        tiktok_url: "",
        latitude: 0,
        longitude: 0,
      },
      logoFile: null, // Archivo seleccionado para subir
      countries: [
        "México",
        "Argentina",
        "Chile",
        "Colombia",
        "España",
        "Perú",
        "Estados Unidos",
        "Venezuela",
        "Guatemala",
        "Ecuador",
        "Cuba",
        "Bolivia",
        "Honduras",
        "El Salvador",
        "Nicaragua",
        "Paraguay",
        "Costa Rica",
        "Puerto Rico",
        "Panamá",
        "Uruguay",
        "República Dominicana",
      ],
    };
  },
  methods: {
    async fetchClubInfo() {
      try {
        const response = await api.get("/clubs");
        this.form = response.data;
      } catch (error) {
        console.error("Error al obtener la información del club:", error);
        this.$q.notify({
          type: "negative",
          message: "Error al cargar información del club",
        });
      }
    },
    async saveClubInfo() {
      try {
        await api.put("/clubs", this.form);
        this.$q.notify({
          type: "positive",
          message: "Información actualizada exitosamente",
        });
      } catch (error) {
        console.error("Error al actualizar la información del club:", error);
        this.$q.notify({
          type: "negative",
          message: "Error al actualizar la información",
        });
      }
    },
    triggerFileUpload() {
      this.$refs.fileInput.click(); // Simula el clic en el input de archivo
    },
    handleFileUpload(event) {
      const file = event.target.files[0];
      if (file) {
        if (file.size > 2 * 1024 * 1024) {
          this.$q.notify({
            type: "negative",
            message: "El archivo es demasiado grande (máximo 2MB).",
          });
          return;
        }
        if (!file.type.startsWith("image/")) {
          this.$q.notify({
            type: "negative",
            message: "El archivo debe ser una imagen.",
          });
          return;
        }

        this.uploadLogo(file);
      }
    },
    async uploadLogo(file) {
      const formData = new FormData();
      formData.append("file", file);

      try {
        const response = await api.post("/clubs/upload-logo", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
            Authorization: `Bearer ${localStorage.getItem("token")}`, // Incluye el token
          },
        });

        this.form.logo_url = response.data.signed_url || response.data.logo_url;

        this.$q.notify({
          type: "positive",
          message: "Logo subido exitosamente",
        });
      } catch (error) {
        console.error("Error al subir el logo:", error);
        this.$q.notify({
          type: "negative",
          message: "Error al subir el logo",
        });
      }
    },
    goBack() {
      this.$router.back();
    },
  },
  mounted() {
    this.fetchClubInfo();
  },
};
</script>
