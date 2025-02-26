<template>
  <q-layout view="lHh Lpr lFf">
    <!-- Contenedor de la página -->
    <q-page-container>
      <q-page class="register-page">
        <div class="register-container">
          <img src="/src/assets/logo.jpeg" alt="Logo" class="register-logo" />
          <q-form @submit="register" class="register-form">
            <q-input
              outlined
              dark
              v-model="fullName"
              label="Nombre completo"
              type="text"
              class="q-mb-md input-dark"
            />
            <q-input
              outlined
              dark
              v-model="email"
              label="Correo electrónico"
              type="email"
              class="q-mb-md input-dark"
            />
            <q-input
              outlined
              dark
              v-model="password"
              label="Contraseña"
              type="password"
              class="q-mb-md input-dark"
            />
            <q-btn label="Registrar" color="white" text-color="black" type="submit" class="register-btn" />
            <div v-if="error" class="error-message">
              {{ error }}
            </div>
            <div v-if="success" class="success-message">
              ¡Registro exitoso! Por favor revisa el correo que te hemos enviado.
            </div>
          </q-form>
          <div class="register-links">
            <q-btn flat label="¿Ya tienes una cuenta? Iniciar sesión" color="white" class="register-link" @click="goToLogin" />
          </div>
        </div>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script>
import api from "../services/api";
import { ref } from "vue";
import { useRouter } from "vue-router";

export default {
  name: "RegisterPage",
  setup() {
    const fullName = ref("");
    const email = ref("");
    const password = ref("");
    const error = ref(null);
    const success = ref(false);
    const router = useRouter();

    const register = async () => {
      error.value = null;
      success.value = false;
      try {
        await api.post("/auth/register", {
          full_name: fullName.value,
          email: email.value,
          password: password.value,
        });
        success.value = true;
      } catch (err) {
        if (err.response && err.response.data && err.response.data.detail) {
          error.value = err.response.data.detail; // Mostrar el mensaje del backend
        } else {
          error.value = "Ocurrió un error inesperado. Intenta de nuevo más tarde.";
        }
        console.error("Error al registrarse:", err);
      }
    };

    const goToLogin = () => {
      router.push("/");
    };

    return {
      fullName,
      email,
      password,
      error,
      success,
      register,
      goToLogin,
    };
  },
};
</script>

<style scoped>
/* Fondo negro para toda la pantalla */
.register-page {
  background-color: black;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* Contenedor del formulario con fondo negro */
.register-container {
  background-color: black;
  padding: 2rem;
  border-radius: 12px;
  width: 100%;
  max-width: 400px;
  text-align: center;
}

/* Logo centrado y espaciado */
.register-logo {
  width: 300px;
  margin-bottom: 2rem;
}

/* Inputs con estilo oscuro */
.input-dark {
  --q-input-border-color: white;
  --q-input-color: white;
  --q-input-label-color: gray;
}

/* Botón personalizado */
.register-btn {
  margin-top: 1rem;
  width: 100%;
  border: 1px solid white;
}

/* Estilo para los links */
.register-links {
  margin-top: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.register-link {
  text-decoration: underline;
  text-align: center;
}

.error-message {
  color: red;
  margin-top: 10px;
}

.success-message {
  color: green;
  margin-top: 10px;
}
</style>
