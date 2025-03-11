<template>
  <q-layout view="hHh lpR fFf" class="body">
    <q-header elevated class="text-white">
      <div class="header-content">
        <div class="greeting">
          <img src="/src/assets/padelplay.png" alt="Logo" class="logo-icon" />
          Bienvenido {{ userStore.fullName }}
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
import { useUserStore } from 'src/stores/userStore';
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router'; // Importa el router

export default {
  name: "DashboardClub",
  components: {
    ClubNavigationMenu,
    ClubTopMenu,
    NotificationBell,
    BannerPromoScrolling
  },
  setup() {
    const userStore = useUserStore();
    const router = useRouter(); // Obtén la instancia del router

    const club_name = ref(null); // Usa ref para datos reactivos
    const options = reactive([ // Usa reactive para arrays de objetos
      { name: "Agenda", icon: "event", route: "agenda" },
      { name: "Reportes", icon: "query_stats", route: "reportes" },
      { name: "Clases", icon: "o_school", route: "clases" },
      { name: "Torneos", icon: "o_emoji_events", route: "torneos" },
      { name: "Pagos", icon: "o_payments", route: "pagos" },
      { name: "Clientes", icon: "o_groups", route: "clientes" },
      { name: "Facturas", icon: "o_receipt_long", route: "facturas" },
      { name: "Instructores", icon: "o_settings_accessibility", route: "instructores" },
      { name: "Comunidad", icon: "o_connect_without_contact", route: "comunidad" },
      { name: "Productos", icon: "o_inventory_2", route: "productos" },
      { name: "Configuración", icon: "o_settings", route: "configuracion" },
      { name: "Soporte", icon: "support_agent", route: "soporte" },
    ]);

    const navigateTo = (route) => {
      router.push(`/club/${route}`); // Usa la instancia del router
    };

    // Si necesitas usar userStore en el template, debes retornarlo
    return {
      userStore,
      club_name,
      options,
      navigateTo,
    };
  },
};
</script>

<style scoped>

.body {
  background-image: url("../assets/menu/padelcourt.jpeg");
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
  background-image: url("../assets/texturafondo.png");
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