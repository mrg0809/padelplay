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

    <q-page-container>
      <q-page class="q-pa-md">
        <div v-if="loading" class="text-center">
          <q-spinner-dots color="primary" size="xl" />
        </div>
        <div v-else>
          <!-- Información del club -->
          <div class="q-mb-md text-center">
            <img
              v-if="clubDetails?.logo_url"
              :src="clubDetails.logo_url"
              alt="Club Logo"
              style="max-width: 150px; border-radius: 8px;"
            />
          </div>
          <q-card class="tabs-section">
            <q-card-section>
          <!-- Pestañas del Club -->
          <q-tabs v-model="selectedTab" align="justify" class="text-white">
            <q-tab name="info" label="Info" icon="info" />
            <q-tab name="reservations" label="Reservas" icon="event" />
            <q-tab name="tournaments" label="Torneos" icon="emoji_events" />
            <q-tab name="wall" label="Muro" icon="chat" />
          </q-tabs>
        </q-card-section>
          </q-card>
          <q-separator />

          <!-- Contenido de las pestañas -->
          <!-- Pestaña Info -->
          
          <div v-if="selectedTab === 'info'">
            <q-card class="tabs-section">
              <q-card-section>
            <p><strong>Dirección:</strong> {{ clubDetails?.address || "No disponible" }}</p>
            <p v-if="clubDetails?.city"><strong>Ciudad:</strong> {{ clubDetails.city }}, {{ clubDetails.state }}, {{ clubDetails.country }}</p>

            <div id="map" style="height: 200px;" v-if="coordinates"></div>
            
            <div v-if="clubDetails">
              <div class="q-mt-md text-center">
                <q-btn
                  v-if="coordinates"
                  flat
                  round
                  icon="mdi-google-maps"
                  color="blue"
                  class="q-my-md"
                  size="xl"
                  @click="openMaps(coordinates)"
                />
                <q-btn
                  v-if="clubDetails.facebook_url"
                  flat
                  round
                  icon="mdi-facebook"
                  color="blue"
                  class="q-mx-sm"
                  size="xl"
                  @click="openSocialLink(clubDetails.facebook_url)"
                />
                <q-btn
                  v-if="clubDetails.instagram_url"
                  flat
                  round
                  icon="mdi-instagram"
                  color="purple"
                  class="q-mx-sm"
                  size="xl"
                  @click="openSocialLink(clubDetails.instagram_url)"
                />
                <q-btn
                  v-if="clubDetails.tiktok_url"
                  flat
                  round
                  icon="mdi-tiktok"
                  color="white"
                  class="q-mx-sm"
                  size="xl"
                  @click="openSocialLink(clubDetails.tiktok_url)"
                />
                <q-btn
                  v-if="clubDetails.whatsapp_number"
                  flat
                  round
                  icon="mdi-whatsapp"
                  color="green"
                  class="q-mx-sm"
                  size="xl"
                  @click="openWhatsApp(clubDetails.whatsapp_number)"
                />
              </div>
            </div>
          </q-card-section>
        </q-card>
          </div>
          <!-- Pestaña reservas -->
          <div v-if="selectedTab === 'reservations'">
            <q-card class="tabs-section">
              <q-card-section>
            <!-- Muestra fechas -->
            <div class="q-mt-lg days-container">
              <q-btn flat icon="arrow_back" @click="previousWeek" />
              <div class="days-scroll">
                <q-btn
                  v-for="(day, index) in days"
                  :key="index"
                  :outline="selectedDay !== day.date"
                  color="grey"
                  class="day-button"
                  @click="selectDay(day.date)"
                >
                  <div>{{ day.label }}</div>
                  <div class="month-label">{{ day.month }}</div>
                </q-btn>
              </div>
              <q-btn flat icon="arrow_forward" @click="nextWeek" />
            </div>
            <!-- Muestra horarios disponibles -->
            <div class="available-times q-mt-lg">
              <div v-if="loadingTimes" class="text-center">
                <q-spinner-dots color="white" size="xl" />
              </div>
              <div v-else class="time-grid">
                <q-btn
                  v-for="time in consolidatedTimes"
                  :key="time"
                  :label="time"
                  :color="time === selectedTime ? 'green' : 'grey'"
                  class="time-slot"
                  @click="selectTime(time)"
                />
              </div>
            </div>
            <!-- Canchas disponibles y selección de tiempo -->
            <div v-if="selectedTime" class="q-mt-lg">
              <h5>Canchas disponibles para {{ selectedTime }}:</h5>
              <div v-if="loadingCourts" class="text-center">
                <q-spinner-dots color="white" size="lg" />
              </div>
              <div v-else>
                <q-list bordered separator>
                  <q-expansion-item
                    v-for="court in availableCourts"
                    :key="court.id"
                    expand-separator
                    :label="court.name"
                    :caption="`${court.is_indoor ? 'Techada' : 'Aire libre'}`" 
                    class="court-expansion-item"
                  >
                    <q-card class="court-card">
                      <q-card-section class="row q-gutter-sm justify-center">
                        <q-btn
                          v-for="option in timeOptions"
                          :key="option.duration"
                          color="primary"
                          @click="selectDuration(option, court)"
                          class="time-option-btn" 
                        >
                          <div class="time-option-label">
                            <span>${{ getCourtPrice(court, option.duration) }}</span>
                            <br>
                            <span class="duration">{{ option.duration }} min</span>
                          </div>
                        </q-btn>
                      </q-card-section>
                    </q-card>
                  </q-expansion-item>
                </q-list>
              </div>
            </div>
          </q-card-section>
        </q-card>
          </div>
          <!-- Seccion Torneos -->
          <div v-if="selectedTab === 'tournaments'">
            <div class="q-mt-md tournament-list">
              <div
                v-for="tournament in tournaments"
                :key="tournament.id"
                class="tournament-card"
                @click="goToTournamentDetails(tournament.id)"
              >
                <h5>{{ tournament.name }}</h5>
                <p>Fecha: {{ tournament.start_date }}</p>
                <p>Categoría: {{ tournament.category }}</p>
                <p>Género: {{ tournament.gender }}</p>
              </div>
              <p v-if="!tournaments.length" class="text-center q-mt-md">
                No hay torneos disponibles en este club.
              </p>
            </div>
          </div>

          <div v-if="selectedTab === 'wall'">
            <h4 class="text-center">Muro del Club</h4>
            <p>Aquí se mostrarán las publicaciones del club.</p>
          </div>
            
        </div>
      </q-page>
    </q-page-container>
    <PlayerNavigationMenu />
  </q-layout>
</template>

<script>
import { ref, onMounted, watch } from "vue";
import { supabase } from "../../services/supabase";
import { useRoute, useRouter } from "vue-router";
import { useQuasar } from "quasar";
import api from "../../api";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import BannerPromoScrolling from "src/components/BannerPromoScrolling.vue";
import NotificationBell from "src/components/NotificationBell.vue";
import PlayerNavigationMenu from "src/components/PlayerNavigationMenu.vue";

export default {
  components: {
    BannerPromoScrolling,
    NotificationBell,
    PlayerNavigationMenu,
  },
  setup() {
    const route = useRoute();
    const router = useRouter();
    const $q = useQuasar();
    const clubDetails = ref(null);
    const coordinates = ref(null);
    const loading = ref(false);
    const days = ref([]);
    const selectedDay = ref("");
    const availableTimes = ref([]);
    const consolidatedTimes = ref([]);
    const selectedTime = ref(null);
    const loadingTimes = ref(false);
    const currentDate = ref(new Date());
    const selectedTab = ref("info");
    const availableCourts = ref([]);
    const selectedCourt = ref(null);
    const selectedDuration = ref(null);
    const timeOptions = ref([
      { label: "60 minutos", duration: 60 },
      { label: "90 minutos", duration: 90 },
      { label: "120 minutos", duration: 120 },
    ]);
    const tournaments = ref([])
    const loadingCourts = ref(false);

    const clubId = route.params.clubId;

    const getCourtPrice = (court, duration) => {
      if (!court) return 0;
      if (duration === 60) {
        return court.price_per_hour || 0;
      } else if (duration === 90) {
        return court.price_per_hour_and_half || 0;
      } else if (duration === 120) {
        return court.price_per_two_hour || 0;
      }
      return 0;
    };

    watch(selectedTab, (newTab) => {
      if (newTab === "info" && coordinates.value) {
        setTimeout(() => {
          const mapElement = document.getElementById("map");
          if (mapElement && !mapElement._leaflet_id) {
            initMap(coordinates.value);
          }
        }, 100); // Espera a que el contenedor del mapa esté completamente renderizado
      }
    });

    onMounted(async () => {
      if (!clubId) {
        console.error("Club ID is undefined");
        return;
      }

      try {
        loading.value = true;
        const { data, error } = await supabase
          .from("clubs")
          .select("*, geolocation, latitude, longitude, city, state, country")
          .eq("id", clubId)
          .single();

        if (error) {
          throw error;
        }

        clubDetails.value = data;

        if (data?.geolocation?.coordinates) {
          coordinates.value = {
            lat: data.geolocation.coordinates[1],
            lng: data.geolocation.coordinates[0],
          };
        } else if (data.latitude && data.longitude) {
          coordinates.value = {
            lat: data.latitude,
            lng: data.longitude,
          };
        } else {
          console.error("No valid coordinates available");
        }

        if (route.params.tab) {
          selectedTab.value = route.params.tab;
        } else if (route.query.tab){
          selectedTab.value = route.query.tab;
        }

        generateDays();
        fetchAvailableTimes();
        await fetchTournaments();

        if (selectedTab.value === "info" && coordinates.value) {
          setTimeout(() => {
            const mapElement = document.getElementById("map");
            if (mapElement && !mapElement._leaflet_id) {
              initMap(coordinates.value);
            }
          }, 100); // Espera a que el contenedor esté completamente renderizado
        }
        
      } catch (error) {
        console.error("Error al obtener detalles del club:", error.message);
        $q.notify({
          type: "negative",
          message: "Error al cargar detalles del club.",
        });
      } finally {
        loading.value = false;
      }
    });

    const fetchTournaments = async () => {
      try {
        const { data, error } = await supabase
          .from("tournaments")
          .select("id, name, start_date, category, gender")
          .eq("club_id", clubId);

        if (error) {
          console.error("Error al obtener los torneos:", error.message);
          return;
        }

        tournaments.value = data;
      } catch (err) {
        console.error("Error inesperado:", err.message);
      }
    };

    const generateDays = () => {
      days.value = [];
      for (let i = 0; i < 7; i++) {
        const date = new Date(currentDate.value);
        date.setDate(currentDate.value.getDate() + i);
        days.value.push({
          date: date.toISOString().split("T")[0],
          label: date.toLocaleDateString("es-ES", { weekday: "short", day: "numeric" }),
          month: date.toLocaleDateString("es-ES", { month: "short" }).toUpperCase(),
        });
      }
      selectedDay.value = days.value[0].date;
    };

    const previousWeek = () => {
      const today = new Date();
      const firstVisibleDay = new Date(currentDate.value);

      // Asegurarse de que no se retroceda más allá del día actual
      if (
        firstVisibleDay.getFullYear() === today.getFullYear() &&
        firstVisibleDay.getMonth() === today.getMonth() &&
        firstVisibleDay.getDate() === today.getDate()
      ) {
        console.log("No se pueden seleccionar días anteriores al día actual.");
        return;
      }

      // Retrocede una semana
      currentDate.value.setDate(currentDate.value.getDate() - 7);
      generateDays();
      fetchAvailableTimes();
    };

    const nextWeek = () => {
      currentDate.value.setDate(currentDate.value.getDate() + 7);
      generateDays();
      fetchAvailableTimes();
    };

    const fetchAvailableTimes = async () => {
      if (!clubId || !selectedDay.value) return;

      try {
        loadingTimes.value = true;
        const response = await api.get(`/reservations/available-times`, {
          params: {
            club_id: clubId,
            date: selectedDay.value,
          },
        });

        const rawAvailableTimes = response.data.available_times;

        // Consolidar horarios únicos independientemente de la cancha
        let allTimes = Object.values(rawAvailableTimes).flat();

        // Redondear todos los horarios al intervalo más cercano de 30 minutos
        const roundToNearest30 = (time) => {
          const [hour, minute] = time.split(":").map(Number);
          const roundedMinute = minute < 15 ? 0 : minute < 45 ? 30 : 0;
          const roundedHour = minute >= 45 ? hour + 1 : hour;
          return `${String(roundedHour).padStart(2, "0")}:${String(roundedMinute).padStart(2, "0")}`;
        };

        allTimes = allTimes.map(roundToNearest30);

        // Eliminar duplicados y ordenar
        allTimes = [...new Set(allTimes)].sort();

        // Filtrar horarios pasados si el día seleccionado es hoy
        const now = new Date();
        const selectedDate = new Date(`${selectedDay.value}T00:00:00`); // Forzar zona horaria local

        if (
          selectedDate.getFullYear() === now.getFullYear() &&
          selectedDate.getMonth() === now.getMonth() &&
          selectedDate.getDate() === now.getDate()
        ) {
          const currentMinutes = now.getMinutes();
          const currentHour = now.getHours();

          // Redondear hacia el siguiente intervalo de 30 minutos
          let roundedHour = currentHour;
          let roundedMinutes = currentMinutes < 30 ? 30 : 0;

          if (currentMinutes >= 30) {
            roundedHour += 1;
          }

          const currentTimeRounded = `${String(roundedHour).padStart(2, "0")}:${String(roundedMinutes).padStart(2, "0")}`;

          allTimes = allTimes.filter((time) => time >= currentTimeRounded);
        }

        consolidatedTimes.value = allTimes;
      } catch (error) {
        console.error("Error al obtener horarios disponibles:", error.message);
        $q.notify({
          type: "negative",
          message: "Error al cargar horarios disponibles.",
        });
      } finally {
        loadingTimes.value = false;
      }
    };

    const initMap = ({ lat, lng }) => {
      const mapElement = document.getElementById("map");
      if (!mapElement || mapElement._leaflet_id) {
        return; // Si el mapa ya está inicializado, no lo reinicialices
      }

      const map = L.map("map").setView([lat, lng], 15);

      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      }).addTo(map);

      L.marker([lat, lng]).addTo(map)
        .bindPopup(clubDetails.value.name)
        .openPopup();
    };


    const fetchAvailableCourts = async () => {
      if (!clubId || !selectedDay.value || !selectedTime.value) return;

      try {
        loadingCourts.value = true;
        const response = await api.get(`/reservations/available-courts`, {
          params: {
            club_id: clubId,
            date: selectedDay.value,
            time: selectedTime.value,
          },
        });
        availableCourts.value = response.data.available_courts;
      } catch (error) {
        console.error("Error al obtener canchas disponibles:", error.message);
        $q.notify({
          type: "negative",
          message: "Error al cargar canchas disponibles.",
        });
      } finally {
        loadingCourts.value = false;
      }
    };


    const selectDay = (day) => {
      selectedDay.value = day;
      fetchAvailableTimes();
    };

    const selectTime = (time) => {
      selectedTime.value = time;
      fetchAvailableCourts();
    };


    const selectCourt = (court) => {
      selectedCourt.value = court;
    };

    const selectDuration = (option, court) => {
      if (!court || !selectedDay.value || !selectedTime.value) {
        console.error("Datos incompletos para la reserva");
        $q.notify({
          type: "negative",
          message: "No se pudo completar la reserva. Por favor, verifica los datos.",
        });
        return;
      }

      selectedCourt.value = court;
      selectedDuration.value = option.duration;

      const reservationDetails = {
        clubId: clubDetails.value?.id || "ID de club no especificado",
        clubName: clubDetails.value?.name || "Nombre de club no especificado",
        courtId: court.id || "ID de cancha no especificado",
        courtName: court.name || "Nombre de cancha no especificado",
        date: selectedDay.value || "Fecha no especificada",
        time: selectedTime.value || "Hora no especificada",
        duration: selectedDuration.value || 0,
        price: getCourtPrice(court, option.duration) || 0,
      };

      router.push({
        name: "CheckoutPage",
        query: reservationDetails,
      });
    };


    const openMaps = ({ lat, lng }) => {
      if (!lat || !lng) {
        console.error("Invalid coordinates:", { lat, lng });
        return;
      }
      const mapsUrl = `https://www.google.com/maps?q=${lat},${lng}`;
      window.open(mapsUrl, "_blank");
    };

    const openSocialLink = (url) => {
      if (url) {
        window.open(url, "_blank");
      }
    };

    const openWhatsApp = (number) => {
      if (number) {
        const whatsappUrl = `https://wa.me/${number}`;
        window.open(whatsappUrl, "_blank");
      }
    };

    return {
      clubDetails,
      coordinates,
      loading,
      openMaps,
      days,
      selectedDay,
      availableTimes,
      consolidatedTimes,
      selectedTime,
      availableCourts,
      selectedCourt,
      selectedDuration,
      timeOptions,
      loadingTimes,
      loadingCourts,
      selectDay,
      selectTime,
      selectCourt,
      selectDuration,
      previousWeek,
      nextWeek,
      selectedTab,
      getCourtPrice,
      openSocialLink,
      openWhatsApp,
      tournaments,
      fetchTournaments,
    };
  },
  methods: {
    goBack() {
      this.$router.back();
    },
    goToTournamentDetails(tournamentId) {
      this.$router.push({ name: "TournamentDetails", params: { tournamentId } });
    },
  },
};
</script>

<style scoped>
.club-logo {
  width: 300px;
  border-radius: 8px;
  margin-bottom: 16px;
}
.court-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 8px;
  justify-content: center;
  margin-top: 16px;
}
.available-times {
  margin-top: 16px;
}
.logo-icon {
    width: 60px; /* Ajusta el tamaño del logo */
    height: 60px;
}
.header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 16px;
    background-color: #000000; /* Fondo del encabezado */
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
.time-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(70px, 1fr));
  gap: 8px;
  justify-content: center;
}
.time-slot {
  text-align: center;
  font-size: 0.9rem;
  padding: 6px;
  height: 40px;
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
.q-list {
  margin-top: 16px;
}
.q-expansion-item {
  background-color: #333;
  color: #fff;
}
.court-expansion-item {
  background-color: #222; 
  color: #fff; 
}
.court-card {
  background-color: #222; 
  padding: 10px; 
  border-radius: 5px; 
}
.tabs-section {
  margin-bottom: 10px;
  background-image: url(../../assets/texturafondo.png);
  background-size: cover;
  border-radius: 20px;
}
.time-option-btn {
  width: 88px; 
  margin: 3px; 
}
.tournament-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.tournament-card {
  background-image: url(../../assets/texturafondo.png);
  background-size: cover;
  padding: 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.tournament-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
}

.tournament-card h5 {
  margin: 0 0 8px;
  color: #ffd700;
}

.tournament-card p {
  margin: 4px 0;
  color: #ccc;
}
</style>
