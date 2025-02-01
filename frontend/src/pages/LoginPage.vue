<template>
  <q-layout view="lHh Lpr lFf">
    <!-- Contenedor de la página -->
    <q-page-container>
      <q-page class="login-page">
        <div class="login-container">
          <img src="/src/assets/logo.jpeg" alt="Logo" class="login-logo" />
          <q-form @submit="login" class="login-form">
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
            <q-btn label="Iniciar sesión" color="white" text-color="black" type="submit" class="login-btn" />
            <div v-if="error" class="error-message">
              {{ error }}
            </div>
          </q-form>
          <div class="login-links">
            <q-btn flat label="Crear una cuenta" color="white" class="login-link" @click="goToSignup" />
            <q-btn flat label="Olvidé mi contraseña" color="white" class="login-link" @click="goToForgotPassword" />
          </div>
        </div>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script>
import api from "../api";
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useUserStore } from "src/stores/userStore"; // Importa el store de Pinia

export default {
  name: "LoginPage",

  setup() {
    const email = ref("");
    const password = ref("");
    const error = ref(null);
    const router = useRouter();
    const userStore = useUserStore(); // Usa el store de Pinia

    const login = async () => {
      error.value = null;
      try {
        const response = await api.post("/auth/login", {
          email: email.value,
          password: password.value,
        });

        const { access_token } = response.data;
        localStorage.setItem("token", access_token); // Guardar el token en localStorage

        // Decodificar el token y guardar los datos en el store
        const base64Url = access_token.split(".")[1]; // Extraer el payload
        const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
        const payload = JSON.parse(atob(base64));

        // Guardar los datos del usuario en el store
        userStore.setUserDataFromToken(access_token);

        // Redirigir al dashboard correspondiente
        if (payload.user_type === "superuser") {
          router.push("/dashboard/superuser");
        } else if (payload.user_type === "admin") {
          router.push("/dashboard/admin");
        } else if (payload.user_type === "club") {
          router.push("/dashboard/club");
        } else {
          router.push("/dashboard/player");
        }
      } catch (err) {
        // Manejo del error
        if (err.response && err.response.data && err.response.data.detail) {
          error.value = err.response.data.detail; // Mostrar el mensaje del backend
        } else {
          error.value = "Ocurrió un error inesperado. Intenta de nuevo más tarde.";
        }
        console.error("Error al iniciar sesión:", err);
      }
    };

    const goToSignup = () => {
      router.push("/signup");
    };

    const goToForgotPassword = () => {
      router.push("/forgot-password");
    };

    return {
      email,
      password,
      error,
      login,
      goToSignup,
      goToForgotPassword,
    };
  },
};
</script>

<style scoped>
/* Fondo negro para toda la pantalla */
.login-page {
  background-color: black;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* Contenedor del formulario con fondo negro */
.login-container {
  background-color: black;
  padding: 2rem;
  border-radius: 12px;
  width: 100%;
  max-width: 400px;
  text-align: center;
}

/* Logo centrado y espaciado */
.login-logo {
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
.login-btn {
  margin-top: 1rem;
  width: 100%;
  border: 1px solid white;
}

/* Estilo para los links */
.login-links {
  margin-top: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.login-link {
  text-decoration: underline;
  text-align: center;
}

.error-message {
  color: red;
  margin-top: 10px;
}
</style>