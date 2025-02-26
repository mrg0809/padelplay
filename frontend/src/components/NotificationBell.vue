<template>
    <q-btn flat round icon="o_notifications" @click="goToNotifications" size="lg">
      <q-badge v-if="unreadCount > 0" color="red" floating>{{ unreadCount }}</q-badge>
    </q-btn>
  </template>
  
  <script>
  import api from "../services/api";
  
  export default {
    name: "NotificationBell",
    data() {
      return {
        unreadCount: 0,
      };
    },
    async mounted() {
      await this.fetchUnreadCount();
    },
    methods: {
        async fetchUnreadCount() {
            try {
                const response = await api.get("/notifications");
                const notifications = Array.isArray(response.data.data) ? response.data.data : []; 
                this.unreadCount = notifications.filter((notification) => !notification.is_read).length;
            } catch (error) {
                console.error("Error fetching unread count:", error);
            }
        },
      goToNotifications() {
        this.$router.push("/notifications");
      },
    },
  };
  </script>
  