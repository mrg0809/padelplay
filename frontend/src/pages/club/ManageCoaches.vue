<template>
    <q-layout view="hHh lpR fFf" class="body text-white">
      <q-header elevated class="bg-primary text-white">
        <div class="header-content">
          <div class="greeting">
            <img src="/src/assets/padelplay.png" alt="Logo" class="logo-icon" />
            Instructores
          </div>
          <div class="header-icons">
            <q-btn flat round icon="arrow_back" @click="goBack" />
          </div>
        </div>
      </q-header>
  
      <q-page-container>
        <q-page class="q-pa-md">
          <div class="q-mb-md">
            <q-card class="transparent-card">
              <q-card-section>
                <h5>Coaches:</h5>
              </q-card-section>
              <q-card-section v-if="coaches.length > 0">
                <q-list bordered separator>
                  <q-item v-for="coach in coaches" :key="coach.id">
                    <q-item-section>
                      <q-item-label>{{ coach.name }}</q-item-label>
                      <q-item-label caption v-if="coach.coach_resume">
                        {{ coach.coach_resume }}
                      </q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-card-section>
              <q-card-section v-else>
                <q-item-label class="text-center text-black">
                  Aún no tienes coaches disponibles
                </q-item-label>
              </q-card-section>
            </q-card>
          </div>
  
          <!-- Botón flotante para agregar coach -->
          <q-btn
            glossy
            round
            size="lg"
            color="black"
            icon="add"
            class="fixed-bottom-right q-mb-xl"
            @click="openCoachDialog"
          />
        </q-page>
      </q-page-container>
  
      <ClubNavigationMenu />
  
      <!-- Diálogo para agregar coach -->
      <q-dialog v-model="isCoachDialogOpen" persistent full-width>
        <q-card class="bg-black">
          <q-card-section>
            <div class="text-h6">Agregar Coach</div>
          </q-card-section>
  
          <q-card-section>
            <q-select
              v-model="selectedCoach"
              :options="availableCoaches"
              option-label="name"
              option-value="user_id"
              label="Selecciona un jugador"
              filled
            />
            <q-input v-model="priceForOne" label="Precio por una persona" filled type="number" />
            <q-input v-model="priceForTwo" label="Precio por dos personas" filled type="number" />
            <q-input v-model="priceForThree" label="Precio por tres personas" filled type="number" />
            <q-input v-model="priceForFour" label="Precio por cuatro personas" filled type="number" />
          </q-card-section>
  
          <q-card-actions align="right">
            <q-btn flat label="Cancelar" color="red" v-close-popup />
            <q-btn flat label="Agregar" color="green" @click="addCoach" />
          </q-card-actions>
        </q-card>
      </q-dialog>
    </q-layout>
  </template>
  
  <script>
  import { ref, onMounted } from "vue";
  import { supabase } from "src/services/supabase";
  import { useRouter } from "vue-router";
  import { useUserStore } from "src/stores/userStore";
  import ClubNavigationMenu from "src/components/ClubNavigationMenu.vue";
  import api from "../../api";
  
  export default {
    name: "ManageCoaches",
    components: {
      ClubNavigationMenu,
    },
    setup() {
      const router = useRouter();
      const userStore = useUserStore();
      const coaches = ref([]);
      const availableCoaches = ref([]);
      const isCoachDialogOpen = ref(false);
      const selectedCoach = ref(null);
      const priceForOne = ref(null);
      const priceForTwo = ref(null);
      const priceForThree = ref(null);
      const priceForFour = ref(null);

  
      const goBack = () => {
        router.back();
      };
  
      const fetchCoaches = async () => {
        try {
          const { data, error } = await supabase
            .from("coaches")
            .select(`
                id, 
                name, 
                coach_resume, 
                players(gender, photo_url, category)
            `)
            .eq("club_id", userStore.clubId)
            .eq("is_active", true);
  
          if (error) throw error;
  
          coaches.value = data.map((coach) => ({
            id: coach.id,
            name: coach.name,
            coach_resume: coach.coach_resume,
            gender: coach.players?.gender || "Desconocido",
            photo_url: coach.players?.photo_url || null,
            category: coach.players?.category || "No especificado",
          }));
        } catch (err) {
          console.error("Error obteniendo coaches:", err.message);
        }
      };
  
      const fetchAvailableCoaches = async () => {
        try {
          const { data, error } = await api.get("/lessons/search-coaches");
          if (error) throw error;
          availableCoaches.value = data;
        } catch (err) {
          console.error("Error obteniendo coaches disponibles:", err.message);
        }
      };
  
      const openCoachDialog = async () => {
        await fetchAvailableCoaches();
        isCoachDialogOpen.value = true;
      };
  
      const addCoach = async () => {
        if (!selectedCoach.value) {
          console.error("Debes seleccionar un jugador.");
          return;
        }
  
        try {
          const payload = {
            user_id: selectedCoach.value.user_id,
            club_id: userStore.clubId,
            price_for_one: priceForOne.value,
            price_for_two: priceForTwo.value,
            price_for_three: priceForThree.value,
            price_for_four: priceForFour.value,
          };
  
          const { data, error } = await api.post("/lessons/add-coach", payload);
          if (error) throw error;
  
          console.log("Coach agregado:", data);
          fetchCoaches();
          isCoachDialogOpen.value = false;
        } catch (err) {
          console.error("Error agregando coach:", err.message);
        }
      };
  
      onMounted(fetchCoaches);
  
      return {
        goBack,
        coaches,
        isCoachDialogOpen,
        openCoachDialog,
        availableCoaches,
        selectedCoach,
        priceForOne,
        priceForTwo,
        priceForThree,
        priceForFour,
        addCoach,
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
  
  .transparent-card {
    background-color: rgba(255, 255, 255, 0.3);
  }
  
  .text-center {
    text-align: center;
  }
  
  .text-grey {
    color: #aaa;
  }
  </style>
  