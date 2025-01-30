<template>
  <q-layout view="hHh lpR fFf" class="bg-dark text-white">
    <q-header elevated class="text-white">
      <div class="header-content">
        <!-- Saludo -->
        <div class="greeting">
          <img src="/src/assets/padelplay.png" alt="Logo" class="logo-icon" />
        </div>
        <div class="header-icons">
          <NotificationBell />
          <ClubTopMenu />
        </div>
      </div>
      <BannerPromoScrolling />
    </q-header>

    <q-page-container>
      <q-page class="q-pa-md">
        <!-- Selector de Fecha -->
        <div class="q-mb-md">
          <q-input
            v-model="selectedDate"
            type="date"
            label="Selecciona una fecha"
            outlined
            dense
            color="primary"
            @change="fetchReservations"
          />
        </div>

        <!-- Tabla de Reservas -->
        <div class="reservation-calendar">
          <table class="reservation-table">
            <thead>
              <tr>
                <th>Hora</th>
                <th v-for="court in courts" :key="court.id">{{ court.name }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="hour in hours" :key="hour">
                <td>{{ hour }}</td>
                <td
                  v-for="court in courts"
                  :key="court.id"
                  :class="getCellClass(court.id, hour)"
                  @click="handleCellClick(court.id, hour)"
                >
                  <div v-if="reservations[court.id]?.[hour]">
                    <strong>{{ reservations[court.id][hour].playerName }}</strong>
                  </div>
                  <div v-else>-</div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </q-page>
    </q-page-container>
    <!-- Menú de Navegación Inferior -->
    <ClubNavigationMenu />
  </q-layout>
</template>

<script>
import BannerPromoScrolling from "src/components/BannerPromoScrolling.vue";
import ClubNavigationMenu from "src/components/ClubNavigationMenu.vue";
import ClubTopMenu from "src/components/ClubTopMenu.vue";
import NotificationBell from "src/components/NotificationBell.vue";
import { supabase } from "src/services/supabase";

export default {
  data() {
    return {
      selectedDate: new Date().toISOString().split("T")[0], // Fecha predeterminada: hoy
      courts: [], // Canchas del club
      hours: [], // Horas generadas dinámicamente
      reservations: {}, // Datos de las reservas organizados por cancha y hora
      clubId: null, // ID del club extraído del token
    };
  },
  components: {
    ClubNavigationMenu,
    ClubTopMenu,
    NotificationBell,
    BannerPromoScrolling,
  },
  methods: {
    handleCellClick(courtId, hour) {
      console.log("Celda clickeada:", courtId, hour);
      // Aquí puedes agregar la lógica para abrir un modal o formulario para agregar un evento.
    },
    getCellClass(courtId, hour) {
      if (this.reservations[courtId]?.[hour]) {
        return "occupied";
      }
      return "available";
    },
    generateHours(openingTime, closingTime) {
      // Convertir horas a intervalos de 30 minutos
      const hours = [];
      const [startHour, startMinutes] = openingTime.split(":").map(Number);
      const [endHour, endMinutes] = closingTime.split(":").map(Number);

      let currentTime = new Date();
      currentTime.setHours(startHour, startMinutes, 0, 0);

      const endTime = new Date();
      endTime.setHours(endHour, endMinutes, 0, 0);

      while (currentTime <= endTime) {
        hours.push(
          `${String(currentTime.getHours()).padStart(2, "0")}:${String(
            currentTime.getMinutes()
          ).padStart(2, "0")}`
        );
        currentTime.setMinutes(currentTime.getMinutes() + 30);
      }

      return hours;
    },
    async fetchReservations() {
      try {
        const { data, error } = await supabase
          .from("reservations")
          .select(`
              start_time,
              end_time,
              court_id,
              player_id,
              courts(name),
              profiles(full_name)
          `)
          .eq("reservation_date", this.selectedDate)
          .eq("courts.club_id", this.clubId);

        if (error) {
          console.error("Error fetching reservations:", error.message);
          return;
        }

        // Transformar los datos
        this.reservations = data.reduce((acc, reservation) => {
          const courtId = reservation.court_id;
          const startTime = reservation.start_time.slice(0, 5); // Reducir a formato HH:MM
          const endTime = reservation.end_time.slice(0, 5); // Reducir a formato HH:MM

          // Iterar sobre el rango de tiempo
          let currentTime = startTime;
          while (currentTime < endTime) {
            if (!acc[courtId]) acc[courtId] = {};
            acc[courtId][currentTime] = {
              playerName: reservation.profiles.full_name,
              courtName: reservation.courts.name,
            };

            // Incrementar por 30 minutos
            const [hours, minutes] = currentTime.split(":").map(Number);
            const newMinutes = minutes + 30;
            const newHours = hours + Math.floor(newMinutes / 60);
            currentTime = `${String(newHours).padStart(2, "0")}:${String(newMinutes % 60).padStart(2, "0")}`;
          }

          return acc;
        }, {});
      } catch (error) {
        console.error("Unexpected error:", error.message);
      }
    },
    async fetchScheduleHours() {
      try {
        if (!this.clubId) {
          console.error("No se encontró el ID del club.");
          return;
        }

        const { data, error } = await supabase
          .from("schedules")
          .select("opening_time, closing_time")
          .eq("club_id", this.clubId);

        if (error) {
          console.error("Error fetching schedule hours:", error.message);
          return;
        }

        if (!data || data.length === 0) {
          console.error("No se encontraron horarios para este club.");
          return;
        }

        // Encontrar el opening_time más temprano y el closing_time más tardío
        const earliestOpeningTime = data.reduce((earliest, schedule) =>
          schedule.opening_time < earliest ? schedule.opening_time : earliest,
          data[0].opening_time
        );

        const latestClosingTime = data.reduce((latest, schedule) =>
          schedule.closing_time > latest ? schedule.closing_time : latest,
          data[0].closing_time
        );

        // Generar las horas a partir del rango más amplio
        this.hours = this.generateHours(earliestOpeningTime, latestClosingTime);
      } catch (error) {
        console.error("Unexpected error:", error.message);
      }
    },
    async fetchCourts() {
      try {
        if (!this.clubId) {
          console.error("No se encontró el ID del club.");
          return;
        }

        const { data, error } = await supabase
          .from("courts")
          .select("id, name")
          .eq("club_id", this.clubId);

        if (error) {
          console.error("Error fetching courts:", error.message);
          return;
        }

        this.courts = data;
      } catch (error) {
        console.error("Unexpected error:", error.message);
      }
    },
    goBack() {
      this.$router.back();
    },
  },
  mounted() {
    // Obtener el clubId desde el token
    const token = localStorage.getItem("token");
    if (token) {
      const base64Url = token.split(".")[1];
      const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
      const payload = JSON.parse(atob(base64));
      this.clubId = payload.club_id || null;
    }

    // Llamar a las funciones de inicialización
    this.fetchCourts();
    this.fetchScheduleHours();
    this.fetchReservations();
  },
};
</script>

<style scoped>
/* Estilos generales */
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

.logo-icon {
  width: 60px; /* Ajusta el tamaño del logo */
  height: 60px;
}

.reservation-calendar {
  overflow-x: auto;
}

.reservation-table {
  width: 100%;
  border-collapse: collapse;
}

.reservation-table th,
.reservation-table td {
  border: 1px solid #444;
  padding: 8px;
  text-align: center;
}

.reservation-table th {
  background-color: #333;
  color: white;
}

/* Celdas disponibles (verde) */
.available {
  background-color: #81c784; /* Fondo verde */
  color: #000; /* Texto oscuro */
  cursor: pointer; /* Cambia el cursor al pasar sobre la celda */
  transition: background-color 0.2s;
}

.available:hover {
  background-color: #66bb6a; /* Verde más oscuro al hacer hover */
}

/* Celdas ocupadas (naranja) */
.occupied {
  background-color: #ffa726; /* Fondo naranja */
  color: #000; /* Texto oscuro */
  cursor: not-allowed; /* Cursor de no permitido */
}

/* Ajustes generales */
.reservation-table td {
  padding: 8px;
  border: 1px solid #ccc; /* Bordes claros */
}
</style>