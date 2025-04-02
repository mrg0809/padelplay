<template>
    <div class="q-mt-md lesson-list">
      <div
        v-for="lesson in lessons"
        :key="lesson.id"
        class="lesson-card"
        @click="goToLessonDetails(lesson.id)"
      >
        <h5>{{ lesson.name }}</h5>
        <p>Fecha: {{ lesson.lesson_date }}</p>
        <p>Hora: {{ lesson.lesson_time }} hrs.</p>
      </div>
      <p v-if="lessons && lessons.length === 0" class="text-center q-mt-md">
        No hay clases abiertas en este club.
      </p>
    </div>
  </template>
  
  <script>
  import { ref, onMounted } from "vue";
  import { fetchClubLessons } from "../services/api/lessons";
  import { useRouter } from "vue-router";

  
  export default {
    props: {
      clubDetails: {
        type: Object,
        required: true,
      },
    },
    setup(props) {
      const lessons = ref([]); 
      const router = useRouter();
  
      const loadLessons = async () => {
        try {
          lessons.value = await fetchClubLessons(props.clubDetails.id);
        } catch (error) {
          console.error("Error al cargar clases:", error);
          lessons.value = [];
        }
      };

      const goToLessonDetails = (lessonId) => {
        router.push({
          name: "LessonDetails",
          params: { lessonId: lessonId },
          query: { clubId: props.clubDetails.id, clubName: props.clubDetails.name },
          });
        };
  
      onMounted(loadLessons); 
  
      return {
        lessons,
        goToLessonDetails,
      };
    },
  };
  </script>
  
  <style scoped>
  .lesson-list {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 16px;
  }
  
  .lesson-card {
    background-image: url(../assets/texturafondo.png);
    background-size: cover;
    padding: 16px;
    border-radius: 8px;
    cursor: pointer;
    transition: transform 0.3s, box-shadow 0.3s;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  }
  
  .lesson-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
  }
  
  .lesson-card h5 {
    margin: 0 0 8px;
    color: #ffd700;
  }
  
  .lesson-card p {
    margin: 4px 0;
    color: #ccc;
  }
  </style>
  