<template>
  <q-layout view="hHh lpR fFf" class="bg-dark text-white">
    <q-header elevated class="bg-primary text-white">
      <q-toolbar>
        <q-toolbar-title>¡Oops! Función no encontrada</q-toolbar-title>
      </q-toolbar>
    </q-header>

    <q-page-container>
      <q-page class="q-pa-md text-center">
        <!-- Imagen divertida -->
        <div class="broken-image">
          <img src="/src/assets/padelball.png" alt="Pelota de pádel rompiendo" class="broken-icon" />
        </div>

        <!-- Mensaje -->
        <h1 class="q-mt-md">¡Oops! Esta función aún no está disponible</h1>
        <p class="q-mb-md">
          Parece que esta pelota de padel ha roto algo... pero no te preocupes, ¡pronto estará listo!
        </p>

        <!-- Botón para regresar -->
        <q-btn
          label="Volver al inicio"
          color="primary"
          class="q-mt-md"
          icon="home"
          @click="goHome"
        />
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script>
export default {
  name: "PageNotFound",
  methods: {
    goHome() {
      const token = localStorage.getItem("token"); // Obtener el token del almacenamiento local

      if (!token) {
        // Si no hay token, redirigir al login
        this.$router.push("/login");
        return;
      }

      try {
        // Decodificar el token usando atob
        const base64Url = token.split(".")[1]; // Extraer el payload
        const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
        const payload = JSON.parse(atob(base64));
        const userType = payload.user_type; // Asegúrate de que 'user_type' esté en el token

        // Redirigir según el tipo de usuario
        if (userType === "superuser") {
          this.$router.push("/dashboard/superuser");
        } else if (userType === "admin") {
          this.$router.push("/dashboard/admin");
        } else if (userType === "club") {
          this.$router.push("/dashboard/club");
        } else {
          this.$router.push("/dashboard/player");
        }
      } catch (error) {
        console.error("Error al decodificar el token:", error);
        // Si algo falla, redirigir al login
        this.$router.push("/");
      }
    },
  },
};
</script>

<style scoped>
.broken-image {
  display: flex;
  justify-content: center;
  margin-top: 50px;
}

.broken-icon {
  max-width: 200px;
  border-radius: 50%;
  animation: bounce 1s infinite ease-in-out;
}

/* Animación de rebote para la pelota */
@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-20px);
  }
}

h1 {
  font-size: 2rem;
  color: #ffd700; /* Amarillo para destacar */
}

p {
  font-size: 1.2rem;
  color: #bbbbbb; /* Texto claro */
}

.q-btn {
  background-color: #1976d2; /* Color primario */
  color: white;
}

.q-btn:hover {
  background-color: #005bb5; /* Más oscuro en hover */
}
</style>
