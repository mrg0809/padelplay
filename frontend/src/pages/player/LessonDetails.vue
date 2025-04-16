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
          <q-card> <q-card-section>
              <div v-if="isLoading" class="q-pa-xl text-center">
                <q-spinner-cube color="primary" size="xl" />
                <p class="q-mt-md">Cargando detalles de la clase...</p>
              </div>
  
              <div v-else-if="lesson" class="q-pa-md q-gutter-sm"> <h3>{{ lesson.name || 'Clase sin Nombre' }}</h3>
                <q-separator dark spaced="md" />
                <p v-if="lesson.description"><strong><q-icon name="mdi-information-outline" class="q-mr-xs"/>Descripción:</strong> {{ lesson.description }}</p>
                <p><strong><q-icon name="mdi-calendar" class="q-mr-xs"/>Fecha:</strong> {{ lesson.lesson_date || 'No especificada' }}</p>
                <p><strong><q-icon name="mdi-clock-outline" class="q-mr-xs"/>Hora:</strong> {{ lesson.lesson_time || 'No especificada' }} hrs.</p>
                <p><strong><q-icon name="mdi-timer-sand" class="q-mr-xs"/>Duración:</strong> {{ lesson.duration || '60' }} minutos</p> <p><strong><q-icon name="mdi-account-supervisor-circle-outline" class="q-mr-xs"/>Coach:</strong> {{ lesson.coaches.name || 'No asignado' }}</p> <p><strong><q-icon name="mdi-cash" class="q-mr-xs"/>Precio Inscripción:</strong> ${{ lesson.price?.toFixed(2) || 'N/A' }}</p>
                <p v-if="lesson.max_participants != null"> <strong><q-icon name="mdi-account-group-outline" class="q-mr-xs"/>Cupo:</strong> {{ lesson.available_slots ?? 'N/A' }} / {{ lesson.max_participants }} disponibles
                </p>

  
                <div class="q-mt-lg text-center">
                  <q-btn
                    color="green"
                    label="Inscribirme"
                    icon-right="mdi-pencil-plus-outline"
                    @click="proceedToSummary"
                    class="full-width"
                    size="lg"
                    push
                    :disable="!lesson || lesson.available_slots <= 0"
                    :title="!lesson || lesson.available_slots <= 0 ? 'No hay cupos disponibles o la clase no se cargó' : 'Inscribirse a esta clase'"
                  />
                   <div v-if="!lesson || lesson.available_slots <= 0" class="text-negative text-caption q-mt-xs">
                      {{ !lesson ? 'Error al cargar la clase' : 'No hay cupos disponibles' }}
                   </div>
                </div>
              </div>
  
              <div v-else class="q-pa-md text-center text-negative">
                 <q-icon name="mdi-alert-circle-outline" size="lg" />
                <p class="q-mt-md">No se pudieron cargar los detalles de la clase.</p>
                <q-btn flat label="Volver" @click="$router.go(-1)" />
              </div>
            </q-card-section>
          </q-card>
        </q-page>
        <PlayerNavigationMenu />
      </q-page-container>
    </q-layout>
  </template>
  
  <script setup> // Usando <script setup> para simplificar
  import { ref, onMounted } from "vue";
  import { useRoute, useRouter } from "vue-router";
  import { useQuasar } from 'quasar';
  import { useSummaryStore } from 'src/stores/summaryStore';
  import { getLessonDetails } from "src/services/supabase/lessons"; 
  import NotificationBell from "src/components/NotificationBell.vue";
  import BannerPromoScrolling from "src/components/BannerPromoScrolling.vue";
  import PlayerNavigationMenu from "src/components/PlayerNavigationMenu.vue";
  
  const route = useRoute();
  const router = useRouter();
  const summaryStore = useSummaryStore();
  const $q = useQuasar();
  

  const lessonId = route.params.lessonId;
  const clubId = route.query.clubId;
  const clubName = route.query.clubName || 'Club no especificado'; 
  
  // --- Estado Reactivo ---
  const lesson = ref(null); // Para guardar los detalles de la lección cargada
  const isLoading = ref(true); // Para manejar el estado de carga
  
  // --- Métodos ---
  const loadLessonDetails = async () => {
    isLoading.value = true;
    lesson.value = null; // Limpiar datos anteriores
    if (!lessonId) {
      console.error("ID de la lección no encontrado en los parámetros de la ruta.");
      $q.notify({ type: 'negative', message: 'No se pudo identificar la clase.' });
      isLoading.value = false;
      return;
    }
    try {
      const details = await getLessonDetails(lessonId); 
      lesson.value = details[0];
       if (!lesson.value || typeof lesson.value !== 'object') {
           throw new Error("Respuesta inválida del API al cargar detalles de clase.");
       }
    } catch (error) {
      console.error("Error al cargar detalles de la lección:", error);
      lesson.value = null; 
      $q.notify({ type: 'negative', message: 'Error al cargar la información de la clase.' });
    } finally {
      isLoading.value = false;
    }
  };
  
  const proceedToSummary = () => {
    if (!lesson.value) {
      console.error("Detalles de la lección no están cargados para ir al resumen.");
      $q.notify({ type: 'negative', message: 'No se pueden obtener los detalles de la clase.' });
      return;
    }
    if (lesson.value.available_slots <= 0) {
         $q.notify({ type: 'warning', message: 'Ya no hay cupos disponibles para esta clase.' });
        return;
    }
  
    // 1. Recopilar información de la lección actual
    const lessonData = lesson.value;
  
    // 2. Construir props para el resumen genérico
    const summaryProps = {
      summaryTitle: 'Resumen de Inscripción', // Título adecuado
      itemDetails: [
        { label: 'Club', value: clubName },
        { label: 'Clase', value: lessonData.name || 'No especificado' },
        { label: 'Fecha', value: lessonData.lesson_date || 'No especificada' },
        { label: 'Hora', value: `${lessonData.lesson_time || '--:--'} hrs.` },
        { label: 'Duración', value: `${lessonData.duration || 60} minutos` },
      ],
      baseData: {
        clubId: clubId,
        price: lessonData.price || 0, // Precio de inscripción individual
        participants: 1,             // Inscripción es para 1 persona
        type: 'public_lesson',       // Identificador de tipo
        id: lessonData.id,           // ID de la lección
      },
      allowPaymentSplit: false,      // No aplica para inscripción individual
      showPublicToggle: false,       // No aplica
      commissionRate: 4,             // O desde config
      extraData: {                   // Datos adicionales útiles
        coachName: lessonData.coach_name,
        lessonDescription: lessonData.description // Si existen en lessonData
      }
    };
  
    // 3. Guardar en Store
    summaryStore.setSummaryDetails(summaryProps);
    console.log('Datos del resumen de CLASE PÚBLICA guardados en Pinia:', summaryProps);
  

    router.push({ name: 'OrderSummary' });
  };
  
  onMounted(() => {
    loadLessonDetails();
  });
  
  
  </script>
  
  
  <style scoped>
  .home {
    background-color: #dddddd;
    min-height: 100vh; 
  }
  
  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 16px;
    background-color: #000000; 
  }
  
  .greeting {
    display: flex;
    align-items: center;
    gap: 8px; 
  }
  
  .header-icons {
    display: flex;
    gap: 2px; 
    align-items: center; 
  }
  
  .logo-icon {
    width: 60px; 
    height: 60px; 
  }
  
  .q-card {
    background-image: url(../../assets/texturafondo.png); 
    background-size: cover; 
    max-width: 400px; 
    margin: 16px auto;
    color: #fff;
    border-radius: 8px;
    box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2); 
  }
    
  
  h3 {
      text-align: center;
      color: #FFF; /* Cambiado a blanco para contraste con fondo de imagen */
      margin-bottom: 1rem; /* Añadido margen inferior */
  }
  h4 {
      margin-bottom: 10px;
      color: #eee; /* Color más claro para contraste */
      font-size: 1rem; /* Tamaño ajustado */
  }
  
  
  .text-center p {
    color: #ccc; 
  }
  
  .text-center {
    text-align: center;
  }
  
  /* Ajustes responsivos */
  @media (max-width: 600px) {
    .q-avatar {
      width: 150px !important;
      height: 150px !important;
    }
    h3 {
      font-size: 1.5rem;
    }

  }
  
  </style>