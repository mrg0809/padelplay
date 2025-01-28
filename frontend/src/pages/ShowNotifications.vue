<template>
  <q-layout view="hHh lpR fFf" class="bg-dark text-white">
    <q-header elevated class="bg-primary text-white">
      <div class="header-content">
        <div class="greeting">
          <img src="/src/assets/padelplay.png" alt="Logo" class="logo-icon" />
        </div>
        <div class="header-icons">
          <q-btn flat round icon="close" @click="goBack" />
        </div>
      </div>
    </q-header>

    <q-page-container>
      <q-page class="q-pa-md">
        <q-card flat bordered class="text-black">
          <q-card-section>
            <div class="text-h6 text-center">Notificaciones</div>
          </q-card-section>

          <div v-if="notifications.length === 0" class="text-center q-my-md">
            <q-icon name="o_notifications_off" size="64px" color="black" />
            <p>No tienes notificaciones pendientes.</p>
          </div>

          <q-list v-else>
            <q-item
              v-for="notification in notifications"
              :key="notification.id"
              clickable
              class="notification-item"
            >
              <q-item-section avatar @click="markAsRead(notification.id)">
                <q-icon name="o_notifications" size="36px" color="white" />
              </q-item-section>
              <q-item-section @click="markAsRead(notification.id)">
                <q-item-label class="text-bold">{{ notification.title }}</q-item-label>
                <q-item-label caption>{{ notification.message }}</q-item-label>
                <q-item-label caption class="text-grey text-sm">
                  {{ formatDate(notification.created_at) }}
                </q-item-label>
              </q-item-section>
              <q-item-section side>
                <q-btn
                  v-if="!notification.is_read"
                  flat
                  round
                  icon="done"
                  color="white"
                  size="sm"
                  class="q-mr-sm"
                  @click.stop="markAsRead(notification.id)"
                />
                <q-btn
                  flat
                  round
                  icon="close"
                  color="white"
                  size="sm"
                  class="q-mr-sm"
                  @click.stop="deleteNotification(notification.id)"
                />
              </q-item-section>
            </q-item>
          </q-list>
        </q-card>
      </q-page>
    </q-page-container>
  </q-layout>
</template>
  
<script>
import api from "../api";

export default {
  data() {
    return {
      notifications: [],
    };
  },
  async mounted() {
    await this.fetchNotifications();
  },
  methods: {
    async fetchNotifications() {
      try {
        const response = await api.get("/notifications/");
        const data = response.data;

        // Validar si la respuesta tiene datos
        if (data && Array.isArray(data.data) && data.data.length > 0) {
          this.notifications = data.data;
        } else {
          this.notifications = []; // Asegurarse de que esté vacío si no hay notificaciones
        }
      } catch (error) {
        console.error("Error fetching notifications:", error);
        this.notifications = []; // Manejo en caso de error
      }
    },
    async markAsRead(notificationId) {
      try {
        await api.put(`/notifications/${notificationId}/read`);
        this.fetchNotifications(); // Actualizar la lista
      } catch (error) {
        console.error("Error marking notification as read:", error);
      }
    },
    async deleteNotification(notificationId) {
      try {
        await api.delete(`/notifications/${notificationId}`);
        this.fetchNotifications(); // Actualizar la lista después de eliminar
      } catch (error) {
        console.error("Error deleting notification:", error);
      }
    },
    formatDate(timestamp) {
      if (!timestamp) return "Fecha desconocida";
      const options = { year: "numeric", month: "long", day: "numeric", hour: "2-digit", minute: "2-digit" };
      return new Date(timestamp).toLocaleDateString("es-MX", options);
    },
    goBack() {
      this.$router.back();
    },
  },
};
</script>

<style scoped>
.notification-item {
  margin-bottom: 10px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 10px;
  background-image: url(../assets/texturafondo.png);
  background-size: cover;
}

.notification-item:hover {
  background-color: #292929;
}
.text-bold {
  font-weight: bold;
}
.text-grey {
  color: grey;
}
.logo-icon {
  width: 60px; /* Ajusta el tamaño del logo */
  height: 60px;
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
</style>

  