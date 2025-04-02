<template>
  <q-layout view="hHh lpR fFf" class="bg-dark text-white">
    <q-header elevated class="text-white">
      <!-- Header content -->
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

        <!-- === FILTERS REFACTORED === -->
        <!-- Use Quasar grid system for responsiveness -->
        <div class="row q-col-gutter-md q-mb-lg">
          <!-- City Filter -->
          <div class="col-12 col-sm-4">
            <q-select
              v-model="filters.city"
              :options="cityOptions"
              label="Ciudad"
              outlined  dense options-dense clearable @filter="filterCityFn" @clear="filters.city = null"
              dark color="black" label-color="black" popup-content-class="bg-dark text-black"
            >
              <template v-slot:prepend>
                <q-icon name="location_on" color="black"/>
              </template>
               <template v-slot:no-option>
                 <q-item>
                   <q-item-section class="text-grey">
                     No hay ciudades disponibles
                   </q-item-section>
                 </q-item>
               </template>
            </q-select>
          </div>

          <!-- Category Filter -->
          <div class="col-12 col-sm-4">
            <q-select
              v-model="filters.category"
              :options="categories"
              label="Categoría"
              outlined dense options-dense clearable
              dark color="black" label-color="black" popup-content-class="bg-dark text-black"
               @clear="filters.category = null"
            >
              <template v-slot:prepend>
                <q-icon name="category" color="black"/>
              </template>
               <template v-slot:no-option>
                 <q-item>
                   <q-item-section class="text-grey">
                     No hay categorías
                   </q-item-section>
                 </q-item>
               </template>
            </q-select>
          </div>

          <!-- Gender Filter -->
          <div class="col-12 col-sm-4">
            <q-select
              v-model="filters.gender"
              :options="genders"
              label="Género"
              outlined dense options-dense clearable
              dark color="black" label-color="black" popup-content-class="bg-dark text-black"
              @clear="filters.gender = null"
            >
              <template v-slot:prepend>
                <q-icon name="wc" color="black"/>
              </template>
               <template v-slot:no-option>
                 <q-item>
                   <q-item-section class="text-grey">
                     No hay géneros
                   </q-item-section>
                 </q-item>
               </template>
            </q-select>
          </div>
        </div>
        <!-- === END FILTERS === -->


        <q-card class="q-mb-md" clickable bordered @click="goToPadelite">
           <!-- ... Padelite card content ... 
           <q-card-section>
             <q-img src="/src/assets/padelite/padelite.jpg" fit="fill"></q-img>
           </q-card-section>
           -->
        </q-card>

        <!-- Tournament List -->
         <div v-if="loadingTournaments" class="text-center q-pa-xl"> <!-- Added loading state -->
           <q-spinner-gears color="primary" size="xl" />
           <p class="q-mt-md">Buscando torneos...</p>
         </div>
        <div v-else-if="tournaments.length === 0" class="text-center text-grey-5 q-pa-xl"> <!-- Adjusted text color -->
          <q-icon name="event_busy" size="64px" />
          <p>No se encontraron torneos con los filtros seleccionados.</p>
        </div>
        <div v-else class="tournaments-list row q-col-gutter-md"> <!-- Use grid for list too -->
          <div v-for="tournament in tournaments" :key="tournament.id" class="col-12 col-sm-6 col-md-4"> <!-- Responsive cols -->
             <q-card class="tournament-card full-height" clickable bordered @click="goToTournamentDetails(tournament.id)">
                <!-- Using full-height might need q-card-section to grow -->
               <q-card-section>
                 <h4 class="tennis-yellow q-mt-none q-mb-sm">{{ tournament.name }}</h4>
                 <p class="q-mb-xs"> <!-- Reduced bottom margin -->
                   <strong><q-icon name="mdi-calendar" size="xs"/> Fecha:</strong> {{ tournament.start_date }} <br />
                   <strong><q-icon name="mdi-map-marker" size="xs"/> Ciudad:</strong> {{ tournament.clubs.city || "N/A" }} <br /> <!-- Added icon -->
                   <strong><q-icon name="mdi-trophy-variant-outline" size="xs"/> Cat:</strong> {{ tournament.category }} <br /> <!-- Added icon -->
                   <strong><q-icon name="mdi-gender-male-female" size="xs"/> Gen:</strong> {{ tournament.gender }} <!-- Added icon -->
                 </p>
               </q-card-section>
             </q-card>
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
import { fetchTournaments } from "../../services/supabase/tournaments";
import { fetchCities } from "../../services/supabase/commun";
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
    const allCityOptions = ref([]); 
    const cityOptions = ref([]); 
    const categories = ref(["primera", "segunda", "tercera", "cuarta", "quinta", "libre"]); 
    const genders = ref(["mixto", "varonil", "femenil"]); 
    const loadingTournaments = ref(false); 


    const loadTournaments = async () => {
      loadingTournaments.value = true;
      try {
           tournaments.value = await fetchTournaments(filters.value);
      } catch (error) {
          console.error("Error loading tournaments:", error);
          tournaments.value = []; 
      } finally {
          loadingTournaments.value = false;
      }
    };

    const loadCities = async () => {
       try {
           const cities = await fetchCities();
           allCityOptions.value = cities.map(city => typeof city === 'string' ? city : city.value || city.label || city);
           cityOptions.value = allCityOptions.value; 
       } catch (error) {
           console.error("Error loading cities:", error);
           allCityOptions.value = [];
           cityOptions.value = [];
       }
    };

     const filterCityFn = (val, update) => {
       if (val === '') {
         update(() => {
           cityOptions.value = allCityOptions.value; 
         })
         return
       }

       update(() => {
         const needle = val.toLowerCase()
         cityOptions.value = allCityOptions.value.filter(v => v.toLowerCase().indexOf(needle) > -1)
       })
     }

    const goToTournamentDetails = (id) => router.push({ name: "TournamentDetails", params: { tournamentId: id } });
    const goToPadelite = () => router.push("/padelite");

    watch(filters, loadTournaments, { deep: true });

    onMounted(() => {
      loadTournaments(); 
      loadCities();
    });

    return {
      tournaments,
      loadingTournaments, 
      filters,
      cityOptions, 
      categories,
      genders,
      goToTournamentDetails,
      goToPadelite,
      filterCityFn, 
    };
  },
};
</script>

<style scoped>

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

.q-card.tournament-card { /* Target specific tournament cards */
  background-image: url(../../assets/texturafondo.png);
  background-size: cover;
  background-position: center;
  color: white;
   transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out; /* Add transition */
   height: 100%; 
   display: flex; 
   flex-direction: column; 
}

.q-card.tournament-card .q-card-section {
    flex-grow: 1; /* Make section fill height */
}


.q-card.tournament-card:hover {
  /* background-color: #292929; */ /* Hover effect might be subtle with background */
  transform: translateY(-3px); /* Slight lift effect */
  box-shadow: 0px 6px 12px rgba(0, 0, 0, 0.4); /* Enhanced shadow */
}

.tennis-yellow {
  color: #f0ff00; /* Keep yellow for tournament name */
   font-size: 1.1rem; /* Slightly smaller heading */
    font-weight: bold;
    line-height: 1.3;
}

.q-card p {
    font-size: 0.9rem;
    line-height: 1.5;
    color: #f0f0f0; /* Slightly off-white for paragraph text */
}
.q-card p strong {
    color: #fafafa; /* Brighter white for strong text */
     margin-right: 4px; /* Space after icon/label */
}
.q-card p strong .q-icon { /* Align icons better */
     vertical-align: middle;
     margin-bottom: 2px;
}

:deep(.q-field--outlined.q-field--dark .q-field__control):before {
  border-color: rgba(0, 0, 0, 0.4) !important;
}
:deep(.q-field--outlined.q-field--dark .q-field__control):hover:before {
  border-color: rgba(0, 0, 0, 0.8) !important;
}
/* Style for the select dropdown popup */
.q-menu.bg-dark {
   border: 1px solid rgba(0, 0, 0, 0.2);
}

</style>