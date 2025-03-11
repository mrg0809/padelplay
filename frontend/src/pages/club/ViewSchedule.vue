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
              color="white"
              bg-color="grey"
              @change="fetchAndTransformReservations"
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
                        <template v-if="reservations[court.id][hour].type === 'reservation'">
                            <strong>{{ reservations[court.id][hour].playerName }}</strong>
                            <q-icon
                                v-if="reservations[court.id][hour].isPaid"
                                name="o_paid"
                                color="green"
                                size="sm"
                                class="q-ml-sm"
                            />
                            <q-icon
                                v-else
                                name="money_off"
                                color="red"
                                size="sm"
                                class="q-ml-sm"
                            />
                        </template>
                        <template v-else-if="reservations[court.id][hour].type === 'block'">
                            <q-tooltip>{{ reservations[court.id][hour].reason }}</q-tooltip>
                            <q-icon name="block" color="red" size="xs" />
                        </template>
                    </div>
                    <div v-else>
                        <q-icon name="add" color="black" size="xs" />
                    </div>
                </td>
                </tr>
              </tbody>
            </table>
          </div>
        </q-page>
      </q-page-container>
          <!-- Diálogo para agregar o ver detalles de un evento -->
          <q-dialog v-model="dialogVisible">
            <q-card class="bg-black">
                <q-card-section>
                <div v-if="isCellAvailable">
                    <h6>Agregar Reserva</h6>
                    
                    <!-- Selección de jugador -->
                    <q-select
                    v-model="selectedPlayer"
                    use-input
                    fill-input
                    input-debounce="300"
                    label="Buscar jugador"
                    :options="playerOptions"
                    option-label="full_name"
                    option-value="user_id"
                    @filter="searchPlayers"
                    />
                    
                    <!-- Fecha seleccionada (deshabilitada, solo informativa) -->
                    <q-input v-model="selectedDate" label="Fecha" disable />

                    <!-- Hora de inicio (deshabilitada, solo informativa) -->
                    <q-input v-model="selectedHour" label="Hora de inicio" disable />

                    <!-- Selección de duración -->
                    <q-select
                    v-model="selectedDuration"
                    :options="durationOptions"
                    label="Duración"
                    @update:model-value="updatePrice"
                    />

                    <!-- Precio calculado automáticamente -->
                    <q-input v-model="selectedPrice" label="Precio" disable />

                </div>

                <div v-else>
                    <h6>Detalles de la Reserva</h6>
                    <p><strong>Jugador:</strong> {{ selectedEvent.playerName }}</p>
                    <p><strong>Estado de pago:</strong> {{ selectedEvent.isPaid ? 'Pagado' : 'Pendiente' }}</p>
                </div>
                </q-card-section>

                <q-card-actions align="right">
                <q-btn
                    v-if="isCellAvailable"
                    label="Guardar"
                    color="green"
                    @click="saveEvent"
                />
                <q-btn
                    label="Cerrar"
                    color="negative"
                    @click="dialogVisible = false"
                />
                </q-card-actions>
            </q-card>
            </q-dialog>
      <!-- Menú de Navegación Inferior -->
      <ClubNavigationMenu />
    </q-layout>
  </template>
  
  <script setup>
  import { ref, onMounted, watchEffect } from 'vue';
  import { useRouter } from 'vue-router';
  import { createReservation } from 'src/services/api/reservations';
  import { fetchCourtBlocks } from 'src/services/supabase/blocks';
  import { fetchReservations } from 'src/services/supabase/reservations';
  import { fetchScheduleHours } from 'src/services/supabase/clubs';
  import { fetchCourts, fetchCourtPrices } from 'src/services/supabase/courts';
  import { generateHours } from 'src/helpers/hourUtils';
  import { searchPlayersByName } from 'src/services/supabase/commun';
  import { useUserStore } from 'src/stores/userStore';
  import BannerPromoScrolling from "src/components/BannerPromoScrolling.vue";
  import ClubNavigationMenu from "src/components/ClubNavigationMenu.vue";
  import ClubTopMenu from "src/components/ClubTopMenu.vue";
  import NotificationBell from "src/components/NotificationBell.vue";
  
  const selectedDate = ref(new Date().toISOString().split("T")[0]);
  const courts = ref([]);
  const hours = ref([]);
  const courtBlocks = ref([]);
  const reservations = ref({});
  const router = useRouter();
  const userStore = useUserStore();
  const clubId = userStore.clubId;
  const dialogVisible = ref(false);
  const isCellAvailable = ref(false);
  const selectedEvent = ref(null);
  const newEvent = ref({
    playerName: '',
    isPaid: false,
    eventType: 'Reserva',
  });
  const selectedPlayer = ref(null);
  const playerOptions = ref([]);
  const selectedCourtId = ref(null);
  const selectedDuration = ref(null);
  const selectedPrice = ref("");
  const selectedHour = ref(""); // Se asignará cuando el usuario haga clic en una celda
  const durationOptions = ref([
    { label: "60 min", value: 60 },
    { label: "90 min", value: 90 },
    { label: "120 min", value: 120 },
    ]);

const searchPlayers = async (val, update) => {
    if (!val) return update(() => (playerOptions.value = []));
    try {
        const players = await searchPlayersByName(val);
        playerOptions.value = players.map(player => ({
        ...player,
        full_name: `${player.first_name} ${player.last_name}`,
        }));
        update(() => (playerOptions.value = playerOptions.value));
    } catch (error) {
        console.error("Error buscando jugadores:", error);
    }
    };

    const updatePrice = async () => {
    console.log("selectedDuration.value:", selectedDuration.value);
    console.log("selectedCourtId.value:", selectedCourtId.value);

    if (!selectedDuration.value || !selectedCourtId.value) {
        selectedPrice.value = "No disponible";
        return;
    }
    try {
        const courtPrices = await fetchCourtPrices(selectedCourtId.value);
        console.log("courtPrices:", courtPrices);

        if (!courtPrices || courtPrices.length === 0) {
            selectedPrice.value = "No disponible";
            return;
        }
        const court = courtPrices[0];
        let price = "No disponible";

        if (selectedDuration.value.value === 60) { // Accedemos a .value
            price = court.price_per_hour;
            console.log("Duración 60, precio:", price);
        } else if (selectedDuration.value.value === 90) { // Accedemos a .value
            price = court.price_per_hour_and_half;
            console.log("Duración 90, precio:", price);
        } else if (selectedDuration.value.value === 120) { // Accedemos a .value
            price = court.price_per_two_hour;
            console.log("Duración 120, precio:", price);
        }

        if (price === null || price === undefined) {
            selectedPrice.value = "No disponible";
            console.log("Precio es null o undefined");
        } else {
            selectedPrice.value = price.toString();
            console.log("Precio asignado:", selectedPrice.value);
        }
    } catch (error) {
        console.error("Error obteniendo precios:", error);
        selectedPrice.value = "No disponible";
    }
};
  
  const handleCellClick = (courtId, hour) => {
    if (reservations.value[courtId]?.[hour]) {
      // Si la celda está ocupada, mostrar detalles del evento
      selectedEvent.value = reservations.value[courtId][hour];
      isCellAvailable.value = false;
    } else {
      // Si la celda está disponible, preparar para agregar un evento
      selectedCourtId.value = courtId;
      selectedHour.value = hour;
      isCellAvailable.value = true;
    }
    dialogVisible.value = true; // Abrir el diálogo
  };
  
  const saveEvent = async () => {
    if (!selectedPlayer.value || !selectedCourtId.value || !selectedHour.value || !selectedDuration.value || !selectedPrice.value) {
        console.error("Faltan datos para crear la reserva.");
        return;
    }

    const startTime = selectedHour.value;
    const durationMinutes = selectedDuration.value.value;
    const [startHours, startMinutes] = startTime.split(":").map(Number);
    let endTimeMinutes = startMinutes + durationMinutes;
    let endTimeHours = startHours + Math.floor(endTimeMinutes / 60);
    endTimeMinutes = endTimeMinutes % 60;

    // Construimos end_time usando concatenación de cadenas
    const endTime = String(endTimeHours).padStart(2, "0") + ":" + String(endTimeMinutes).padStart(2, "0");

    const reservationData = {
        club_id: clubId,
        court_id: selectedCourtId.value,
        reservation_date: selectedDate.value,
        start_time: startTime,
        end_time: endTime, // Usamos la cadena construida correctamente
        total_price: selectedPrice.value,
        player_id: selectedPlayer.value.user_id,
    };

        try {
            const response = await createReservation(reservationData);
            console.log("Reserva creada:", response);
            dialogVisible.value = false;
            fetchAndTransformReservations();
        } catch (error) {
            console.error("Error al crear la reserva:", error);
            // Manejar el error, por ejemplo, mostrar un mensaje al usuario
        }
    };
    
    const getCellClass = (courtId, hour) => {
        if (reservations.value[courtId]?.[hour]) {
            if (reservations.value[courtId][hour].type === 'block') {
                return "blocked";
            } else if (reservations.value[courtId][hour].type === 'reservation') {
                return "occupied";
            }
        }
        return "available";
    };

  
    const fetchAndTransformReservations = async () => {
        try {
            const reservationData = await fetchReservations(selectedDate.value, clubId);
            const blockData = await fetchCourtBlocks(selectedDate.value, clubId);

            // Procesar reservas
            const processedReservations = reservationData.reduce((acc, reservation) => {
                const courtId = reservation.court_id;
                const startTime = reservation.start_time.slice(0, 5);
                const endTime = reservation.end_time.slice(0, 5);

                let currentTime = startTime;
                while (currentTime < endTime) {
                    if (!acc[courtId]) acc[courtId] = {};
                    acc[courtId][currentTime] = {
                        type: 'reservation',
                        playerName: reservation.profiles.full_name,
                        courtName: reservation.courts.name,
                        isPaid: reservation.is_paid,
                        id: reservation.id,
                    };

                    const [hours, minutes] = currentTime.split(":").map(Number);
                    let newMinutes = minutes + 30;
                    let newHours = hours + Math.floor(newMinutes / 60);
                    newMinutes = newMinutes % 60;
                    currentTime = `${String(newHours).padStart(2, "0")}:${String(newMinutes).padStart(2, "0")}`;

                    // Detener el bucle si currentTime >= endTime
                    if (currentTime > endTime) break;
                }
                return acc;
            }, {});

        // Procesar bloqueos (con cambios)
            const processedBlocks = blockData.reduce((acc, block) => {
                const courtId = block.court_id;
                const startTime = block.start_time.slice(0, 5);
                const endTime = block.end_time.slice(0, 5);

                let currentTime = startTime;
                while (currentTime < endTime) {
                    if (!acc[courtId]) acc[courtId] = {};
                    acc[courtId][currentTime] = {
                        type: 'block',
                        isBlock: true,
                        reason: block.reason,
                    };

                    const [hours, minutes] = currentTime.split(":").map(Number);
                    let newMinutes = minutes + 30;
                    let newHours = hours + Math.floor(newMinutes / 60);
                    newMinutes = newMinutes % 60;
                    currentTime = `${String(newHours).padStart(2, "0")}:${String(newMinutes).padStart(2, "0")}`;

                    // Detener el bucle si currentTime >= endTime
                    if (currentTime > endTime) break;
                }
                return acc;
            }, {});

            // Combinar reservas y bloqueos (sin cambios)
            reservations.value = {};
            reservations.value = Object.assign({}, processedReservations, processedBlocks);

        } catch (error) {
            console.error("Unexpected error:", error.message);
        }
    };
  
  const fetchAndSetScheduleHours = async () => {
    try {
      const data = await fetchScheduleHours(clubId);
      const earliestOpeningTime = data.reduce((earliest, schedule) =>
        schedule.opening_time < earliest ? schedule.opening_time : earliest,
        data[0].opening_time
      );
  
      const latestClosingTime = data.reduce((latest, schedule) =>
        schedule.closing_time > latest ? schedule.closing_time : latest,
        data[0].closing_time
      );
  
      hours.value = generateHours(earliestOpeningTime, latestClosingTime);
    } catch (error) {
      console.error("Unexpected error:", error.message);
    }
  };
  
  const fetchAndSetCourts = async () => {
    try {
      const data = await fetchCourts(clubId);
      courts.value = data;
    } catch (error) {
      console.error("Unexpected error:", error.message);
    }
  };
  
  // Reaccionar a cambios en selectedDate.value
  watchEffect(() => {
    fetchAndTransformReservations();
     }
  );
  
  // Inicialización en mounted
  onMounted(() => {
    fetchAndSetCourts();
    fetchAndSetScheduleHours();
    fetchAndTransformReservations();
  });
  </script>
  
  <style scoped>
  /* Estilos generales */
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
  
  .reservation-calendar {
    overflow-x: auto;
    max-height: 80vh;
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
    position: sticky;
    top: 0;
    z-index: 2;
  }
  
  .reservation-table th:first-child,
  .reservation-table td:first-child {
    background-color: #444;
    color: white;
    position: sticky;
    left: 0; /* Fija la primera columna a la izquierda */
    z-index: 1; /* Asegura que la columna esté por encima de las celdas */
  }
  
  .available {
    background-color: #81c784; 
    color: #000; 
    cursor: pointer; 
    transition: background-color 0.2s;
  }
  
  .available:hover {
    background-color: #66bb6a; 
  }
  
  
  .occupied {
    background-color: #ffa726; /* Fondo naranja */
    color: #000; /* Texto oscuro */
    cursor: not-allowed; /* Cursor de no permitido */
  }

  .blocked {
    background-color: #f44336; /* Fondo rojo */
    color: #fff; /* Texto blanco */
    cursor: not-allowed;
}
  
  
  .reservation-table td {
    padding: 8px;
    border: 1px solid #ccc; 
  }
  </style>