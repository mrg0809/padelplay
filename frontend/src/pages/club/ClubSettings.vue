<template>
    <q-layout view="hHh lpR fFf" class="body">
      <!-- Encabezado -->
      <q-header elevated class="text-white">
        <div class="header-content">
          <!-- Saludo -->
          <div class="greeting">
            <img src="/src/assets/padelplay.png" alt="Logo" class="logo-icon" />
          </div>
        
          <div class="header-icons">
            <NotificationBell />
            <ClubTopMenu />
          </div>
        </div>
        <BannerPromoScrolling />
      </q-header>
  
      <q-page-container>
        <div class="home">
          <!-- Lista de iconos con nombres -->
          <div class="icon-grid">
            <div
              v-for="option in options"
              :key="option.name"
              class="icon-item"
              @click="navigateTo(option.route)"
            >
              <div class="icon-background">
                <q-icon :name="option.icon" size="xl" class="icon" />
              </div>
              <span class="icon-name text-black">{{ option.name }}</span>
            </div>
          </div>
        </div>
      </q-page-container>
      <ClubNavigationMenu />
    </q-layout>
  </template>
  
  <script>
  import BannerPromoScrolling from 'src/components/BannerPromoScrolling.vue';
  import ClubNavigationMenu from 'src/components/ClubNavigationMenu.vue';
  import ClubTopMenu from 'src/components/ClubTopMenu.vue';
  import NotificationBell from 'src/components/NotificationBell.vue';
  
  export default {
    name: "DashboardClub",
    components: {
      ClubNavigationMenu,
      ClubTopMenu,
      NotificationBell,
      BannerPromoScrolling
    },
    data() {
      return {
        club_name: null,
        options: [
          {
            name: "Canchas",
            icon: "event",
            route: "canchas",
          },
          {
            name: "Horarios",
            icon: "query_stats",
            route: "horarios",
          },
          {
            name: "Bloqueos",
            icon: "o_school",
            route: "bloqueos",
          },
          {
            name: "Perfil",
            icon: "o_emoji_events",
            route: "creartorneos",
          },
          {
            name: "Cuentas",
            icon: "o_payments",
            route: "cuentas",
          },
        ],
      };
    },
    methods: {
      navigateTo(route) {
        this.$router.push(`/club/${route}`);
      },
      fetchClubNameFromToken() {
        const token = localStorage.getItem("token");
        if (token) {
          const base64Url = token.split(".")[1];
          const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
          const payload = JSON.parse(atob(base64));
          this.club_name = payload.full_name || "Club";
        }
      },
    },
    mounted() {
      this.fetchClubNameFromToken();
    },
  };
  </script>
  
  <style scoped>
  
  .body {
    background-image: url("src/assets/menu/padelcourt.jpeg");
    background-size: cover;
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
  
  /* Cuadrícula de iconos */
  .icon-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); /* Columnas automáticas */
    gap: 16px; /* Espacio entre iconos */
    padding: 16px; /* Espaciado interno */
  }
  
  .icon-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    cursor: pointer;
    transition: transform 0.2s, opacity 0.2s;
  }
  
  .icon-item:hover {
    transform: scale(1.1); /* Efecto hover */
    opacity: 0.9;
  }
  
  .icon-background {
    background-image: url("src/assets/texturafondo.png");
    background-size: cover;
    border-radius: 50px; /* Bordes redondeados */
    padding: 16px; /* Espaciado interno */
    display: flex;
    align-items: center;
    justify-content: center;
    width: 80px; /* Ancho del contenedor */
    height: 80px; /* Alto del contenedor */
    transition: transform 0.2s, box-shadow 0.2s;
  }
  
  .icon-background:hover {
    transform: scale(1.05); /* Efecto hover */
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5); /* Sombra al hacer hover */
  }
  
  .icon {
    color: #ffffff; /* Color del ícono */
  }
  
  .icon-name {
    font-size: 0.9rem;
    color: #ffffff; /* Color del texto */
    margin-top: 8px; /* Espacio entre ícono y texto */
  }
  </style>