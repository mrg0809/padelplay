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
        <div class="filter-options">
          <!-- Button Dropdown for City -->
          <q-btn
            dense
            color="black"
            filled
            rounded
            icon="location_on"
            label="Ciudad"
            @click="cityMenu = true"
          />
          <q-menu v-model="cityMenu" anchor="bottom left" self="top left">
            <q-list>
              <q-item
                v-for="city in cityOptions"
                :key="city.value"
                clickable
                @click="selectCity(city)"
              >
                <q-item-section>{{ city.label }}</q-item-section>
              </q-item>
            </q-list>
          </q-menu>

          <!-- Button Dropdown for Dates -->
          <q-btn
            dense
            color="black"
            filled
            rounded
            icon="calendar_month"
            label="Fechas"
            @click="dateMenu = true"
          />
          <q-menu v-model="dateMenu" anchor="bottom left" self="top left">
            <q-list>
              <q-item
                v-for="date in dateOptions"
                :key="date.value"
                clickable
                @click="selectDate(date)"
              >
                <q-item-section>{{ date.label }}</q-item-section>
              </q-item>
            </q-list>
          </q-menu>

          <!-- Button Dropdown for Gender -->
          <q-btn
            dense
            color="black"
            filled
            rounded
            icon="wc"
            label="Tipo"
            @click="genderMenu = true"
          />
          <q-menu v-model="genderMenu" anchor="bottom left" self="top left">
            <q-list>
              <q-item
                v-for="gender in genderOptions"
                :key="gender.value"
                clickable
                @click="selectGender(gender)"
              >
                <q-item-section>{{ gender.label }}</q-item-section>
              </q-item>
            </q-list>
          </q-menu>
        </div>

        <!-- Games List -->
        <div class="games-list">
          <q-list v-if="games.length > 0" class="q-mt-md">
            <q-card
              v-for="game in games"
              :key="game.id"
              clickable
              @click="navigateToMatch(game.id)"
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
                    <q-btn
                      v-else
                      flat
                      round
                      icon="o_person_add"
                      @click="openAddPlayerDialog(1, 0)"
                    />
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
                      @click="openAddPlayerDialog(1, 1)"
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
                      @click="openAddPlayerDialog(2, 0)"
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
                      @click="openAddPlayerDialog(2, 1)"
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

<script>
import { ref, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import { supabase } from "../../services/supabase";
import { fetchCities } from "src/services/supabase/commun";
import PlayerNavigationMenu from "src/components/PlayerNavigationMenu.vue";
import NotificationBell from "src/components/NotificationBell.vue";
import BannerPromoScrolling from "src/components/BannerPromoScrolling.vue";

export default {
  components: {
    PlayerNavigationMenu,
    BannerPromoScrolling,
    NotificationBell,
  },
  setup() {
    const cityOptions = ref([]);
    const dateOptions = ref([
      { label: "Hoy", value: "today" },
      { label: "Mañana", value: "tomorrow" },
      { label: "Esta semana", value: "this_week" },
    ]);
    const genderOptions = ref([
      { label: "Femenil", value: "femenil" },
      { label: "Varonil", value: "varonil" },
      { label: "Mixto", value: "mixto" },
    ]);

    const router = useRouter();

    const selectedCity = ref(null);
    const selectedDates = ref([]);
    const selectedGender = ref(null);

    const cityMenu = ref(false);
    const dateMenu = ref(false);
    const genderMenu = ref(false);

    const games = ref([]);
    const searching = ref(false);

    // Format the timestamp to a readable date string
    const formatTimestamp = (timestamp) => {
      return new Date(timestamp).toLocaleDateString('es-MX', {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
      });
    };

    // Calculate the duration of the match in minutes
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

    // Fetch matches from Supabase with filters
    const fetchMatches = async () => {
      searching.value = true;
      try {
        // 1. Obtener los partidos con la información del club
        let { data: matches, error } = await supabase
          .from("matches")
          .select(`
            *,
            club:clubs (
              name,
              city,
              logo_url,
              geolocation
            ),
            reservation:reservations(total_price, start_time, end_time)
          `)
          .eq("is_open", true)
          .gt("match_date", new Date().toISOString());

        if (selectedCity.value) {
          query = query.eq("club.city", selectedCity.value); // Filtrar por ciudad del club
        }
        if (selectedGender.value) {
          query = query.eq("gender", selectedGender.value);
        }
        if (selectedDates.value.length > 0) {
          // Filtrado por fechas 
          if (selectedDates.value.includes("today")) {
            const today = new Date();
            const startOfDay = new Date(
              today.getFullYear(),
              today.getMonth(),
              today.getDate()
            ).toISOString();
            const endOfDay = new Date(
              today.getFullYear(),
              today.getMonth(),
              today.getDate() + 1
            ).toISOString();
            query = query.or(`match_date.gte.${startOfDay},match_date.lt.${endOfDay}`);
          }
          if (selectedDates.value.includes("tomorrow")) {
            const today = new Date();
            const startOfTomorrow = new Date(
              today.getFullYear(),
              today.getMonth(),
              today.getDate() + 1
            ).toISOString();
            const endOfTomorrow = new Date(
              today.getFullYear(),
              today.getMonth(),
              today.getDate() + 2
            ).toISOString();
            query = query.or(`match_date.gte.${startOfTomorrow},match_date.lt.${endOfTomorrow}`);
          }
        }

        if (error) {
          console.error("Error fetching matches:", error.message);
          games.value = [];
          return;
        }

        // 2. Obtener los IDs de todos los jugadores
        const playerIds = matches.flatMap(match => [
          ...match.team1_players, 
          ...match.team2_players
        ]);

        // 3. Obtener la información de los jugadores
        let { data: players, error: playersError } = await supabase
          .from("players")
          .select("user_id, first_name, photo_url, category")
          .in("user_id", playerIds);

        if (playersError) {
          console.error("Error fetching players:", playersError.message);
          games.value = [];
          return;
        }

        // 4. Crear un mapa de jugadores por user_id
        const playerMap = players.reduce((map, player) => {
          map[player.user_id] = player;
          return map;
        }, {});

        // 5. Agregar la información de los jugadores a los partidos
        games.value = matches.map(match => ({
          ...match,
          team1_players: match.team1_players.map(playerId => playerMap[playerId]),
          team2_players: match.team2_players.map(playerId => playerMap[playerId]),
        }));

      } catch (error) {
        console.error("Unexpected error fetching matches:", error.message);
        games.value = [];
      } finally {
        searching.value = false;
      }
    };

    const navigateToMatch = (matchId) => {
      router.push(`/player/match/${matchId}`);
    };

    const selectCity = (city) => {
      selectedCity.value = city.value;
      cityMenu.value = false;
    };

    const selectDate = (date) => {
      if (!selectedDates.value.includes(date.value)) {
        selectedDates.value.push(date.value);
      } else {
        selectedDates.value = selectedDates.value.filter((d) => d !== date.value);
      }
      dateMenu.value = false;
    };

    const selectGender = (gender) => {
      selectedGender.value = gender.value;
      genderMenu.value = false;
    };

    // Watch for changes in filters and refetch matches
    watch([selectedCity, selectedDates, selectedGender], fetchMatches);

    onMounted(() => {
      fetchCities();
      fetchMatches();
    });

    return {
      cityOptions,
      dateOptions,
      genderOptions,
      selectedCity,
      selectedDates,
      selectedGender,
      cityMenu,
      dateMenu,
      genderMenu,
      games,
      navigateToMatch,
      searching,
      selectCity,
      selectDate,
      selectGender,
      formatTimestamp,
      calculateDuration,
    };
  },
};
</script>

  
<style>

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

  .games-list .game-card {
      padding: 16px;
      border-radius: 8px;
      background-image: url("../../assets/texturafondo.png");
      background-size: cover;
      margin-bottom: 16px;
    }
    
    .club-info-section {
      display: flex;
      align-items: center; /* Centra verticalmente */
    }

    .club-info {
      display: flex;
      align-items: center; /* Centra verticalmente el logo y el nombre */
    }

    .club-logo {
      width: 30px;
      height: 30px;
      border-radius: 50%;
      object-fit: cover;
      margin-right: 18px; /* Espacio entre el logo y el nombre */
    }

    .vertical-divider {
      border-left: 1px solid #ccc; /* Estilo de la línea divisora */
      height: 40px; /* Altura de la línea */
      margin: 0 20px; /* Espacio a los lados de la línea */
    }

    .price-duration {
      margin-left: 15px;
      text-align: left; /* Alinea el texto a la derecha */
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
  