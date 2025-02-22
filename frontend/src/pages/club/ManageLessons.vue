<template>
    <q-layout view="hHh lpR fFf" class="body text-white">
      <q-header elevated class="bg-primary text-white">
        <div class="header-content">
          <div class="greeting">
            <img src="/src/assets/padelplay.png" alt="Logo" class="logo-icon" />
            Configura clases
          </div>
          <div class="header-icons">
            <q-btn flat round icon="arrow_back" @click="goBack" />
          </div>
        </div>
      </q-header>
  
      <q-page-container>
        <q-page class="q-pa-md">
         



          <!-- Botón flotante para agregar producto -->
          <q-btn
            glossy
            round
            size="lg"
            color="black"
            icon="add"
            class="fixed-bottom-right q-mb-xl"
            @click="openLessonDialog"
          />
        </q-page>
  

      </q-page-container>
      <ClubNavigationMenu />
    </q-layout>
  </template>
  
  <script>
  import { ref, onMounted } from "vue";
  import { supabase } from "src/services/supabase";
  import { useRouter } from "vue-router";
  import { useQuasar } from 'quasar';
  import api from "../../api";
  import ClubNavigationMenu from "src/components/ClubNavigationMenu.vue";
  
  export default {
    name: "ManageLessons",
    components: {
      ClubNavigationMenu,
    },
    setup() {
      const router = useRouter();

      const goBack = () => {
        router.back();
      };
  
      onMounted(() => {

      });
  
      return {
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
  
  .body {
    background-image: url(../../assets/menu/padelcourtfloor.jpg);
    background-size: cover;
  }

  .fixed-bottom-right {
    position: fixed;
    bottom: 80px;
    right: 20px;
    z-index: 1000;
  }
  
  </style>