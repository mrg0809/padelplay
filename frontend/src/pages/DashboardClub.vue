<template>
    <q-layout view="hHh lpR fFf" class="bg-dark">
      <!-- Encabezado -->
      <q-header elevated class="bg-primary text-white">
        <div class="header-content">
          <!-- Saludo -->
          <div class="greeting">
            <img src="/src/assets/logo.jpeg" alt="Logo" class="logo-icon" />
            Hola 
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
            <div
              v-for="option in options"
              :key="option.name"
              class="option-card"
              @click="navigateTo(option.route)"
            >
              <img :src="option.image_url" alt="Option Image" class="option-image" />
              <q-icon :name="option.icon" size="lg" class="option-icon" />
              <h3>{{ option.name }}</h3>
              <p>{{ option.description }}</p>
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
        clubName: "Club PadelPlay", // Reemplaza con el nombre real del club desde la API o store
        options: [
          {
            name: "Administrar reservas",
            description: "Gestiona las reservas de tus canchas",
            icon: "event",
            image_url: "/src/assets/menu/campopadel.jpg",
            route: "reservas",
          },
          {
            name: "Administrar canchas",
            description: "Configura tus canchas y horarios",
            icon: "sports_tennis",
            image_url: "/src/assets/menu/campopadel.jpg",
            route: "canchas",
          },
          {
            name: "Crear torneos",
            description: "Organiza torneos y eventos",
            icon: "emoji_events",
            image_url: "/src/assets/menu/campopadel.jpg",
            route: "torneos",
          },
        ],
        tabs: [
          { name: "inicio", label: "Inicio", icon: "home" },
          { name: "torneos", label: "Torneos", icon: "sports_tennis" },
          { name: "perfil", label: "Perfil", icon: "account_circle" },
        ],
      };
    },
    methods: {
      navigateTo(route) {
        this.$router.push(`/club/${route}`);
      },
      onTabChange(tabName) {
        this.$router.push(`/club/${tabName}`);
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