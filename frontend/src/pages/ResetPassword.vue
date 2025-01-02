<template>
    <q-page class="q-pa-md text-center">
      <h1 class="q-mb-md">Establece tu nueva contraseña</h1>
      <q-input
        v-model="newPassword"
        type="password"
        label="Nueva contraseña"
        outlined
        dense
        color="primary"
      />
      <q-btn
        label="Actualizar contraseña"
        color="primary"
        class="q-mt-md"
        @click="updatePassword"
      />
      <q-notify v-model="notification" />
    </q-page>
  </template>
  
  <script>
  import { supabase } from "src/services/supabase";
  
  export default {
    data() {
      return {
        newPassword: "",
        notification: null,
      };
    },
    methods: {
      async updatePassword() {
        try {
          const { error } = await supabase.auth.updateUser({ password: this.newPassword });
  
          if (error) {
            this.notification = { type: "negative", message: error.message };
            return;
          }
  
          this.notification = { type: "positive", message: "Contraseña actualizada exitosamente." };
          this.$router.push("/login");
        } catch (error) {
          console.error("Error al actualizar la contraseña:", error.message);
          this.notification = { type: "negative", message: "Error inesperado al actualizar la contraseña." };
        }
      },
    },
    mounted() {
      supabase.auth.onAuthStateChange((event) => {
        if (event === "PASSWORD_RECOVERY") {
          console.log("Modo recuperación de contraseña activado.");
        }
      });
    },
  };
  </script>