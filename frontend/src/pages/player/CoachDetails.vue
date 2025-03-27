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
              <div class="text-center q-mb-md">
                <q-avatar size="200px">
                  <img :src="coach.players?.photo_url || 'default-avatar.png'" />
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
                    :outline="selectedDate?.date.getTime() !== date.date.getTime()"
                    :color="selectedDate?.date.getTime() === date.date.getTime() ? 'primary' : 'grey'"
                    class="day-button"
                    @click="selectDay(date.date)"
                  >
                    <div>{{ date.formattedDate }}</div>
                    <div class="month-label">{{ date.month }}</div>
                  </q-btn>
                </div>
                <q-btn flat round icon="arrow_forward" size="xs" />
              </div>

              <div v-if="availableTimes && selectedDate" class="q-mt-md">
                <h4>Horarios Disponibles:</h4>
                <div class="time-slots">
                  <q-btn
                    v-for="time in availableTimes"
                    :key="time"
                    @click="selectTime(time)"
                    :color="selectedTime === time ? 'secondary' : 'grey'"
                    :outline="selectedTime !== time"
                    class="time-option-btn"
                  >
                    {{ time }}
                  </q-btn>
                </div>
              </div>

              <div v-if="selectedTime && priceOptions && priceOptions.length > 0" class="q-mt-md">
                 <h4>Selecciona el número de personas:</h4>
                 <div class="price-options-container">
                    <q-btn
                      v-for="option in priceOptions"
                      :key="option.people"
                      @click="selectPriceOption(option)"
                      :color="selectedPriceOption?.people === option.people ? 'green' : 'secondary'"
                      :outline="selectedPriceOption?.people !== option.people"
                      class="price-option-btn"
                      padding="sm" >
                      <div class="column text-left">
                        <div class="row items-center">
                          <span class="text-h6">{{ option.label }}</span> 
                          <q-icon name="group" class="q-mr-xs" />
                        </div>
                        <span class="text-caption text-white">${{ option.price.toFixed(2) }}</span> 
                      </div>
                    </q-btn>
                 </div>
              </div>

              <div class="q-mt-lg text-center" v-if="selectedPriceOption">
                <q-btn
                  color="accent"
                  label="Continuar Reserva"
                  @click="startReservation"
                  icon-right="shopping_cart"
                  size="lg"
                />
              </div>

            </div>
            <div v-else class="q-pa-md text-center">
              <q-spinner-cube color="orange" size="5.5em" />
              <p class="q-mt-md">Cargando detalles del coach...</p>
            </div>
          </q-card-section>
        </q-card>
      </q-page>
      <PlayerNavigationMenu />
    </q-page-container>
  </q-layout>
</template>

<script>
// El script permanece igual que en la respuesta anterior
import { ref, onMounted, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { getCoachDetails } from "src/services/supabase/coaches";
import { processAvailability, generateAvailableDates } from "src/helpers/coachUtils";
import api from "../../services/api";
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
    const router = useRouter();
    const coachId = route.params.coachId;
    const clubId = route.query.clubId;
    const coach = ref(null);
    const availability = ref({});
    const selectedTime = ref(null);
    const availableDates = ref([]);
    const availableTimes = ref(null);
    const selectedDate = ref(null);
    const selectedPriceOption = ref(null);

    const priceOptions = computed(() => {
      if (!coach.value) return [];
      const options = [];
      if (coach.value.price_for_one != null) options.push({ people: 1, price: coach.value.price_for_one, label: '1' });
      if (coach.value.price_for_two != null) options.push({ people: 2, price: coach.value.price_for_two, label: '2' });
      if (coach.value.price_for_three != null) options.push({ people: 3, price: coach.value.price_for_three, label: '3' });
      if (coach.value.price_for_four != null) options.push({ people: 4, price: coach.value.price_for_four, label: '4' });
      return options;
    });

    const loadCoachDetails = async () => {
      coach.value = null;
      selectedDate.value = null;
      selectedTime.value = null;
      selectedPriceOption.value = null;
      availableTimes.value = null;
      try {
        const coachDetails = await getCoachDetails(coachId, clubId);
        coach.value = coachDetails;
        if (coachDetails?.availability) {
          availability.value = processAvailability(coachDetails.availability);
          availableDates.value = generateAvailableDates(availability.value, 14);
        } else {
            availableDates.value = [];
        }
      } catch (error) {
        console.error("Error al cargar detalles del coach:", error);
      }
    };

    const selectDay = (date) => {
      const selected = availableDates.value.find(
        (availableDate) => availableDate.date.getTime() === date.getTime()
      );
      if (selected && selected.date.getTime() !== selectedDate.value?.date.getTime()) {
        selectedDate.value = selected;
        selectedTime.value = null;
        selectedPriceOption.value = null;
        availableTimes.value = null;
        loadAvailableTimes();
      }
    };

    const selectTime = (time) => {
      selectedTime.value = time;
      selectedPriceOption.value = null;
    };

    const selectPriceOption = (option) => {
      selectedPriceOption.value = option;
    };

    const loadAvailableTimes = async () => {
       if (!selectedDate.value || !clubId || !coachId) {
         availableTimes.value = [];
         return;
      };
      availableTimes.value = null;
      try {
        const response = await api.get("/lessons/available-times", {
          params: {
            club_id: clubId,
            date: selectedDate.value.date.toISOString().split("T")[0],
            coach_id: coachId,
          },
        });
        if (response.data?.available_times) {
          const allTimesSet = new Set();
          Object.values(response.data.available_times).forEach(timesArray => {
            if (Array.isArray(timesArray)) {
              timesArray.forEach(time => allTimesSet.add(time));
            }
          });
          availableTimes.value = Array.from(allTimesSet).sort();
        } else {
          availableTimes.value = [];
        }
      } catch (error) {
        console.error("Error fetching available times:", error);
        availableTimes.value = [];
      }
    };

    const startReservation = () => {
      if (!selectedDate.value || !selectedTime.value || !selectedPriceOption.value) {
        console.error("Información incompleta para la reserva.");
        return;
      }
      const reservationDetails = {
          coachId: coachId,
          coachName: coach.value?.name,
          clubId: clubId,
          date: selectedDate.value.date.toISOString().split("T")[0],
          time: selectedTime.value,
          people: selectedPriceOption.value.people,
          price: selectedPriceOption.value.price,
      };
      console.log("Procediendo al checkout con:", reservationDetails);
      router.push({
         name: 'CheckoutPage',
         query: {
            coachId: reservationDetails.coachId,
            clubId: reservationDetails.clubId,
            date: reservationDetails.date,
            time: reservationDetails.time,
            people: reservationDetails.people,
            price: reservationDetails.price,
            coachName: reservationDetails.coachName
         }
       });
    };

    onMounted(loadCoachDetails);

    return {
      coach,
      selectedTime,
      selectTime,
      startReservation,
      availableDates,
      selectedDate,
      selectDay,
      availableTimes,
      priceOptions,
      selectedPriceOption,
      selectPriceOption,
    };
  },
};
</script>

<style scoped>
/* --- Tus Estilos --- */
.home {
  background-color: #dddddd;
  /* Asegúrate que q-page-container es el elemento correcto para esto */
  /* O podrías aplicarlo a q-page si prefieres el fondo solo en el contenido */
  min-height: 100vh; /* Para asegurar que cubra la altura */
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  background-color: #000000; /* Mantenido */
}

.greeting {
  /* font-size: 1rem; */ /* Comentado si no hay texto */
  /* font-weight: 500; */ /* Comentado si no hay texto */
  display: flex;
  align-items: center;
  gap: 8px; /* Mantenido */
}

.header-icons {
  display: flex;
  gap: 2px; /* Mantenido */
  align-items: center; /* Añadido para alinear verticalmente los íconos */
}

.logo-icon {
  width: 60px; /* Mantenido */
  height: 60px; /* Mantenido */
}

.q-card {
  background-image: url(../../assets/texturafondo.png); /* Mantenido */
  background-size: cover; /* Mantenido */
  max-width: 400px; /* Mantenido */
  margin: 16px auto; /* Ajustado para centrar mejor */
  color: #fff; /* Mantenido */
  border-radius: 8px; /* Mantenido */
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2); /* Mantenido */
}

.time-option-btn {
  width: 88px; /* Mantenido */
  margin: 3px; /* Mantenido */
  /* El padding se quita del template si width/margin son fijos */
}

.day-button {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  /* --- Añadidos/Ajustados --- */
  min-width: 65px; /* Ancho mínimo */
  border: 1px solid #ccc; /* Borde como en mi sugerencia */
  border-radius: 8px; /* Borde redondeado */
  padding: 6px 4px; /* Padding ajustado */
  font-size: 0.8rem; /* Tamaño de fuente */
  line-height: 1.2; /* Interlineado */
  text-align: center;
  /* gap ya está en el padre (.days-scroll) */
}

.month-label {
  font-size: 0.75rem; /* Mantenido */
  color: #aaa; /* Mantenido */
  /* --- Añadidos/Ajustados --- */
  text-transform: uppercase; /* Mayúsculas */
  margin-top: 2px; /* Espacio superior */
}

.days-container {
  display: flex;
  align-items: center;
  justify-content: space-between; /* Mantenido */
  /* overflow: hidden; quitado para no cortar flechas si están muy cerca */
}

.days-scroll {
  display: flex;
  overflow-x: auto; /* Mantenido */
  flex-wrap: nowrap; /* Mantenido */
  gap: 8px; /* Mantenido - gestiona el espacio entre day-button */
  flex-grow: 1; /* Para que ocupe el espacio entre flechas */
  padding: 4px 0; /* Espacio vertical pequeño */
   /* Ocultar barra de scroll */
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none;  /* IE/Edge */
}
.days-scroll::-webkit-scrollbar {
  display: none; /* Chrome/Safari/Opera */ /* Mantenido */
}

/* --- Estilos Adicionales/Modificados --- */

h3 {
    text-align: center;
    color: #FFF; /* Cambiado a blanco para contraste con fondo de imagen */
    margin-bottom: 1rem; /* Añadido margen inferior */
}
h4 {
    margin-bottom: 10px;
    color: #eee; /* Color más claro para contraste */
    font-size: 1rem; /* Tamaño ajustado */
}

/* Contenedores para botones de hora y precio */
.time-slots,
.price-options-container {
  display: flex;
  flex-wrap: wrap; /* Permitir que los botones pasen a la siguiente línea */
  gap: 6px; /* Espacio entre botones (ajusta si prefieres) */
  /* justify-content: center; */ /* Descomenta si quieres centrar los botones */
}

/* Estilo para botones de precio (si quieres diferenciar de time-option-btn) */
.price-option-btn {
  /* Puedes añadir estilos específicos aquí, por ejemplo: */
  /* width: auto; */ /* O un ancho fijo si lo prefieres */
  padding: 6px 12px; /* Padding interno */
  margin: 3px; /* Añadido margen similar a time-option-btn */
}

/* Asegurar que el spinner sea visible sobre el fondo oscuro/imagen */
.q-spinner-cube {
  /* El color ya está definido en el template, pero podrías asegurarlo aquí */
  /* color: orange; */
}
.text-center p {
  color: #ccc; /* Color para el texto "Cargando..." */
}

/* Avatar centrado */
.text-center {
  text-align: center;
}

/* Ajustes responsivos */
@media (max-width: 600px) {
  .q-avatar {
    width: 150px !important;
    height: 150px !important;
  }
  h3 {
    font-size: 1.5rem;
  }
  /* Ajustar ancho de botones de día si es necesario */
  .day-button {
    min-width: 60px;
    padding: 4px 2px;
  }
  /* Ajustar ancho/margen de botones de hora/precio */
  .time-option-btn {
    width: 80px;
    margin: 2px;
  }
    .price-option-btn {
    padding: 5px 10px;
    margin: 2px;
  }
}

</style>