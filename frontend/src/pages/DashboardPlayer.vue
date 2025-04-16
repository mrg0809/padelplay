<template>
    <q-layout view="hHh lpR fFf">
      <q-header elevated class="text-white">
        <div class="header-content">
      <!-- Saludo -->
          <div class="greeting">
            <img src="/src/assets/padelplay.png" alt="Logo" class="logo-icon" />
            Bienvenido {{userStore.fullName}}
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

          <div class="next-events">
            <h4>Mis Eventos:</h4>
          </div>
          
          <div class="events-carousel flex flex-center">

            <div v-if="matches.length === 0 && !isInitiallyLoading" class="q-pa-md text-center text-grey">
              No tienes próximos eventos registrados.
            </div>
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
  import { useQuasar } from 'quasar';
  import { ref, onMounted, computed } from 'vue';
  import { useRouter } from 'vue-router';
  import NotificationBell from "../components/NotificationBell.vue";
  import NavigationMenu from "../components/PlayerNavigationMenu.vue";
  import PlayerTopMenu from "src/components/PlayerTopMenu.vue";
  import BannerPromoScrolling from "src/components/BannerPromoScrolling.vue";
  import { useUserStore } from "src/stores/userStore";
  import { runTaskWithMinLoading } from 'src/helpers/loadingUtils';
  import { fetchUpcomingPlayerMatches } from "src/services/api/matches";
  import { formatDate } from 'src/helpers/dateUtils';

  export default {
    name: "DashboardPlayer",
    components: {
      NotificationBell,
      NavigationMenu,
      PlayerTopMenu,
      BannerPromoScrolling,
    },
    setup() {
      const $q = useQuasar();
      const router = useRouter();
      const matches = ref([]);
      const full_name = ref(null);
      const isInitiallyLoading = ref(true);
      const userStore = useUserStore();

      const options = [
        {
          name: "Reserva tu cancha",
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
          icon: "o_emoji_events",
          image_url: "/src/assets/menu/torneos.jpeg",
          route: "torneos",
        },
        {
          name: "Clases de Pádel",
          icon: "o_school",
          image_url: "/src/assets/menu/clases.jpeg",
          route: "reservas",
        },
      ];

      const fetchDashboardMatches = async () => {
        const upcomingMatches = await fetchUpcomingPlayerMatches();
        // Puedes añadir transformaciones aquí si es necesario antes de devolver
        return upcomingMatches;
      };

      const navigateToMatch = (matchId) => {
        router.push(`/player/match/${matchId}`);
      };

      const navigateTo = (route) => {
        router.push(`/player/${route}`);
      };

      onMounted(async () => {
        isInitiallyLoading.value = true;
        matches.value = []; // Limpia datos anteriores

        try {
          // Llama al util: pasa $q, tu función de fetch, y el tiempo mínimo deseado
          const fetchedMatches = await runTaskWithMinLoading(
            $q,
            fetchDashboardMatches, // La función que hace el trabajo real
            2000 // Ejemplo: mostrar spinner mínimo 0.7 segundos
            // Puedes pasar opciones extras de QLoading aquí si quieres sobrescribir defaults:
            // { message: 'Cargando el dashboard...', spinnerColor: 'amber' }
          );

          // Si la promesa se resuelve, runTaskWithMinLoading devuelve el resultado de fetchDashboardMatches
          matches.value = fetchedMatches || []; // Actualiza tu estado

        } catch (error) {
          // El error ya fue notificado y logueado por el util.
          // Puedes añadir lógica adicional aquí si es necesario para este componente
          // específico (ej: mostrar un mensaje de error diferente en la UI).
          console.error("Error especifico capturado en DashboardPlayer:", error);
          matches.value = []; // Asegurar que esté vacío en caso de error
        } finally {
          isInitiallyLoading.value = false; // Marca que la carga inicial (intento) terminó
        }
      });

      return {
        full_name,
        options,
        matches,
        isInitiallyLoading,
        formatDate,
        navigateToMatch,
        navigateTo,
        userStore,
      };
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
  width: 100%;
  display: flex;
  flex-wrap: nowrap;
  gap: 13px;
  overflow-x: auto; /* Desplazamiento horizontal */
  overflow-y: hidden; 
  padding: 5px 0;
  scroll-snap-type: x mandatory; /* Efecto de desplazamiento suave */
  align-items: center;
  white-space: nowrap;
  }

  .event-card {
    flex: 0 0 auto; /* Tres tarjetas visibles a la vez */
    max-width: 220px;
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