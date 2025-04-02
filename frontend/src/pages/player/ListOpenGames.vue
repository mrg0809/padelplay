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
        <!-- Filter Buttons -->
        <div class="row q-col-gutter-md q-mb-lg">
          <div class="col-12 col-sm-4">
            <q-select
              v-model="selectedCity"
              :options="cityOptions"
              label="Ciudad"
              outlined dense options-dense clearable hide-selected
              input-debounce="300" @filter="filterCityFn" @clear="selectedCity = null"
              dark color="black" label-color="black"
              popup-content-class="bg-black text-black"
            >
              <template v-slot:prepend>
                <q-icon name="location_on" color="black"/>
              </template>
              <template v-slot:no-option>
                <q-item><q-item-section class="text-black">No hay ciudades</q-item-section></q-item>
              </template>
            </q-select>
          </div>

          <div class="col-12 col-sm-4">
            <q-select
              v-model="selectedDate"
              :options="dateOptions"
              label="Fecha"
              outlined dense options-dense clearable
              dark color="black" label-color="black"
              popup-content-class="bg-black text-black"
              @clear="selectedDate = null"
            >
              <template v-slot:prepend>
                <q-icon name="calendar_month" color="black"/>
              </template>
              <template v-slot:no-option>
                <q-item><q-item-section class="text-black">No hay opciones</q-item-section></q-item>
              </template>
            </q-select>
          </div>

          <div class="col-12 col-sm-4">
            <q-select
              v-model="selectedGender"
              :options="genderOptions"
              label="Género"
              outlined dense options-dense clearable
              dark color="black" label-color="black"
              popup-content-class="bg-black text-black"
              @clear="selectedGender = null"
            >
              <template v-slot:prepend>
                <q-icon name="wc" color="black"/>
              </template>
              <template v-slot:no-option>
                <q-item><q-item-section class="text-grey-8">No hay opciones</q-item-section></q-item>
              </template>
            </q-select>
          </div>
        </div>

        <!-- Games List -->
        <div class="games-list">
          <q-list v-if="games.length > 0" class="q-mt-md">
            <q-card
              v-for="game in games"
              :key="game.id"
              clickable
              class="match-card"
            >
            <q-card-section class="q-mt-md">
              <strong>{{ formatTimestamp(game.match_date) }} | {{ new Date(game.match_date + 'T' + game.match_time).toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' }) }}</strong><br>
              Categoría<q-icon name="o_sports_tennis"></q-icon> {{ game.category }}
              <div class="court-container">
                <div class="court">
                  <!-- Jugadores o botones de agregar -->
                  <div class="player team1-player1">
                    <div v-if="game.team1_players[0]">
                      <q-avatar size="40px" v-if="game.team1_players[0].photo_url">
                        <img :src="game.team1_players[0].photo_url" alt="Foto del jugador" />
                      </q-avatar>
                      <span v-else> {{ game.team1_players[0].first_name || "Jugador 1 Equipo 1" }}</span>
                      <div class="text-caption">
                        {{ game.team1_players[0].category }}
                      </div>
                    </div>
                  </div>
                  <div class="player team1-player2">
                    <div v-if="game.team1_players[1]">
                      <q-avatar size="40px" v-if="game.team1_players[1].photo_url">
                        <img :src="game.team1_players[1].photo_url" alt="Foto del jugador" />
                      </q-avatar>
                      <span v-else> {{ game.team1_players[1].first_name || "Jugador 1 Equipo 1" }}</span>
                      <div class="text-caption">
                        {{ game.team1_players[1].category }}
                      </div>
                    </div>
                    <q-btn
                      v-else
                      flat
                      round
                      icon="o_person_add"
                      @click.stop="prepareJoinGameSummary(game, 1, 1)"
                      title="Unirse a este espacio"
                    />
                  </div>
                  <div class="player team2-player1">
                    <div v-if="game.team2_players[0]">
                      <q-avatar size="40px" v-if="game.team2_players[0].photo_url">
                        <img :src="game.team2_players[0].photo_url" alt="Foto del jugador" />
                      </q-avatar>
                      <span v-else> {{ game.team2_players[0].first_name || "Jugador 1 Equipo 2" }}</span>
                      <div class="text-caption">
                        {{ game.team2_players[0].category }}
                      </div>
                    </div>
                    <q-btn
                      v-else
                      flat
                      round
                      icon="o_person_add"
                      @click.stop="prepareJoinGameSummary(game, 2, 0)"
                      title="Unirse a este espacio"
                    />
                  </div>
                  <div class="player team2-player2">
                    <div v-if="game.team2_players[1]">
                      <q-avatar size="40px" v-if="game.team2_players[1].photo_url">
                        <img :src="game.team2_players[1].photo_url" alt="Foto del jugador" />
                      </q-avatar>
                      <span v-else> {{ game.team2_players[1].first_name || "Jugador 2 Equipo 2" }}</span>
                      <div class="text-caption">
                        {{ game.team2_players[1].category }}
                      </div>
                    </div>
                    <q-btn
                      v-else
                      flat
                      round
                      icon="o_person_add"
                      @click.stop="prepareJoinGameSummary(game, 2, 1)"
                      title="Unirse a este espacio"
                    />
                  </div>
                  
                  <div class="line1"></div>
                  <div class="net"></div>
                  <div class="line2"></div>
                  <div class="horizontal-line"></div>
                  
                </div>
              </div>
              
            </q-card-section>
            <q-card-section class="club-info-section">
              <div class="club-info">
                <img 
                  :src="game.club.logo_url || '/src/assets/logo.jpeg'" 
                  alt="Club Logo" 
                  class="club-logo" 
                />
                <span class="club-name">{{ game.club.name }}</span>
              </div>
              <div class="vertical-divider"></div>
              <div class="price-duration">
                <span class="total-price">${{ game.reservation.total_price / 4 }} MXN</span><br>
                <span class="duration">{{ calculateDuration(game.reservation.start_time, game.reservation.end_time) }} minutos</span>
              </div>
            </q-card-section>
            
            </q-card>
          </q-list>
          <div v-else-if="searching" class="text-center">Buscando...<br>
            <q-spinner-dots color="black" size="xl" />
          </div>
          <div v-else class="text-center text-black">
            <p>No se encontraron juegos.</p>


          </div>
        </div>
      </q-page>
    </q-page-container>
    <PlayerNavigationMenu />
  </q-layout>
</template>

<script setup> // Usar script setup
  import { ref, onMounted, watch } from "vue";
  import { useRouter } from "vue-router";
  import { supabase } from "../../services/supabase"; // Asegúrate que la ruta sea correcta
  import { fetchCities } from "src/services/supabase/commun"; // Asegúrate que la ruta sea correcta
  import { useSummaryStore } from 'src/stores/summaryStore'; 
  import { useQuasar } from 'quasar'; 

  import PlayerNavigationMenu from "src/components/PlayerNavigationMenu.vue";
  import NotificationBell from "src/components/NotificationBell.vue";
  import BannerPromoScrolling from "src/components/BannerPromoScrolling.vue";

  // --- Inicialización ---
  const router = useRouter();
  const summaryStore = useSummaryStore(); // Inicializar store
  const $q = useQuasar(); // Para notificaciones

  // --- Estado de Filtros ---
  const allCityOptions = ref([]);
  const cityOptions = ref([]); // Para el select con filtro
  const dateOptions = ref(['Hoy', 'Mañana', 'Esta Semana', 'Próximos 7 días']); // Opciones simplificadas
  const genderOptions = ref(["femenil", "varonil", "mixto"]); // Valores directos

  const selectedCity = ref(null); 
  const selectedDate = ref(null); 
  const selectedGender = ref(null); 

  const games = ref([]);
  const searching = ref(false); 

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleDateString('es-MX', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    });
  };

  const calculateDuration = (startTime, endTime) => {
    const [startHour, startMinute] = startTime.split(':').map(Number);
    const [endHour, endMinute] = endTime.split(':').map(Number);

    let durationMinutes = (endHour * 60 + endMinute) - (startHour * 60 + startMinute);

    // Si la duración es negativa, significa que el partido terminó después de la medianoche
    if (durationMinutes < 0) {
      durationMinutes += 24 * 60; // Agregar 24 horas (en minutos)
    }

    return durationMinutes;
  };

  const loadCities = async () => {
    try {
        const cities = await fetchCities();
        allCityOptions.value = cities.map(city => typeof city === 'string' ? city : city.value || city.label || city);
        cityOptions.value = allCityOptions.value;
    } catch (error) { /* ... manejo error ... */ }
  };

  const filterCityFn = (val, update) => {
    if (val === '') {
        update(() => { cityOptions.value = allCityOptions.value; });
        return;
    }
    update(() => {
        const needle = val.toLowerCase();
        cityOptions.value = allCityOptions.value.filter(v => v.toLowerCase().indexOf(needle) > -1);
    });
  };


  // Fetch matches from Supabase with filters
  const fetchMatches = async () => {
    searching.value = true;
    games.value = []; // Limpiar antes de buscar
    try {
        let query = supabase
            .from("matches")
            .select(`
                id, match_date, match_time, category, gender, is_open, team1_players, team2_players,
                club:clubs!inner ( id, name, city, logo_url ),
                reservation:reservations ( total_price, start_time, end_time )
            `)
            .eq("is_open", true); // Solo juegos abiertos

        // --- Aplicar Filtro de Fecha ---
        const dateFilter = selectedDate.value;
        const today = new Date(); today.setHours(0, 0, 0, 0);
        const tomorrow = new Date(today); tomorrow.setDate(today.getDate() + 1);
        const dayAfterTomorrow = new Date(today); dayAfterTomorrow.setDate(today.getDate() + 2);
        const endOfWeek = new Date(today); endOfWeek.setDate(today.getDate() + (7 - today.getDay())); endOfWeek.setHours(23, 59, 59, 999);
        const endOfNext7Days = new Date(today); endOfNext7Days.setDate(today.getDate() + 7); endOfNext7Days.setHours(23, 59, 59, 999);

        const todayStr = today.toISOString().split('T')[0];
        const tomorrowStr = tomorrow.toISOString().split('T')[0];
        const dayAfterTomorrowStr = dayAfterTomorrow.toISOString().split('T')[0];
        const endOfWeekStr = endOfWeek.toISOString().split('T')[0];
        const endOfNext7DaysStr = endOfNext7Days.toISOString().split('T')[0];


        if (dateFilter === 'Hoy') {
            query = query.gte('match_date', todayStr).lt('match_date', tomorrowStr);
        } else if (dateFilter === 'Mañana') {
            query = query.gte('match_date', tomorrowStr).lt('match_date', dayAfterTomorrowStr);
        } else if (dateFilter === 'Esta Semana') {
            query = query.gte('match_date', todayStr).lte('match_date', endOfWeekStr);
        } else if (dateFilter === 'Próximos 7 días') {
            query = query.gte('match_date', todayStr).lte('match_date', endOfNext7DaysStr);
        } else {
             // Por defecto, mostrar solo desde hoy en adelante si no hay filtro de fecha
             query = query.gte('match_date', todayStr);
        }
        // --- Fin Filtro Fecha ---

        // --- Otros Filtros ---
        if (selectedCity.value) {
             query = query.eq("club.city", selectedCity.value); 
        }
        if (selectedGender.value) {
            query = query.eq("gender", selectedGender.value);
        }

        const { data: matchesData, error } = await query.order('match_date').order('match_time');

        if (error) throw error;
        if (!matchesData) { games.value = []; return; }

         const playerIds = matchesData.flatMap(match => [...(match.team1_players || []), ...(match.team2_players || [])]).filter(id => id != null);
         let playerMap = {};
         if (playerIds.length > 0) {
            const { data: players, error: playersError } = await supabase
               .from("players")
               .select("user_id, first_name, photo_url, category")
               .in("user_id", [...new Set(playerIds)]);
            if (playersError) throw playersError;
            playerMap = (players || []).reduce((map, player) => { map[player.user_id] = player; return map; }, {});
         }

        // --- Mapear Resultados ---
        games.value = matchesData.map(match => ({
            ...match,
            club: match.club || { name: 'N/A', city: 'N/A', id: null }, // Default object for club
            reservation: match.reservation || { total_price: 0, start_time: '00:00', end_time: '00:00' }, // Default for reservation
            // Mapear jugadores, devolver null si el ID no está o no se encontró
            team1_players: (match.team1_players || [null, null]).map(playerId => playerMap[playerId] || null),
            team2_players: (match.team2_players || [null, null]).map(playerId => playerMap[playerId] || null),
        }));

    } catch (error) {
        console.error("Error fetching matches:", error);
        games.value = []; // Limpiar en caso de error
        $q.notify({ type: 'negative', message: 'Error al buscar juegos.' });
    } finally {
        searching.value = false;
    }
  };

  const prepareJoinGameSummary = (game, teamNum, playerIndex) => {
    console.log(`Intentando unirse a juego ${game.id}, equipo ${teamNum}, slot ${playerIndex}`);

    // Validaciones
    if (!game || !game.reservation || game.reservation.total_price === undefined || game.reservation.total_price === null || !game.club?.id) {
        console.error("Datos incompletos del juego para proceder al pago:", game);
        $q.notify({ type: 'negative', message: 'Información del juego incompleta para unirse.' });
        return;
    }

    const pricePerPlayer = (game.reservation.total_price || 0) / 4;
    if (pricePerPlayer <= 0) {
        // Podría ser un juego gratuito o un error en el precio total
        // Decide cómo manejar juegos gratuitos (¿quizás unirse directamente sin pago?)
        console.warn("El precio por jugador es cero o inválido.");
         // $q.notify({ type: 'info', message: 'Este juego parece ser gratuito o tiene un error en el precio.' });
         // Por ahora, continuamos asumiendo que un precio > 0 es necesario
         // Si permites juegos gratuitos, necesitarías otra lógica aquí.
         // return; // Descomenta si no permites precio cero
    }


    // 1. Construir Props
    const summaryProps = {
        summaryTitle: 'Confirmar Unión a Juego',
        itemDetails: [
            { label: 'Club', value: game.club.name || 'No especificado' },
            { label: 'Fecha', value: formatTimestamp(game.match_date) }, // Usar función existente
            { label: 'Hora', value: `${new Date(game.match_date + 'T' + game.match_time).toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' })} hrs.` },
            { label: 'Categoría', value: game.category || 'N/A' },
            { label: 'Precio (Tu parte)', value: `$${pricePerPlayer.toFixed(2)}` },
        ],
        baseData: {
            clubId: game.club.id,
            price: pricePerPlayer,
            participants: 1, // Al unirse, paga 1 persona
            type: 'open_match_join', // Nuevo tipo
            id: game.id, // ID del Match
        },
        allowPaymentSplit: false, // Ya está dividido, se paga la parte individual
        showPublicToggle: false, // No aplica
        commissionRate: 4, // O desde config
        extraData: { // Información adicional útil
            matchId: game.id,
            teamToJoin: teamNum,
            slotIndex: playerIndex, // Puede ser útil post-pago para actualizar el match
            matchCategory: game.category,
            matchGender: game.gender,
            matchDate: game.match_date,
            matchTime: game.match_time,
            clubName: game.club.name,
        }
    };

    summaryStore.setSummaryDetails(summaryProps);
    console.log('Datos para unirse a juego guardados en Pinia:', summaryProps);
    router.push({ name: 'OrderSummary' });
  };

    watch([selectedCity, selectedDate, selectedGender], fetchMatches, { deep: true }); 

    onMounted(() => {
      loadCities();
      fetchMatches();
    });

</script>

  
<style scooped>

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

  .games-list .game-card {
      padding: 16px;
      border-radius: 8px;
      background-image: url("../../assets/texturafondo.png");
      background-size: cover;
      margin-bottom: 16px;
    }
    
    .club-info-section {
      display: flex;
      align-items: center; 
    }

    .club-info {
      display: flex;
      align-items: center; 
    }

    .club-logo {
      width: 30px;
      height: 30px;
      border-radius: 50%;
      object-fit: cover;
      margin-right: 18px; 
    }

    .vertical-divider {
      border-left: 1px solid #ccc; 
      height: 40px; 
      margin: 0 20px; 
    }

    .price-duration {
      margin-left: 15px;
      text-align: left; 
    }
    
    .club-name {
      font-size: 1.2em;
      font-weight: bold;
    }

    .filter-options {
    display: flex;
    gap: 10px;
    justify-content: center;
  }

  .filter-options q-select {
    height: 10px;
    width: 40%;
  }

  .filter-options q-select ::v-deep .q-field__label,
  .filter-options q-select ::v-deep .q-item__label {
    font-size: 0.5em; 
  }

  .court-container {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
  }

  .court {
    position: relative;
    background-color: #1976d2;
    border-radius: 10px;
    color: white;
    width: 100%;
    max-width: 400px; 
    aspect-ratio: 2 / 1;
    padding: 0;
  }

  .match-card {
    background-image: url("../../assets/texturafondo.png");
    background-size: cover;
    margin-bottom: 10px;
    border-radius: 7%;
    padding: 0px;
  }

  .match-card h3 {
    margin-top: 0px;
    margin-bottom: 15px;
    font-size: x-large;
    font-weight: bold;
  }

  .player {
    position: absolute;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    transform: translate(-50%, -50%);
  }

  .team1-player1 {
    top: 25%;
    left: 33%;
  }

  .team1-player2 {
    top: 75%;
    left: 33%;
  }

  .team2-player1 {
    top: 25%;
    left: 67%;
  }

  .team2-player2 {
    top: 75%;
    left: 67%;
  }

  .net {
    position: absolute;
    top: 0;
    bottom: 0;
    left: 50%;
    width: 1.5px;
    background-color: rgb(194, 194, 194);
    opacity: 0.6;
    transform: translateX(-50%);
    box-shadow: 1px 15px 4px #d1d0d0;
  }

  .line1 {
    position: absolute;
    top: 0;
    bottom: 0;
    left: 15%;
    width: 1.5px;
    background-color: white;
    opacity: 0.9;
    transform: translateX(-50%);
  }

  .line2 {
    position: absolute;
    top: 0;
    bottom: 0;
    left: 85%;
    width: 1.5px;
    background-color: white;
    opacity: 0.9;
    transform: translateX(-50%);
  }

  .horizontal-line {
    position: absolute;
    top: 50%;
    left: 15%;
    width: 70%;
    height: 1.5px; 
    background-color: white;
    opacity: 0.7;
    transform: translateY(-50%);
  }
</style>
  