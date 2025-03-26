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
              <h3>{{ coach.name }}</h3>
              <p>Especialidad: {{ coach.coach_focus }}</p>
              <p>Resumen: {{ coach.coach_resume }}</p>

              <div class="q-mt-lg days-container">
                <q-btn flat round icon="arrow_back" size="xs"/>
                <div class="days-scroll">
                  <q-btn
                    v-for="(date, index) in availableDates"
                    :key="index"
                    :name="index"
                    :outline="selectedDate && selectedDate.date.getTime() !== date.date.getTime()"
                    color="grey"
                    class="day-button"
                    @click="selectDay(date.date)"
                  >
                    <div>{{ date.formattedDate }}</div>
                    <div class="month-label">{{ date.month }}</div>
                  </q-btn>
                </div>
                <q-btn flat round icon="arrow_forward" size="xs" />
              </div>

              <div v-if="selectedDate">
                <h3>Horarios Disponibles para {{ selectedDate.day }}</h3>
                <div class="time-slots">
                  <q-btn
                    v-for="time in availableTimes"
                    :key="time"
                    @click="selectTime(time, selectedDate.day)"
                    color="grey"
                    :class="{ 'selected': selectedTime === time && selectedDay === selectedDate.day }"
                    class="time-option-btn"
                  >
                    {{ time }}
                  </q-btn>
                </div>
              </div>

              <button v-if="selectedTime" @click="startReservation">Reservar Clase</button>
            </div>
            <div v-else class="q-pa-md">
              <q-spinner-cube color="orange" size="5.5em" />
            </div>
          </q-card-section>
        </q-card>
      </q-page>
      <PlayerNavigationMenu />
    </q-page-container>
  </q-layout>
</template>

<script>
import { ref, onMounted, computed } from "vue";
import { useRoute } from "vue-router";
import { getCoachDetails } from "src/services/supabase/coaches";
import { processAvailability, generateAvailableDates } from "src/helpers/coachUtils";
import api from "../../services/api"
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
    const selectedDateIndex = ref(0);
    const availableDates = ref([]);
    const availableTimes = ref(null);
    const selectedDate = ref(null);

    const loadCoachDetails = async () => {
      try {
        const coachDetails = await getCoachDetails(coachId, clubId);
        coach.value = coachDetails;
        if (coachDetails.availability) {
          availability.value = processAvailability(coachDetails.availability);
          availableDates.value = generateAvailableDates(availability.value);
        }
      } catch (error) {
        console.error("Error al cargar detalles del coach:", error);
      }
    };

    const selectDay = (date) => {
      const selected = availableDates.value.find(
        (availableDate) => availableDate.date.getTime() === date.getTime()
      );
      if (selected) {
        selectedDate.value = selected;
        loadAvailableTimes();
      }
    };

    const selectTime = (time, day) => {
      selectedTime.value = time;
      selectedDay.value = day;
    };

    const loadAvailableTimes = async () => {
      if (selectedDate.value) {
        try {
          const response = await api.get("/lessons/available-times", {
            params: {
              club_id: clubId,
              date: selectedDate.value.date.toISOString().split("T")[0],
              coach_id: coachId,
            },
          });

          if (response.data) {
            availableTimes.value = response.data.available_times;
          }
        } catch (error) {
          console.error("Error al obtener horarios disponibles:", error);
        }
      }
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
      availableDates,
      selectedDateIndex,
      selectedDate,
      selectDay,
      availableTimes,
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
  color: #fff;
  border-radius: 8px;
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2);
}

.time-option-btn {
  width: 88px;
  margin: 3px;
}

.day-button {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
  
.month-label {
  font-size: 0.75rem;
  color: #aaa;
}
  
.days-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
  
.days-scroll {
  display: flex;
  overflow-x: auto;
  flex-wrap: nowrap;
  gap: 8px;
}

.days-scroll::-webkit-scrollbar {
  display: none;
}
  
</style>