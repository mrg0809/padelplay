<template>
    <q-layout view="hHh lpR fFf" class="bg-dark text-white">
      <q-header elevated class="text-white">
        <div class="header-content">
          <div class="greeting">
            <img src="/src/assets/padelplay.png" alt="Logo" class="logo-icon" />
          </div>
          <div class="header-icons"></div>
        </div>
      </q-header>
  
      <!-- Agregar q-page-container -->
      <q-page-container>
        <q-page class="q-pa-md">
          <PaymentMethodsComponent />
        </q-page>
      </q-page-container>
      <PlayerNavigationMenu />
    </q-layout>
  </template>
  
  <script setup>
  import { useRouter } from "vue-router";
  import { useSummaryStore } from "src/stores/summaryStore"; // Asegúrate de que existe
  import PaymentMethodsComponent from "src/components/PaymentMethodsComponent.vue";
  import PlayerNavigationMenu from "src/components/PlayerNavigationMenu.vue";
  
  const summaryStore = useSummaryStore();
  const router = useRouter();
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
    width: 60px; /* Ajusta el tamaño del logo */
    height: 60px;
  }
</style>