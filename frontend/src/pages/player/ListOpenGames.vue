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

          <!-- Button Dropdown for Genre -->
          <q-btn
            dense
            color="white"
            outline
            icon="wc"
            label="Tipo"
            @click="genreMenu = true"
          />
          <q-menu v-model="genreMenu" anchor="bottom left" self="top left">
            <q-list>
              <q-item
                v-for="genre in genreOptions"
                :key="genre.value"
                clickable
                @click="selectGenre(genre)"
              >
                <q-item-section>{{ genre.label }}</q-item-section>
              </q-item>
            </q-list>
          </q-menu>
        </div>

        <!-- Games List -->
        <div class="games-list">
          <q-list v-if="games.length > 0" class="q-mt-md">
            <q-item
              v-for="game in games"
              :key="game.id"
              clickable
              @click="viewGameDetails(game.id)"
              class="game-card"
            >
              <q-item-section avatar>
                <img
                  :src="club.logo_url || '/src/assets/logo.jpeg'"
                  alt="Club Logo"
                  class="club-logo"
                />
              </q-item-section>
              <q-item-section>
                <q-item-label class="club-name">{{ club.name }}</q-item-label>
                <q-item-label caption>{{ club.address }}</q-item-label>
                <q-item-label caption v-if="club.distance">
                  Distancia: {{ (club.distance / 1000).toFixed(2) }} km
                </q-item-label>
              </q-item-section>
            </q-item>
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
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
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
    const genreOptions = ref([
      { label: "Femenil", value: "femenil" },
      { label: "Varonil", value: "varonil" },
      { label: "Mixto", value: "mixto" },
    ]);

    const selectedCity = ref(null);
    const selectedDates = ref([]);
    const selectedGenre = ref(null);

    const cityMenu = ref(false);
    const dateMenu = ref(false);
    const genreMenu = ref(false);

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

    const selectCity = (city) => {
      selectedCity.value = city.value;
      cityMenu.value = false;
    };

    const selectDate = (date) => {
      if (!selectedDates.value.includes(date.value)) {
        selectedDates.value.push(date.value);
      } else {
        selectedDates.value = selectedDates.value.filter(
          (d) => d !== date.value
        );
      }
      dateMenu.value = false;
    };

    const selectGenre = (genre) => {
      selectedGenre.value = genre.value;
      genreMenu.value = false;
    };

    onMounted(fetchCities);

    return {
      cityOptions,
      dateOptions,
      genreOptions,
      selectedCity,
      selectedDates,
      selectedGenre,
      cityMenu,
      dateMenu,
      genreMenu,
      selectCity,
      selectDate,
      selectGenre,
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
    width: 64px;
    height: 64px;
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
  </style>
  