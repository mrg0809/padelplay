<template>
    <q-layout view="hHh lpR fFf">
      <!-- Encabezado -->
      <q-header elevated class="text-white">
        <div class="header-content">
      <!-- Saludo -->
          <div class="greeting">
            <img src="/src/assets/padelplay.png" alt="Logo" class="logo-icon" />
            Bienvenido {{full_name}}
          </div>
      <!-- Iconos de la derecha -->
          <div class="header-icons">
            <NotificationBell />
            <PlayerTopMenu />
          </div>
        </div>
        <BannerPromoScrolling />
      </q-header>
  
      <q-page-container>
      
        
  
        <div class="home">
          <div class="options">
            <div v-for="option in options" :key="option.name" class="option-card" @click="navigateTo(option.route)"> 
              <img :src="option.image_url" alt="Option Image" class="option-image" />
              <h3>{{ option.name }}</h3>
              <q-icon :name="option.icon" size="xl" class="option-icon" />
            </div>
          </div>

          <div class="events-carousel flex flex-center">
            <div class="next-events">
              <h4>Mis Eventos:</h4>
            </div>
            <q-spinner-puff v-if="isLoading" color="primary" size="9em" />
            <div
              v-else
              v-for="match in matches"
              :key="match.id"
              class="event-card"
              @click="navigateToMatch(match.id)"
            >
              <!-- Ícono dinámico según el tipo de evento -->
              <q-icon
                :name="match.tournament_id ? 'emoji_events' : 'sports_tennis'"
                class="event-icon material-icons-outlined"
                size="35px"
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

      <NavigationMenu />
    
    </q-layout>
  </template>
  
  <script>
  import NotificationBell from "../components/NotificationBell.vue";
  import api from "../api";
  import NavigationMenu from "../components/PlayerNavigationMenu.vue";
  import PlayerTopMenu from "src/components/PlayerTopMenu.vue";
  import BannerPromoScrolling from "src/components/BannerPromoScrolling.vue";
  import { ref } from 'vue';

  export default {
    name: "DashboardPlayer",
    components: {
      NotificationBell,
      NavigationMenu,
      PlayerTopMenu,
      BannerPromoScrolling,
    },
    data() {
      return {
        full_name: null,
        options: [
          {
            name: "Reserva tu cancha",
            description: "Encuentra tu club favorito",
            icon: "edit_calendar",
            image_url: "/src/assets/menu/reserva.jpeg",
            route: "reservas",
          },
          {
            name: "Únete a un partido",
            icon: "sports_tennis",
            image_url: "/src/assets/menu/unete.jpeg",
            route: "unete",
          },
          {
            name: "Inscríbete a torneos",
            icon: "emoji_events",
            image_url: "/src/assets/menu/torneos.jpeg",
            route: "torneos"
          },
          {
            name: "Clases de Pádel",
            icon: "school",
            image_url: "/src/assets/menu/clases.jpeg",
          },
        ],
        matches: [], // Aquí se almacenan los partidos próximos
        activeMatch: null,
      };
    },
    setup() {
      const isLoading = ref(true);
      return { isLoading }
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
        } finally {
          this.isLoading = false;
        }
      },
      formatDate(date) {
        const [year, month, day] = date.split('-').map(Number); 
        const localDate = new Date(year, month - 1, day); // Crear fecha en zona horaria local
        return localDate.toLocaleDateString("es-MX", {
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
      fetchUserNameFromToken() {
        const token = localStorage.getItem("token");
        if (token) {
          const base64Url = token.split(".")[1];
          const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
          const payload = JSON.parse(atob(base64));
          this.full_name = payload.full_name || "Usuario";
        }
      },
    },
    mounted() {
      this.fetchUserNameFromToken();
      this.fetchMatches();
    },
  };
  </script>
  
  <style scoped>

  .home {
    background-color: #dddddd;
  }
  
  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 16px;
    background-color: #000000; /* Fondo del encabezado */
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
    gap: 2px;
  }
  
  .logo-icon {
    width: 60px; /* Ajusta el tamaño del logo */
    height: 60px;
  }
  
  /* Opciones */
  .options {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1px;
  }
  
  .option-card {
    background-image: url("../assets/texturafondo.png");
    background-size: cover;
    color: #ffffff; /* Texto blanco */
    border-radius: 15px;
    text-align: center;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.5); /* Sombra */
    overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
    margin: 7px;
  }
  
  .option-card:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.8);
    background-color: #282828; /* Color de fondo ligeramente más oscuro */
  }
  
  .option-image {
    width: 100%;
    height: 120px;
    object-fit: cover; /* Ajuste de imagen */
  }
  
  .option-icon {
    margin-bottom: 10px;
    color: #ffffff
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
  padding: 5px 0;
  scroll-snap-type: x mandatory; /* Efecto de desplazamiento suave */
  align-items: center;
  }

  .event-card {
    flex: 0 0 calc(33.333% - 16px); /* Tres tarjetas visibles a la vez */
    max-width: calc(33.333% - 16px);
    background-image: url("../assets/texturafondo.png");
    background-size: cover;
    border-radius: 15px;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.5);
    cursor: pointer;
    margin: auto;
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
  }

  .next-events {
    background-image: url("../assets/texturafondo.png");
    background-size: cover;
    color: #ffffff;
    width: 94%;
    overflow: hidden; /* Oculta contenido fuera del área visible */
    height: 30px; 
    border-radius: 80px;
    display: flex;
    align-items: center;
    align-content: center;
    text-align: center;
    margin: 7px auto;
  }

  .next-events h4 {
    font-size: medium;
    margin: 1px auto;
  }
  </style>