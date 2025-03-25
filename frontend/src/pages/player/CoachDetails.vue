<template>
    <q-layout view="hHh lpR fFf" class="bg-dark text-white">
      <q-header elevated class="text-white">
        <div class="header-content">
          <div class="greeting">
            <img src="/src/assets/padelplay.png" alt="Logo" class="logo-icon" />
          </div>
          <div class="header-icons">
            <NotificationBell />
          </div>
        </div>
        <BannerPromoScrolling />
      </q-header>
      <q-page-container class="home">
        <q-page class="q-pa-md">
          <q-card>
            <q-card-section>
              <div v-if="coach" class="q-pa-md q-gutter-md">
                <div class="q-mx-auto">
                  <q-avatar size="200px" class="q-mb-md">
                    <img :src="coach.players.photo_url || 'default-avatar.png'" />
                  </q-avatar>
                </div>
                <h2>{{ coach.name }}</h2>
                <p>Especialidad: {{ coach.coach_focus }}</p>
                <p>Resumen: {{ coach.coach_resume }}</p>
             
                <div v-for="(day, dayName) in availability" :key="dayName">
                
                <div class="time-slots">
                  <q-btn
                    v-for="time in availability[dayName]"
                    :key="time"
                    @click="selectTime(time, dayName)"
                    color="grey"
                    :class="{ 'selected': selectedTime === time && selectedDay === dayName }"
                    class="time-option-btn"
                  >
                    {{ time }}
                  </q-btn>
                </div>
              </div>
  
                <button v-if="selectedTime" @click="startReservation">Reservar Clase</button>
              </div>
              <div v-else class="q-pa-md">
                Cargando...
              </div>
            </q-card-section>
          </q-card>
        </q-page>
        <PlayerNavigationMenu />
      </q-page-container>
    </q-layout>
  </template>
  
  <script>
  import { ref, onMounted } from "vue";
  import { useRoute } from "vue-router";
  import { getCoachDetails } from "src/services/supabase/coaches";
  import { processAvailability } from "src/helpers/coachUtils";
  import NotificationBell from "src/components/NotificationBell.vue";
  import BannerPromoScrolling from "src/components/BannerPromoScrolling.vue";
  import PlayerNavigationMenu from "src/components/PlayerNavigationMenu.vue";
  
  export default {
    components: {
      NotificationBell,
      BannerPromoScrolling,
      PlayerNavigationMenu,
    },
    setup() {
      const route = useRoute();
      const coachId = route.params.coachId;
      const clubId = route.query.clubId;
      const coach = ref(null);
      const availability = ref({});
      const selectedTime = ref(null);
      const selectedDay = ref(null);
  
      const loadCoachDetails = async () => {
        try {
          const coachDetails = await getCoachDetails(coachId, clubId);
          coach.value = coachDetails;
          if (coachDetails.availability) {
            availability.value = processAvailability(coachDetails.availability);
          }
        } catch (error) {
          console.error("Error al cargar detalles del coach:", error);
        }
      };
  
      const selectTime = (time, day) => {
        selectedTime.value = time;
        selectedDay.value = day;
      };
  
      const startReservation = () => {
        console.log("Iniciar reserva para:", coachId, selectedDay.value, selectedTime.value);
      };
  
      onMounted(loadCoachDetails);
  
      return {
        coach,
        availability,
        selectedTime,
        selectTime,
        startReservation,
      };
    },
  };
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
    width: 60px;
    height: 60px;
  }

  .q-card {
    background-image: url(../../assets/texturafondo.png);
    background-size: cover;
    max-width: 400px;
    margin: auto;
    color: #fff; /* Texto blanco para visibilidad */
    border-radius: 8px; /* Bordes redondeados */
    box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2); /* Sombra para destacar */
    }

    .time-option-btn {
    width: 88px;
    margin: 3px;
  }
  </style>