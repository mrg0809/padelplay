<template>
  <q-layout view="hHh lpR fFf" class="bg-dark text-white">
    <q-header elevated class="text-white">
      <div class="header-content">
        <div class="greeting">
          <img src="/src/assets/padelplay.png" alt="Logo" class="logo-icon" />
        </div>
        <div class="header-icons">
          <NotificationBell />
          <PlayerTopMenu />
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
          <q-card class="text-white q-pa-md match-card">
            <q-card-section>
              <div class="row items-center" style="position: relative; width: 100%; margin-bottom: 20px;">
                <q-btn flat @click="shareClass" style="position: absolute; left: 0;">
                  <q-icon name="o_share" size="md" />
                </q-btn>
                <h3 class="text-h5 text-white" style="flex: 1; margin: 0; text-align: center;">Entrenamiento</h3>
              </div>
              <p>
                Entrenas en el club {{ classDetails.clubs.name || "No disponible" }}
                <q-btn size="sm" flat round color="orange" icon="o_location_on" @click="goToMapLocation(classDetails.clubs.latitude, classDetails.clubs.longitude)"></q-btn>
                el día {{ formatLargeDate(classDetails.lesson_date.value) }} a
                las {{ classDetails.lesson_time.slice(0, 5) }} hrs. En la cancha {{ classDetails.courts.name || "No disponible" }}.
              </p>
              <p>Tipo de partido: Clase Privada<br>
                Precio: ${{ classDetails.price }} PP: ${{ classDetails.price / classDetails.participants }}<br>
                Coach: {{ classDetails.coaches.name }}</p>
            </q-card-section>
          </q-card>

          <q-card class="match-card text-white q-pa-md">
            <q-card-section class="q-mt-md">
              <h3 class="text-center text-white">Participantes</h3>
              <q-list bordered separator>
                <q-item v-for="player in classDetails.playerDetails" :key="player.user_id">
                  <q-item-section avatar>
                    <q-avatar size="48px">
                      <img :src="player.photo_url" alt="Foto del jugador" style="border-radius: 50%;" />
                    </q-avatar>
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>{{ player.first_name }}</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item v-for="i in (classDetails.participants - classDetails.playerDetails.length)" :key="'add-player-' + i" clickable @click="openSearchPlayerDialog">
                  <q-item-section avatar>
                    <q-avatar size="48px" class="bg-grey-7">
                      <q-icon name="person_add" size="32px" color="white" />
                    </q-avatar>
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>Agregar jugador</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </q-card-section>
          </q-card>
        </div>
      </q-page>
    </q-page-container>

    <q-dialog v-model="searchPlayerDialog">
      <q-card>
        <q-card-section>
          <div class="text-h6">Agregar Jugador</div>
            <PlayerSearch v-model="searchPlayerDialog" @playerSelected="addSelectedPlayer" />
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancelar" color="negative" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <PlayerNavigationMenu />
  </q-layout>
</template>

<script setup>
  import { ref, onMounted } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import { useQuasar } from 'quasar';

  import { getPrivateLessonDeatails } from 'src/services/supabase/lessons';
  import { formatLargeDate } from 'src/helpers/dateUtils';
  import { goToMapLocation } from 'src/helpers/locationUtils';
  import { shareContent } from 'src/helpers/shareUtils';

  import PlayerNavigationMenu from 'src/components/PlayerNavigationMenu.vue';
  import BannerPromoScrolling from 'src/components/BannerPromoScrolling.vue';
  import NotificationBell from 'src/components/NotificationBell.vue';
  import PlayerTopMenu from 'src/components/PlayerTopMenu.vue';
  import PlayerSearch from 'src/components/PlayerSearch.vue';

  const route = useRoute();
  const router = useRouter();
  const $q = useQuasar();

  const classDetails = ref(null);
  const loading = ref(true);
  const searchPlayerDialog = ref(false);

  const fetchClassDetails = async () => {
    try {
      const data = await getPrivateLessonDeatails(route.params.lessonId);
      classDetails.value = data;
      console.log(classDetails.value)
    } catch (error) {
      console.error('Error al cargar los detalles del partido:', error.message);
      $q.notify({
        type: 'negative',
        message: 'Error al cargar los detalles del partido.',
      });
    } finally {
      loading.value = false;
    }
  };

  const openSearchPlayerDialog = () => {
    searchPlayerDialog.value = true;
  };

  const addSelectedPlayer = (player) => {
    console.log('Jugador seleccionado:', player);
    // Aquí puedes agregar la lógica para agregar el jugador seleccionado al evento
    searchPlayerDialog.value = false; // Cierra el diálogo PlayerSearch
  };

  const shareClass = () => {
    const title = 'Únete a esta clase.';
    const url = window.location.href;
    const text = 'Echa un vistazo a esta clase de padel.';

    shareContent(title, url, text);
  };


  onMounted(fetchClassDetails);
</script>
    
  <style scoped>
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
  
  .header {
    text-align: center;
    font-weight: bold;
    color: white;
  }
  
  .team-label {
    text-align: center;
    font-weight: bold;
    color: white;
  }
  
  </style>