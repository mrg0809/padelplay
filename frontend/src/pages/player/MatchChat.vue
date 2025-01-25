<template>
    <q-layout view="hHh lpR fFf" class="bg-dark text-white">
      <q-header elevated class="bg-primary text-white">
     
          <div class="header-content">
          <div class="greeting">
              <img src="/src/assets/padelplay.png" alt="Logo" class="logo-icon" />
            </div>
        <!-- Iconos de la derecha -->
            <div class="header-icons">
              <q-btn flat round icon="close" @click="goBack" />
            </div>
          </div>
        
      </q-header>
  
      <q-page-container>
        <q-page class="q-pa-md">
          <!-- Pasar el matchId como prop al componente -->
          <MatchChatRoom :matchId="matchId" />
        </q-page>
      </q-page-container>
      <PlayerNavigationMenu />
    </q-layout>
  </template>
  
  <script>
  import MatchChatRoom from 'src/components/MatchChatRoom.vue';
  import PlayerNavigationMenu from 'src/components/PlayerNavigationMenu.vue';
  import { useRoute } from 'vue-router';
  
  export default {
    components: {
      MatchChatRoom,
      PlayerNavigationMenu
    },
    setup() {
      const route = useRoute();
      // Obtener el matchId desde los parámetros de la ruta
      const matchId = route.params.matchId;
  
      const goBack = () => {
        window.history.back();
      };
  
      return {
        matchId,
        goBack,
      };
    },
  };
  </script>
  
  <style scoped>
  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 16px;
    background-color: #000000; 
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
    width: 60px; 
    height: 60px;
  }

  </style>
  