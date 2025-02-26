<template>
  <q-layout view="hHh lpR fFf" class="body text-white">
    <q-header elevated class="bg-primary text-white">
      <div class="header-content">
        <div class="greeting">
          <img src="/src/assets/padelplay.png" alt="Logo" class="logo-icon" />
          Configura clases
        </div>
        <div class="header-icons">
          <q-btn flat round icon="arrow_back" @click="goBack" />
        </div>
      </div>
    </q-header>

    <q-page-container>
      <q-page class="q-pa-md">
        <!-- Lista de lecciones -->
        <q-list bordered class="q-mb-md">
          <q-item v-for="lesson in lessons" :key="lesson.id" class="q-my-sm">
            <q-item-section>
              <q-item-label>{{ lesson.name }}</q-item-label>
              <q-item-label caption>{{ lesson.description }}</q-item-label>
              <q-item-label caption>{{ lesson.lesson_date }} a las {{ lesson.lesson_time }}</q-item-label>
            </q-item-section>
          </q-item>
        </q-list>

        <!-- Botón flotante para agregar producto -->
        <q-btn
          glossy
          round
          size="lg"
          color="black"
          icon="add"
          class="fixed-bottom-right q-mb-xl"
          @click="openLessonDialog"
        />
      </q-page>
    </q-page-container>

    <!-- Diálogo para agregar una nueva lección -->
    <q-dialog v-model="lessonDialog">
      <q-card class="q-pa-md bg-black">
        <q-card-section>
          <div class="text-h6">Agregar nueva lección</div>
        </q-card-section>

        <q-card-section>
          <q-form @submit="createLesson">
            <q-input v-model="newLesson.name" label="Nombre" required />
            <q-input v-model="newLesson.description" label="Descripción" />
            <q-input v-model="newLesson.lesson_date" type="date" label="Fecha" required />
            <q-input v-model="newLesson.lesson_time" type="time" label="Hora" required />
            <q-input v-model="newLesson.duration" type="number" label="Duración (minutos)" required />
            <q-select v-model="newLesson.coach" :options="coaches" label="Entrenador" required />
            <q-select v-model="newLesson.court_id" :options="courts" label="Cancha" required />
            <q-input v-model="newLesson.price" type="number" label="Precio por Jugador" required />
            <q-btn type="submit" color="green" label="Crear lección" />
          </q-form>
        </q-card-section>
      </q-card>
    </q-dialog>

    <ClubNavigationMenu />
  </q-layout>
</template>

<script>
import { ref, onMounted } from "vue";
import { supabase } from "src/services/supabase";
import { useRouter } from "vue-router";
import { useQuasar } from 'quasar';
import { useUserStore } from "src/stores/userStore";
import api from "../../services/api";
import ClubNavigationMenu from "src/components/ClubNavigationMenu.vue";

export default {
  name: "ManageLessons",
  components: {
    ClubNavigationMenu,
  },
  setup() {
    const router = useRouter();
    const $q = useQuasar();
    const userStore = useUserStore();

    const lessons = ref([]);
    const coaches = ref([]);
    const courts = ref([]);
    const lessonDialog = ref(false);
    const newLesson = ref({
      name: "",
      description: "",
      lesson_date: "",
      lesson_time: "",
      duration: 60,
      coach: "",
      court_id: "",
      lesson_type: "public",
    });

    const goBack = () => {
      router.back();
    };

    const openLessonDialog = async () => {
      // Cargar entrenadores y canchas antes de abrir el diálogo
      const coachesResponse = await supabase.from("coaches").select("*").eq("club_id", userStore.clubId);
      const courtsResponse = await supabase.from("courts").select("*").eq("club_id", userStore.clubId);

      coaches.value = coachesResponse.data.map(coach => ({ label: coach.name, value: coach.id }));
      courts.value = courtsResponse.data.map(court => ({ label: court.name, value: court.id }));

      lessonDialog.value = true;
    };

    const createLesson = async () => {
      try {
        // Asegúrate de que todos los campos requeridos estén presentes
        const lessonData = {
          name: newLesson.value.name,
          description: newLesson.value.description,
          lesson_date: newLesson.value.lesson_date,
          lesson_time: newLesson.value.lesson_time,
          duration: newLesson.value.duration,
          lesson_type: newLesson.value.lesson_type,
          club_id: userStore.clubId, // Asegúrate de que club_id esté incluido
          court_id: newLesson.value.court_id.value, // Extrae el valor de court_id
          coach: newLesson.value.coach.value, // Extrae el valor de coach
          price: newLesson.value.price,
        };

        // Envía la solicitud al backend
        const response = await api.post("/lessons", lessonData);

        if (response.data.message === "Lección creada exitosamente") {
          $q.notify({
            type: "positive",
            message: "Lección creada exitosamente",
          });
          lessonDialog.value = false;
          loadLessons(); // Recarga la lista de lecciones
        }
      } catch (error) {
        $q.notify({
          type: "negative",
          message: "Error al crear la lección",
        });
        console.error("Error al crear la lección:", error);
      } finally {
        lessonDialog.value = false;
      }
    };

    const loadLessons = async () => {
      const response = await api.get(`/lessons?club_id=${userStore.clubId}`);
      lessons.value = response.data;
    };

    onMounted(() => {
      loadLessons();
    });

    return {
      goBack,
      lessons,
      coaches,
      courts,
      lessonDialog,
      newLesson,
      openLessonDialog,
      createLesson,
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
  
  .body {
    background-image: url(../../assets/menu/padelcourtfloor.jpg);
    background-size: cover;
  }

  .fixed-bottom-right {
    position: fixed;
    bottom: 80px;
    right: 20px;
    z-index: 1000;
  }
  
  </style>