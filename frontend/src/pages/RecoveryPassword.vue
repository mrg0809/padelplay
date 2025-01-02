<template>
    <q-layout view="hHh lpR fFf" class="bg-dark text-white">
      <q-header elevated class="bg-primary text-white">
        <q-toolbar>
          <q-toolbar-title>Recuperar Contraseña</q-toolbar-title>
        </q-toolbar>
      </q-header>
  
      <q-page-container>
        <q-page class="q-pa-md">
          <div class="text-center q-mb-md">
            <q-icon name="lock_reset" size="64px" color="primary" />
            <h2>¿Olvidaste tu contraseña?</h2>
            <p>Introduce tu correo electrónico para enviarte un enlace de recuperación.</p>
          </div>
  
          <q-form @submit.prevent="sendRecoveryEmail">
            <q-input
              v-model="email"
              label="Correo electrónico"
              type="email"
              outlined
              dense
              color="primary"
              required
            />
            <q-btn
              label="Enviar enlace"
              color="primary"
              class="q-mt-md full-width"
              type="submit"
            />
          </q-form>
  
          <div v-if="message" class="q-mt-md text-center">
            <q-banner dense color="positive" class="banner-message">
              <q-icon name="check_circle" />
              {{ message }}
            </q-banner>
          </div>
          <div v-if="error" class="q-mt-md text-center">
            <q-banner dense color="negative" class="banner-message">
              <q-icon name="error" />
              {{ error }}
            </q-banner>
          </div>
        </q-page>
      </q-page-container>
    </q-layout>
  </template>
  
  <script>
  import { supabase } from "src/services/supabase";
  
  export default {
    name: "RecoveryPassword",
    data() {
      return {
        email: "",
        message: null,
        error: null,
      };
    },
    methods: {
      async sendRecoveryEmail() {
        this.message = null;
        this.error = null;
  
        try {
          const { error } = await supabase.auth.resetPasswordForEmail(this.email, {
            redirectTo: "https://tu-dominio.com/update-password",
          });
  
          if (error) {
            console.error("Error al enviar el correo de recuperación:", error.message);
            this.error = "No se pudo enviar el enlace de recuperación. Intenta nuevamente.";
            return;
          }
  
          this.message = "Correo de recuperación enviado exitosamente. Revisa tu bandeja de entrada.";
        } catch (error) {
          console.error("Error inesperado:", error.message);
          this.error = "Ocurrió un error inesperado. Intenta nuevamente más tarde.";
        }
      },
    },
  };
  </script>
  
  <style scoped>
  .q-layout {
    min-height: 100vh;
  }
  
  /* Estilo para los banners */
  .banner-message {
    background-color: #1f1f1f !important; /* Fondo oscuro */
    color: white !important; /* Texto claro */
    border-radius: 8px; /* Bordes redondeados */
    padding: 10px;
  }
  
  .q-banner q-icon {
    color: white !important; /* Ícono blanco */
  }
  </style>
  