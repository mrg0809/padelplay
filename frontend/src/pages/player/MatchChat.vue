<template>
    <q-layout view="hHh lpR fFf" class="bg-dark text-white">
      <q-header elevated class="bg-primary text-white">
        <q-toolbar>
          <q-btn flat round icon="arrow_back" @click="goBack" />
          <q-toolbar-title>Chat del Partido</q-toolbar-title>
        </q-toolbar>
      </q-header>
  
      <q-page-container>
        <q-page class="q-pa-md">
          <!-- Pasar el matchId como prop al componente -->
          <MatchChatRoom :matchId="matchId" />
        </q-page>
      </q-page-container>
    </q-layout>
  </template>
  
  <script>
  import MatchChatRoom from 'src/components/MatchChatRoom.vue';
  import { useRoute } from 'vue-router';
  
  export default {
    components: {
      MatchChatRoom,
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
  .messages {
    max-height: 70vh;
    overflow-y: auto;
    padding: 16px;
  }
  
  .message {
    margin: 8px 0;
    display: flex;
    flex-direction: column;
  }
  
  .message.mine {
    align-items: flex-end;
  }
  
  .message.theirs {
    align-items: flex-start;
  }
  
  .message-content {
    background-color: #007bff;
    color: white;
    padding: 8px 12px;
    border-radius: 12px;
    max-width: 70%;
  }
  
  .message-time {
    font-size: 0.75rem;
    color: #ccc;
    margin-top: 4px;
  }
  
  .message-input {
    display: flex;
    align-items: center;
    padding: 16px;
    background-color: #1e1e1e;
  }
  </style>
  