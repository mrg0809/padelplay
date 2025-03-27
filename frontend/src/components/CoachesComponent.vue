<template>
    <div class="q-mt-md coach-list">
      <div
        v-for="coach in coaches"
        :key="coach.id"
        class="coach-card"
        @click="goToCoachDetails(coach.id)"
      >
        <q-avatar size="100px">
          <img :src="coach.players?.photo_url || '/ruta/imagen-default.jpg'" alt="Foto del coach" />
        </q-avatar>
        <div class="coach-info">
          <p class="coach-name">{{ coach.name }}</p>
          <p class="coach-focus">Especialidad: {{ coach.coach_focus }}</p>
        </div>
      </div>
      <p v-if="coaches && coaches.length === 0" class="text-center q-mt-md">
        No hay entrenadores disponibles en este momento.
      </p>
    </div>
  </template>
  
  <script>
  import { ref, onMounted } from "vue";
  import { useRouter } from "vue-router";
  import { getCoachesByClub } from "src/services/supabase/coaches";
  
  export default {
    props: {
      clubDetails: {
        type: Object,
        required: true,
      },
    },
    setup(props) {
      const coaches = ref([]); 
      const router = useRouter();
  
      const loadCoaches = async () => {
        try {
          console.log("Club ID:", props.clubDetails.id);
          coaches.value = await getCoachesByClub(props.clubDetails.id);
        } catch (error) {
          console.error("Error al cargar entrenadores:", error);
          coaches.value = [];
        }
      };
  
      const goToCoachDetails = (coach) => {
        console.log("Coach seleccionado:", coach);
        router.push({
          name: "CoachDetails",
          params: { coachId: coach },
          query: { clubId: props.clubDetails.id },
          });
        };
  
      onMounted(() => {
        if (props.clubDetails?.id) {
          loadCoaches();
        }
      });
  
      return {
        coaches,
        goToCoachDetails,
      };
    },
  };
  </script>
  
  <style scoped>
  .coach-list {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 16px;
  }
  
  .coach-card {
    display: flex; /* Alinea imagen y texto en línea */
    align-items: center;
    background-image: url(../assets/texturafondo.png);
    background-size: cover;
    padding: 16px;
    border-radius: 8px;
    cursor: pointer;
    transition: transform 0.3s, box-shadow 0.3s;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  }
  
  .coach-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
  }
  
  .coach-info {
    margin-left: 16px;
  }
  
  .coach-name {
    font-weight: bold;
    font-size: 18px;
    color: #ffd700;
    margin: 0;
  }
  
  .coach-focus {
    font-size: 14px;
    color: #ccc;
    margin: 4px 0;
  }
  </style>
  