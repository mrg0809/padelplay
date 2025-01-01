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
            <div v-for="option in options" :key="option.name" class="option-card" @click="navigateTo(option.route)"> 
              <img :src="option.image_url" alt="Option Image" class="option-image" />
              <q-icon :name="option.icon" size="lg" class="option-icon" />
              <h3>{{ option.name }}</h3>
              <p>{{ option.description }}</p>
            </div>
          </div>
          <h2>Mis Eventos:</h2>
          <div class="events-carousel">
            <div
              v-for="match in matches"
              :key="match.id"
              class="event-card"
              @click="navigateToMatch(match.id)"
            >
              <!-- Ícono dinámico según el tipo de evento -->
              <q-icon
                :name="match.tournament_id ? 'mdi-trophy' : 'mdi-tennis'"
                class="event-icon"
                :color="match.tournament_id ? 'orange' : 'yellow'"
                size="48px"
              />
              <div class="event-info">
                <p class="event-date">{{ formatDate(match.match_date) }}</p>
                <p class="event-time">{{ match.match_time }}</p>
                <p class="event-club">{{ match.club_name }}</p>
                <p class="event-court">{{ match.court_name }}</p>
              </div>
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
  import api from "../api";

  export default {
    name: "DashboardPlayer",
    data() {
      return {
        options: [
          {
            name: "Reserva una cancha",
            description: "Si ya sabes con quién vas a jugar",
            icon: "event_seat",
            image_url: "/src/assets/menu/campopadel.jpg",
            route: "reservas",
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
        matches: [], // Aquí se almacenan los partidos próximos
        activeMatch: null,
        tabs: [
          { name: "inicio", label: "Inicio", icon: "home" },
          { name: "torneos", label: "Torneos", icon: "sports_tennis" },
          { name: "asociaciones", label: "Asociaciones", icon: "group" },
          { name: "perfil", label: "Perfil", icon: "account_circle" },
        ],
      };
    },
    methods: {
      async fetchMatches() {
        try {
          const response = await api.get("/matches/upcoming");
          this.matches = response.data.matches;
        } catch (error) {
          console.error("Error al cargar partidos:", error);
          this.$q.notify({
            type: "negative",
            message: "No se pudieron cargar los partidos.",
          });
        }
      },
      formatDate(date) {
        return new Date(date).toLocaleDateString("es-ES", {
          weekday: "short",
          day: "numeric",
          month: "short",
        });
      },
      navigateToMatch(matchId) {
        this.$router.push(`/player/match/${matchId}`);
      },
      navigateTo(route) {
        this.$router.push(`/player/${route}`);
      },
      onTabChange(tabName) {
        this.$router.push(`/player/${tabName}`);
      },
      onNotifications() {
        console.log("Notificaciones abiertas");
      },
      onMenu() {
        console.log("Menú abierto");
      },
    },
    mounted() {
      this.fetchMatches();
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
  
  .events-carousel {
  display: flex;
  gap: 16px;
  overflow-x: auto; /* Desplazamiento horizontal */
  padding: 16px 0;
  scroll-snap-type: x mandatory; /* Efecto de desplazamiento suave */
  }

  .event-card {
    flex: 0 0 calc(33.333% - 16px); /* Tres tarjetas visibles a la vez */
    max-width: calc(33.333% - 16px);
    background: #1f1f1f;
    border-radius: 8px;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.5);
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
    scroll-snap-align: start; /* Alineación en el scroll */
    text-align: center;
    padding: 16px;
  }


  .event-card:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.8);
  }

  .event-image {
    width: 100%;
    height: 120px;
    object-fit: cover;
    border-radius: 8px 8px 0 0;
  }

  .event-info {
    padding: 8px;
    text-align: center;
    color: #ffffff;
  }

  .event-date,
  .event-time,
  .event-club,
  .event-court {
    margin: 4px 0;
  }

  .event-date {
    font-weight: bold;
    color: #ffd700; /* Dorado */
  }
  
  .bg-dark {
    background-color: #121212 !important; /* Fondo oscuro */
    color: #ffffff !important; /* Texto claro */
  }
  </style>