<template>
  <q-layout view="hHh lpR fFf" class="bg-dark text-white">
    <q-header elevated class="bg-primary text-white">
      <q-toolbar>
        <q-toolbar-title>¡Oops! Página no encontrada</q-toolbar-title>
      </q-toolbar>
    </q-header>

    <q-page-container>
      <q-page class="q-pa-md text-center">
        <!-- Imagen divertida -->
        <div class="broken-image">
          <img src="/src/assets/padelball.png" alt="Pelota de pádel rompiendo" class="broken-icon" />
        </div>

        <!-- Mensaje -->
        <h1 class="q-mt-md">¡Oops! Esta página aún no está disponible</h1>
        <p class="q-mb-md">
          Parece que esta pelota de pádel ha roto algo... pero no te preocupes, ¡pronto estará listo!
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
      this.$router.push("/player/inicio");
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
