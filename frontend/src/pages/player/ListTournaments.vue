<template>
  <q-layout view="hHh lpR fFf" class="bg-dark text-white">
    <q-header elevated class="text-white">
      <div class="header-content">
        <div class="greeting">
          <img src="/src/assets/padelplay.png" alt="Logo" class="logo-icon" />
        </div>
        <div class="header-icons"></div>
      </div>
      <BannerPromoScrolling />
    </q-header>

    <q-page-container>
      <q-page class="q-pa-md">
        <div class="filters">
          <q-select v-model="filters.city" :options="cityOptions" label="Ciudad" rounded standout class="filter-select" bg-color="primary">
            <template v-slot:prepend>
              <q-icon name="location_on" />
            </template>
          </q-select>
          <q-select v-model="filters.category" :options="categories" label="Categoría" rounded standout class="filter-select" bg-color="primary">
            <template v-slot:prepend>
              <q-icon name="category" />
            </template>
          </q-select>
          <q-select v-model="filters.gender" :options="genders" label="Género" rounded standout class="filter-select" bg-color="primary">
            <template v-slot:prepend>
              <q-icon name="wc" />
            </template>
          </q-select>
        </div>
        
        <q-card class="q-mb-md" clickable bordered @click="goToPadelite">
          <q-card-section>
            <q-img src="/src/assets/padelite/padelite.jpg" fit="fill"></q-img>
          </q-card-section>
        </q-card>
        
        <div v-if="tournaments.length === 0" class="text-center text-black">
          <q-icon name="event_busy" size="64px" />
          <p>No se encontraron torneos.</p>
        </div>
        <div v-else class="tournaments-list">
          <q-card v-for="tournament in tournaments" :key="tournament.id" class="q-mb-md tournament-card" clickable bordered @click="goToTournamentDetails(tournament.id)">
            <q-card-section>
              <h4 class="tennis-yellow">{{ tournament.name }}</h4>
              <p>
                <strong>Fecha:</strong> {{ tournament.start_date }} <br />
                <strong>Ciudad:</strong> {{ tournament.city || "No disponible" }} <br />
                <strong>Categoría:</strong> {{ tournament.category }} <br />
                <strong>Género:</strong> {{ tournament.gender }}
              </p>
            </q-card-section>
          </q-card>
        </div>
      </q-page>
    </q-page-container>
    
    <PlayerNavigationMenu />
  </q-layout>
</template>

<script>
import { ref, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import { fetchTournaments } from "../../services/supabase/tournaments";
import { fetchCities } from "../../services/supabase/commun"
import PlayerNavigationMenu from "../../components/PlayerNavigationMenu.vue";
import BannerPromoScrolling from "../../components/BannerPromoScrolling.vue";

export default {
  name: "ListTournaments",
  components: {
    PlayerNavigationMenu,
    BannerPromoScrolling,
  },
  setup() {
    const router = useRouter();
    const tournaments = ref([]);
    const filters = ref({ city: null, category: null, gender: null });
    const cityOptions = ref([]);
    const categories = ref(["primera", "segunda", "tercera", "cuarta", "quinta", "libre"]);
    const genders = ref(["mixto", "varonil", "femenil"]);

    const loadTournaments = async () => {
      tournaments.value = await fetchTournaments(filters.value);
    };

    const loadCities = async () => {
      cityOptions.value = await fetchCities();
    };

    const goToTournamentDetails = (id) => router.push({ name: "TournamentDetails", params: { tournamentId: id } });
    const goToPadelite = () => router.push("/padelite");

    watch(filters, loadTournaments, { deep: true });
    onMounted(() => {
      loadTournaments();
      loadCities();
    });

    return {
      tournaments,
      filters,
      cityOptions,
      categories,
      genders,
      goToTournamentDetails,
      goToPadelite,
    };
  },
};
</script>

<style scoped>
.filters {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  width: 100%;
}

.filter-select {
  flex: 1;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  background-color: #000000;
}

.logo-icon {
  width: 60px;
  height: 60px;
}

.tournaments-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.q-card {
  background-image: url(../../assets/texturafondo.png);
  background-size: cover;
  color: white;
}

.q-card:hover {
  background-color: #292929;
}

.tennis-yellow {
  color: #f0ff00;
}
</style>
