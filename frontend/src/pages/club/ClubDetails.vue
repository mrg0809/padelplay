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
        <div v-if="club.loading.value === true" class="text-center">
          <q-spinner-dots color="primary" size="xl" />
        </div>
        <div v-else>
          <!-- Club logo -->
          <div class="q-mb-md text-center">
            <img 
              v-if="clubLogoUrl" 
              :src="clubLogoUrl" 
              alt="Club Logo" 
             style="max-width: 150px; border-radius: 8px;"
           />
         </div>
         
         <!-- Tabs navigation -->
         <q-card class="tabs-section">
           <q-card-section>
             <q-tabs v-model="selectedTab" align="justify" class="text-white">
              <q-icon name="arrow_back_ios" />
               <q-tab name="info" label="Info" icon="o_info" />
               <q-tab name="reservations" label="Reservas" icon="event" />
               <q-tab name="tournaments" label="Torneos" icon="o_emoji_events" />
               <q-tab name="publiclessons" label="Clases" icon="event" />
               <q-tab name="privatelessons" label="Coaches" icon="o_school" />
               <q-tab name="wall" label="Muro" icon="o_chat" />
               <q-icon name="arrow_forward_ios" />
             </q-tabs>
           </q-card-section>
         </q-card>
         <q-separator />
         
         <!-- Tab content components -->
         <ClubInfoComponent
           v-if="selectedTab === 'info'"
           :clubDetails="unwrappedClubDetails"
           :coordinates="club.coordinates.value"
         />
         <ReservationsComponent
          v-if="selectedTab === 'reservations'"
          :days="reservations.days.value"
          :selectedDay="reservations.selectedDay.value"
          :consolidatedTimes="reservations.consolidatedTimes.value"
          :selectedTime="reservations.selectedTime.value || ''"
          :loadingTimes="reservations.loadingTimes.value"
          :availableCourts="reservations.availableCourts.value"
          :loadingCourts="Boolean(reservations.loadingCourts.value)"
          :timeOptions="reservations.timeOptions.value"
          @previous-week="reservations.previousWeek"
          @next-week="reservations.nextWeek"
          @select-day="reservations.selectDay"
          @select-time="reservations.selectTime"
          @select-duration="onSelectDuration"
        />
         <TournamentsClubListComponent
           v-if="selectedTab === 'tournaments'"
           :tournaments="club.tournaments.value"
           @go-to-tournament-details="goToTournamentDetails"
         />
         <ClubWallComponent
           v-if="selectedTab === 'wall'"
           :posts="club.posts.value"
           :reactionEmojis="reactionEmojis"
           :selectedReaction="selectedReaction"
           :playerId="userStore.userId"
           :menuVisible="menuVisible"
           @update:posts="updatePosts"
         />
         <LessonsComponent
          v-if="selectedTab === 'publiclessons'"
          :clubDetails="unwrappedClubDetails"
        />
        <CoachesComponent
          v-if="selectedTab === 'privatelessons'"
          :clubDetails="unwrappedClubDetails"
        />
       </div>
     </q-page>
   </q-page-container>
   <PlayerNavigationMenu />
 </q-layout>
</template>

<script>
import { ref, onMounted, watch, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useQuasar } from "quasar";
import { useUserStore } from "src/stores/userStore";
import { useClub } from "src/composables/useClub";
import { useReactions } from "src/composables/useReactions";
import { useReservations } from "src/composables/useReservations";
import "leaflet/dist/leaflet.css";

// Components
import BannerPromoScrolling from "src/components/BannerPromoScrolling.vue";
import NotificationBell from "src/components/NotificationBell.vue";
import PlayerNavigationMenu from "src/components/PlayerNavigationMenu.vue";
import ClubWallComponent from "src/components/ClubWallComponent.vue";
import TournamentsClubListComponent from "src/components/TournamentsClubListComponent.vue";
import ReservationsComponent from "src/components/ReservationsComponent.vue";
import ClubInfoComponent from "src/components/ClubInfoComponent.vue";
import LessonsComponent from "src/components/LessonsComponent.vue";
import CoachesComponent from "src/components/CoachesComponent.vue";

export default {
  components: {
    BannerPromoScrolling,
    NotificationBell,
    PlayerNavigationMenu,
    ClubWallComponent,
    ReservationsComponent,
    TournamentsClubListComponent,
    ClubInfoComponent,
    LessonsComponent,
    CoachesComponent,
  },
  setup() {
    const route = useRoute();
    const router = useRouter();
    const $q = useQuasar();
    const userStore = useUserStore();
    const selectedTab = ref("info");
    const clubId = route.params.clubId;
    
    // Composables
    const club = useClub();
    const reservations = useReservations(clubId);
    const { toggleReaction } = useReactions();
    
    // Reaction state
    const reactionEmojis = {
      like: "👍",
      love: "❤️",
      laugh: "😂",
      wow: "😮",
      sad: "😢",
      angry: "😡",
    };
    const selectedReaction = ref(null);
    const menuVisible = ref(false);

    const updatePosts = (updatedPosts) => {
      club.posts.value = updatedPosts;
    };

    // Computed property to unwrap the ref value for passing to components
    const unwrappedClubDetails = computed(() => {
      return club.clubDetails.value;
    });

    const clubLogoUrl = computed(() => {
      return club.clubDetails.value?.logo_url || null; // Usa encadenamiento opcional
    });

    // Watch for tab changes to initialize map when info tab is selected
    watch(selectedTab, (newTab) => {
      if (newTab === "info" && club.coordinates.value) {
        club.initMap();
      }
    });

    // Handle reservation selection
    const onSelectDuration = (payload) => {
      const { option, court} = payload;

      if (!court || !reservations.selectedDay.value || !reservations.selectedTime.value) {
        const missingFields = [];
        if (!court) missingFields.push("cancha");
        if (!reservations.selectedDay.value) missingFields.push("día");
        if (!reservations.selectedTime.value) missingFields.push("hora");

        $q.notify({
          color: "negative",
          message: `Datos incompletos: ${missingFields.join(", ")}`,
        });
        return;
      }

      const clubDetails = club.clubDetails.value

      const reservationDetails = {
        clubId: clubDetails.id || "ID de club no especificado",
        clubName: clubDetails.name || "Nombre de club no especificado",
        courtId: court.id || "ID de cancha no especificado",
        courtName: court.name || "Nombre de cancha no especificado",
        date: reservations.selectedDay.value || "Fecha no especificada",
        time: reservations.selectedTime.value || "Hora no especificada",
        duration: option.duration || 0,
        price: reservations.getCourtPrice(court, option.duration) || 0,
      };

      router.push({
        name: "ReservationSummary",
        query: reservationDetails,
      });
    };

    const goToTournamentDetails = (tournamentId) => {
      router.push({ name: "TournamentDetails", params: { tournamentId } });
    }

    // Initialize data on component mount
    onMounted(async () => {
      if (!clubId) {
        club.loading.value = false;
        console.error("Club ID is undefined");
        return;
      }

      try {
        if (route.params.tab) {
          selectedTab.value = route.params.tab;
        } else if (route.query.tab) {
          selectedTab.value = route.query.tab;
        }

        // Fetch club data
        await club.fetchClubData(clubId);
        
        // Initialize reservations
        await reservations.fetchTimes();

        // Initialize map if on info tab
        if (selectedTab.value === "info" && club.coordinates.value) {
          club.initMap();
        }
      } catch (error) {
        club.loading.value = false;
        console.error("Error initializing club details:", error);
        $q.notify({
          color: "negative",
          message: "Error al cargar detalles del club.",
        });
      }
    });

    return {
      club,
      reservations,
      selectedTab,
      reactionEmojis,
      menuVisible,
      selectedReaction,
      updatePosts,
      unwrappedClubDetails,
      toggleReaction,
      userStore, 
      onSelectDuration,
      clubLogoUrl,
      goToTournamentDetails,
    };
  },
};
</script>

<style scoped>
.club-logo {
  width: 300px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.logo-icon {
  width: 60px;
  height: 60px;
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

.tabs-section {
  margin-bottom: 10px;
  background-image: url(../../assets/texturafondo.png);
  background-size: cover;
  border-radius: 20px;
}
</style>
