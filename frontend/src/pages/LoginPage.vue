<template>
  <q-layout view="lHh Lpr lFf">
    <!-- Barra de navegación (opcional) -->
    <q-header elevated>
      <q-toolbar>
        <q-toolbar-title>
          Login
        </q-toolbar-title>
      </q-toolbar>
    </q-header>

    <!-- Contenedor de la página -->
    <q-page-container>
      <q-page class="login-page">
        <div class="login-container">
          <img src="/src/assets/logo.png" alt="Logo" class="login-logo" />
          <q-form @submit="submitForm" class="login-form">
            <q-input
              filled
              v-model="email"
              label="Correo electrónico"
              type="email"
              class="q-mb-md"
            />
            <q-input
              filled
              v-model="password"
              label="Contraseña"
              type="password"
              class="q-mb-md"
            />
            <q-btn label="Iniciar sesión" color="primary" type="submit" />
          </q-form>
        </div>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script>
import api from "../api";
import { ref } from 'vue';

const email = ref('');
const password = ref('');

const submitForm = () => {
  // Lógica para enviar el formulario
};

export default {
  name: "LoginPage",
  data() {
    return {
      email: "",
      password: "",
      error: null,
    };
  },

  methods: {
  async login() {
    this.error = null;
    try {
      const response = await api.post("/auth/login", {
        email: this.email,
        password: this.password,
      });

      const { access_token } = response.data;
      localStorage.setItem("token", access_token); // Guardar el token en localStorage

      // Decodificar el token usando atob
      const base64Url = access_token.split(".")[1]; // Extraer el payload
      const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
      const payload = JSON.parse(atob(base64));
      const userType = payload.user_type;

      // Redirigir al dashboard correspondiente
      if (userType === "superuser") {
        this.$router.push("/dashboard/superuser");
      } else if (userType === "admin") {
        this.$router.push("/dashboard/admin");
      } else if (userType === "club") {
        this.$router.push("/dashboard/club");
      } else {
        this.$router.push("/dashboard/player");
      }
    } catch (err) {
      this.error = "Invalid credentials. Please try again.";
      console.error("Login error:", err);
    }
  },
},
};
</script>

<style scoped>
.login-page {
  background-color: black;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
}

.login-container {
  background-color: rgba(255, 255, 255, 0.8);
  padding: 2rem;
  border-radius: 8px;
  width: 100%;
  max-width: 400px;
  text-align: center;
}

.login-logo {
  width: 150px;
  margin-bottom: 2rem;
}

.q-input, .q-btn {
  width: 100%;
}

.q-btn {
  margin-top: 1rem;
}
</style>