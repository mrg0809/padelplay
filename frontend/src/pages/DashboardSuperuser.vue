<template>
  <q-layout view="hHh lpR fFf" class="bg-dark">
    <!-- Encabezado -->
    <q-header elevated class="bg-primary text-white">
      <div class="header-content">
    <!-- Saludo -->
        <div class="greeting">
          <img src="/src/assets/logo.jpeg" alt="Logo" class="logo-icon" />
          Hola Marcelo
        </div>
    <!-- Iconos de la derecha -->
        <div class="header-icons">
          <q-btn flat round dense icon="notifications" @click="onNotifications" />
          <q-btn flat round dense icon="menu" @click="onMenu" />
        </div>
      </div>
    </q-header>


    <!-- Contenido Principal -->
    <q-page-container>
      <!-- Imagen al inicio -->
      <div class="header-image">
        <img src="/src/assets/padelplayletraslogo.png" alt="Header Image" />
      </div>

      <!-- Línea divisora -->
      <div class="divider"></div>
      <div class="home">
        <div class="options">
          <div v-for="option in options" :key="option.name" class="option-card"> 
            <img :src="option.image_url" alt="Option Image" class="option-image" />
            <q-icon :name="option.icon" size="lg" class="option-icon" />
            <h3>{{ option.name }}</h3>
            <p>{{ option.description }}</p>
          </div>
        </div>
        <h2>Tus favoritos:</h2>
        <div class="clubs">
          <div v-for="club in clubs" :key="club.name" class="club-card">
            <img :src="club.image_url" alt="Club Image" />
            <p>{{ club.name }}</p>
          </div>
        </div>
      </div>
    </q-page-container>

    <!-- Menú de Navegación Inferior -->
    <q-footer class="bg-primary text-white">
      <q-tabs
        align="justify"
        class="q-pa-xs"
        active-color="white"
        @update:model-value="onTabChange"
      >
        <q-tab
          v-for="tab in tabs"
          :key="tab.name"
          :name="tab.name"
          :label="tab.label"
          :icon="tab.icon"
          class="text-white"
        />
      </q-tabs>
    </q-footer>
  </q-layout>
</template>

<script>
export default {
  data() {
    return {
      options: [
        {
          name: "Reserva una cancha",
          description: "Si ya sabes con quién vas a jugar",
          icon: "event_seat",
          image_url: "/src/assets/menu/campopadel.jpg",
        },
        {
          name: "Clases",
          description: "Encuentra clases cerca de ti",
          icon: "school",
          image_url: "/src/assets/menu/maestropadel.jpg",
        },
        {
          name: "Torneos",
          description: "Inscríbete a torneos cerca de ti",
          icon: "emoji_events",
          image_url: "/src/assets/menu/cuadrotorneo.jpg",
        },
        {
          name: "Partidos",
          description: "Encuentra jugadores de tu nivel",
          icon: "sports_tennis",
          image_url: "/src/assets/menu/partidopadel.jpg",
        },
      ],
      clubs: [
        { name: "Racket Sports Bugambilias OK", image_url: "/src/assets/menu/partidopadel.jpg" },
        { name: "Padel Provi Revolución", image_url: "/src/assets/menu/partidopadel.jpg" },
      ],
      tabs: [
        { name: "inicio", label: "Inicio", icon: "home" },
        { name: "torneos", label: "Torneos", icon: "sports_tennis" },
        { name: "asociaciones", label: "Asociaciones", icon: "group" },
        { name: "perfil", label: "Perfil", icon: "account_circle" },
      ],
    };
  },
  methods: {
    onTabChange(tabName) {
      this.$router.push(`/${tabName}`);
    },
    onNotifications() {
      console.log("Notificaciones abiertas");
    },
    onMenu() {
      console.log("Menú abierto");
    },
  },
};
</script>

<style scoped>
/* General */
body {
  background-color: #121212; /* Fondo oscuro */
  color: #ffffff; /* Texto claro */
}

/* Encabezado */
.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  background-color: #1e1e1e; /* Fondo del encabezado */
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
  gap: 8px;
}

.header-image img {
  width: 100%; /* La imagen ocupará todo el ancho del contenedor */
  height: auto;
  border-radius: 8px; /* Opcional: bordes redondeados */
  margin-bottom: 16px; /* Espacio debajo de la imagen */
  margin-top: 16px;
}

.divider {
  height: 2px;
  background-color: #444; /* Color de la línea */
  margin: 16px 0; /* Espaciado arriba y abajo */
}

.logo-icon {
  width: 24px; /* Ajusta el tamaño del logo */
  height: 24px;
  margin-left: 8px; /* Espaciado entre texto y logo */
}

/* Opciones */
.options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
}

.option-card {
  background: #1f1f1f; /* Fondo de tarjeta oscuro */
  color: #ffffff; /* Texto blanco */
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.5); /* Sombra */
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
}

.option-card:hover {
  transform: scale(1.05); /* Efecto hover */
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.8);
}

.option-image {
  width: 100%;
  height: 120px;
  object-fit: cover; /* Ajuste de imagen */
}

.option-icon {
  margin-top: 8px;
  color: #ffd700; /* Ícono dorado */
}

.option-card h3 {
  margin: 8px 0;
  font-size: 1.2rem;
}

.option-card p {
  font-size: 0.9rem;
  color: #bbbbbb; /* Texto más claro */
}

/* Clubs */
.clubs {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.club-card {
  background: #1f1f1f;
  padding: 8px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
}

.club-card img {
  width: 100%;
  height: auto;
  border-radius: 8px;
}

.bg-dark {
  background-color: #121212 !important; /* Fondo oscuro */
  color: #ffffff !important; /* Texto claro */
}
</style>