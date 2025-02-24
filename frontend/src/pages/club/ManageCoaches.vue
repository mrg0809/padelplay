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
                    <q-item-section avatar>
                      <q-avatar>
                        <img :src="coach.photo_url || 'default-avatar.png'" />
                      </q-avatar>
                    </q-item-section>
                    <q-item-section @click="goToCoachProfile(coach.id)">     
                      <q-item-label>{{ coach.name }}</q-item-label>
                      <q-item-label caption v-if="coach.coach_focus">
                        {{ coach.coach_focus }}
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

        <!-- Paso 1: Selección del Jugador -->
        <q-card-section v-if="currentStep === 1">
          <q-select
            v-model="selectedCoach"
            :options="filteredAvailableCoaches"
            option-label="name"
            option-value="user_id"
            label="Buscar jugador"
            filled
            use-input
            @filter="filterCoaches"
            class="custom-select"
          />
        </q-card-section>

        <!-- Paso 2: Información Financiera -->
        <q-card-section v-if="currentStep === 2">
          <q-input v-model="priceForOne" label="Entrenamiento individual" filled type="number" />
          <q-input v-model="priceForTwo" label="Entrenamiento pareja" filled type="number" />
          <q-input v-model="priceForThree" label="Entrenamiento 3 jugadores" filled type="number" />
          <q-input v-model="priceForFour" label="Entrenamiento 4 jugadores" filled type="number" />
        </q-card-section>

        <!-- Paso 3: Información del Coach -->
        <q-card-section v-if="currentStep === 3">
          <q-input v-model="coachResume" label="Resumen del Coach" filled type="textarea" />
          <q-input v-model="coachFocus" label="Enfoque del Coach" filled type="textarea" />
        </q-card-section>

        <!-- Paso 4: Disponibilidad -->
        <q-card-section v-if="currentStep === 4">
          <q-list bordered>
            <q-item v-for="(schedule, index) in generalSchedule" :key="index" class="q-mb-md">
              <q-item-section>
                <div class="text-bold">{{ daysOfWeek[index] }}</div>
                <!-- Toggle para activar/desactivar el día -->
                <q-toggle
                  v-model="generalSchedule[index].is_open"
                  label="¿Disponible?"
                  dense
                  color="black"
                />
              </q-item-section>
              <q-item-section v-if="generalSchedule[index].is_open">
                <!-- Inputs para la hora de inicio y fin -->
                <q-input
                  v-model="generalSchedule[index].start_time"
                  label="Hora de inicio"
                  dense
                  outlined
                  color="black"
                  class="text-black"
                  mask="time"
                  :rules="['time']"
                />
                <q-input
                  v-model="generalSchedule[index].end_time"
                  label="Hora de fin"
                  dense
                  outlined
                  color="black"
                  class="text-black"
                  mask="time"
                  :rules="['time']"
                />
              </q-item-section>
            </q-item>
          </q-list>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancelar" color="red" v-close-popup />
          <q-btn flat label="Anterior" color="blue" @click="previousStep" v-if="currentStep > 1" />
          <q-btn flat label="Siguiente" color="green" @click="nextStep" v-if="currentStep < 4" />
          <q-btn flat label="Agregar" color="green" @click="addCoach" v-if="currentStep === 4" />
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
      const filteredAvailableCoaches = ref([]);
      const isCoachDialogOpen = ref(false);
      const selectedCoach = ref(null);
      const priceForOne = ref(null);
      const priceForTwo = ref(null);
      const priceForThree = ref(null);
      const priceForFour = ref(null);
      const coachResume = ref("");
      const coachFocus = ref("");
      const currentStep = ref(1);

      // Disponibilidad
      const daysOfWeek = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"];
      const generalSchedule = ref(
        Array(7).fill(null).map(() => ({
          is_open: false,
          start_time: "09:00",
          end_time: "13:00",
        }))
      );

      const goToCoachProfile = (coachId) => {
        console.log('ir al coach')
        router.push({ name: "CoachProfile", params: { id: coachId }})
      }

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
                coach_focus, 
                players(gender, photo_url, category)
            `)
            .eq("club_id", userStore.clubId)
            .eq("is_active", true);
  
          if (error) throw error;
  
          coaches.value = data.map((coach) => ({
            id: coach.id,
            name: coach.name,
            coach_focus: coach.coach_focus,
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
        const { data, error } = await api.get("/coaches/search-coaches");
        if (error) throw error;
        availableCoaches.value = data;
        filteredAvailableCoaches.value = data;
      } catch (err) {
        console.error("Error obteniendo coaches disponibles:", err.message);
      }
    };

    const filterCoaches = (val, update) => {
      update(() => {
        const needle = val.toLowerCase();
        filteredAvailableCoaches.value = availableCoaches.value.filter(
          (coach) => coach.name.toLowerCase().indexOf(needle) > -1
        );
      });
    };

    const openCoachDialog = async () => {
      await fetchAvailableCoaches();
      isCoachDialogOpen.value = true;
      currentStep.value = 1;
    };

    const nextStep = () => {
      currentStep.value++;
    };

    const previousStep = () => {
      currentStep.value--;
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
          name: selectedCoach.value.name,
          price_for_one: priceForOne.value,
          price_for_two: priceForTwo.value,
          price_for_three: priceForThree.value,
          price_for_four: priceForFour.value,
          coach_resume: coachResume.value,
          coach_focus: coachFocus.value,
          availability: generalSchedule.value
            .filter((day) => day.is_open)
            .map((day, index) => ({
              day: daysOfWeek[index],
              start_time: day.start_time,
              end_time: day.end_time,
            })),
        };

        const { data, error } = await api.post("/coaches/add-coach", payload);
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
      filteredAvailableCoaches,
      selectedCoach,
      priceForOne,
      priceForTwo,
      priceForThree,
      priceForFour,
      coachResume,
      coachFocus,
      currentStep,
      nextStep,
      previousStep,
      addCoach,
      filterCoaches,
      daysOfWeek,
      generalSchedule,
      goToCoachProfile,
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

  .custom-select .q-select__dialog {
  background-color: #ffcc00; /* Color de fondo personalizado */
}

.custom-select .q-select__dialog.q-select__dialog--dark {
  background-color: #333333; /* Color de fondo para el modo oscuro */
}
  </style>
  