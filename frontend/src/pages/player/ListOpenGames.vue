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
            color="white"
            outline
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
            color="white"
            outline
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
            color="white"
            outline
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
              @click="viewGameDetails(game.id)"
              class="match-card"
            >
            <q-card-section class="q-mt-md">
              <strong>{{ game.match_date }} | {{ game.match_time }}</strong><br>
              <q-icon name="o_sports_tennis"></q-icon> {{ game.category }}
              <div class="court-container">
                <div class="court">
                  <!-- Jugadores o botones de agregar -->
                  <div class="player team1-player1">
                    <div v-if="game.team1_players[0]">
                      {{ game.team1_players[0] || "Jugador 1 Equipo 1" }}
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
                      {{ game.team1_players[1] || "Jugador 2 Equipo 1" }}
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
                      {{ game.team2_players[0] || "Jugador 1 Equipo 2" }}
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
                      {{ game.team2_players[1] || "Jugador 2 Equipo 2" }}
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
            <q-card-section avatar>
                  <img
                    :src="game.club.logo_url || '/src/assets/logo.jpeg'"
                    alt="Club Logo"
                    class="club-logo"
                  />
                  {{ game.club.name }}
                </q-card-section>
            
            </q-card>
          </q-list>
          <div v-else-if="searching" class="text-center">Buscando...</div>
          <div v-else class="text-center">No se encontraron juegos.</div>
        </div>
      </q-page>
    </q-page-container>
    <PlayerNavigationMenu />
  </q-layout>
</template>

<script>
import { ref, onMounted, watch } from "vue";
import { supabase } from "../../services/supabase";
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

    const selectedCity = ref(null);
    const selectedDates = ref([]);
    const selectedGender = ref(null);

    const cityMenu = ref(false);
    const dateMenu = ref(false);
    const genderMenu = ref(false);

    const games = ref([]);
    const searching = ref(false);

    // Fetch cities from Supabase
    const fetchCities = async () => {
      try {
        const { data, error } = await supabase.rpc("get_unique_cities");
        if (error) {
          console.error("Error fetching cities:", error.message);
          return;
        }
        cityOptions.value = data.map((city) => ({
          label: city,
          value: city,
        }));
      } catch (error) {
        console.error("Unexpected error fetching cities:", error.message);
      }
    };

    // Fetch matches from Supabase with filters
    const fetchMatches = async () => {
        searching.value = true;
        try {
            let query = supabase
            .from("matches")
            .select(`
                *,
                club:clubs (
                name,
                city,
                logo_url,
                geolocation
                )
            `) // Relaciona la tabla "clubs" con "matches"
            .eq("is_open", true)
            .gt("match_date", new Date().toISOString());

            if (selectedCity.value) {
            query = query.eq("club.city", selectedCity.value); // Filtrar por ciudad del club
            }
            if (selectedGender.value) {
            query = query.eq("gender", selectedGender.value);
            }
            if (selectedDates.value.length > 0) {
            // Filtrado por fechas (igual que antes)
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

            const { data, error } = await query;
            if (error) {
            console.error("Error fetching matches:", error.message);
            games.value = [];
            } else {
            games.value = data;
            }
        } catch (error) {
            console.error("Unexpected error fetching matches:", error.message);
        } finally {
            searching.value = false;
        }
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
      searching,
      selectCity,
      selectDate,
      selectGender,
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

  .games-list .game-card {
    padding: 16px;
    border-radius: 8px;
    background-image: url("../../assets/texturafondo.png");
    background-size: cover;
    margin-bottom: 16px;
  }
  
  .club-logo {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    object-fit: cover;
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
  margin-bottom: 10px;
}

.court {
  position: relative;
  background-color: #1976d2;
  border-radius: 10px;
  color: white;
  width: 100%;
  max-width: 400px; /* Tamaño fijo para mantener proporción */
  aspect-ratio: 2 / 1; /* Relación de aspecto de la cancha */
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
  height: 1.5px; /* Ajusta el grosor de la línea si es necesario */
  background-color: white;
  opacity: 0.7;
  transform: translateY(-50%);
}
  </style>
  