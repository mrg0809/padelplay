<template>
    <q-layout view="hHh lpR fFf" class="body text-white">
      <q-header elevated class="bg-primary text-white">
        <div class="header-content">
          <div class="greeting">
            <img src="/src/assets/padelplay.png" alt="Logo" class="logo-icon" />
            Soporte
          </div>
          <div class="header-icons">
            <q-btn flat round icon="arrow_back" @click="goBack" />
          </div>
        </div>
      </q-header>
  
      <q-page-container>
        <q-page class="q-pa-md">
          <!-- FAQ dentro de un q-card translúcido -->
          <q-card class="transparent-card q-pa-md">
            <q-card-section>
              <h4 class="text-h5 q-mb-md">Preguntas Frecuentes (FAQ)</h4>
  
              <!-- Preguntas y respuestas -->
              <div v-for="(faq, index) in faqs" :key="index" class="q-mb-md">
                <h6 class="text-h6 q-mb-sm">{{ faq.question }}</h6>
                <p class="q-mb-md">{{ faq.answer }}</p>
                <q-separator v-if="index < faqs.length - 1" />
              </div>
            </q-card-section>
          </q-card>
        </q-page>
  
        <!-- Botón flotante para soporte por WhatsApp -->
        <q-btn
          glossy
          round
          size="lg"
          color="green"
          icon="support_agent"
          class="fixed-bottom-right q-mb-xl"
          @click="openWhatsApp"
        />
      </q-page-container>
      <ClubNavigationMenu />
    </q-layout>
  </template>
  
  <script>
  import { ref } from "vue";
  import { useRouter } from "vue-router";
  import ClubNavigationMenu from "src/components/ClubNavigationMenu.vue";
  
  export default {
    name: "SupportOptions",
    components: {
      ClubNavigationMenu,
    },
    setup() {
      const router = useRouter();
  
      // Lista de preguntas frecuentes
      const faqs = ref([
        {
            question: "1. ¿Cómo puedo registrar mi club en la plataforma?",
            answer:
            "Para registrar tu club, ve a la página de registro, completa el formulario con los datos de tu club y sube los documentos requeridos. Una vez aprobado, podrás acceder a tu panel de administración.",
        },
        {
            question: "2. ¿Cómo agrego canchas a mi club?",
            answer:
            'Inicia sesión en tu panel de administración, ve a la sección "Canchas" y haz clic en "Agregar Cancha". Completa los detalles de la cancha y guarda los cambios.',
        },
        {
            question: "3. ¿Cómo gestiono las reservaciones?",
            answer:
            'Desde la sección "Reservaciones" de tu panel de administración, puedes ver todas las reservaciones activas, aprobar, cancelar o modificar reservaciones, y generar reportes.',
        },
        {
            question: "4. ¿Cómo configuro los precios de las canchas?",
            answer:
            'Ve a la sección "Canchas", selecciona la cancha que deseas configurar y haz clic en "Editar Precios". Define los precios por hora, media hora o paquetes especiales.',
        },
        {
            question: "5. ¿Cómo agrego productos adicionales (como raquetas o pelotas)?",
            answer:
            'Ve a la sección "Productos" en tu panel de administración, haz clic en "Agregar Producto" y completa los detalles del producto (nombre, marca, precio, modalidad de venta o renta).',
        },
        {
            question: "6. ¿Cómo cierro un torneo y genero el fixture?",
            answer:
            'Ve a la sección "Torneos", selecciona el torneo que deseas cerrar y haz clic en "Cerrar Torneo". El sistema generará automáticamente el fixture y notificará a los participantes.',
        },
        {
            question: "7. ¿Cómo contacto al soporte técnico?",
            answer:
            "Puedes contactarnos por correo electrónico (soporte@tupagina.com), teléfono (+52 55 1234 5678) o chat en vivo desde tu panel de administración.",
        },
        {
            question: "8. ¿Cómo actualizo la información de mi club?",
            answer:
            'Ve a la sección "Mi Club" en tu panel de administración, haz clic en "Editar Información" y actualiza los datos que necesites (dirección, teléfono, horarios, etc.).',
        },
        {
            question: "9. ¿Cómo gestiono los pagos y facturación?",
            answer:
            'Desde la sección "Pagos" de tu panel de administración, puedes ver el historial de pagos, generar facturas y configurar métodos de pago.',
        },
        {
            question: "10. ¿Cómo promociono mi club en la plataforma?",
            answer:
            'Ve a la sección "Promociones", crea ofertas especiales (descuentos en reservaciones, paquetes promocionales, etc.) y publícalas en la plataforma.',
        },
        {
            question: "11. ¿Cómo bloqueo una cancha por mantenimiento?",
            answer:
            'Ve a la sección "Canchas", selecciona la cancha que deseas bloquear, haz clic en "Bloquear Cancha" y define el período de bloqueo (fecha y hora de inicio y fin).',
        },
        {
            question: "12. ¿Cómo veo las estadísticas de mi club?",
            answer:
            'Puedes ver las estadísticas de tu club en la sección "Reportes" de tu panel de administración. Ahí encontrarás reservaciones, ingresos y productos más vendidos o rentados.',
        },
        {
            question: "13. ¿Cómo configuro los horarios de mi club?",
            answer:
            'Ve a la sección "Horarios", define los horarios de apertura y cierre para cada día de la semana y guarda los cambios.',
        },
        {
            question: "14. ¿Cómo agrego nuevos administradores o empleados?",
            answer:
            'Ve a la sección "Usuarios", haz clic en "Agregar Usuario" y completa los datos del usuario (nombre, correo, rol, etc.).',
        },
        {
            question: "15. ¿Cómo restablezco mi contraseña?",
            answer:
            'Ve a la página de inicio de sesión, haz clic en "¿Olvidaste tu contraseña?" e ingresa tu correo electrónico para recibir instrucciones.',
        },
        {
            question: "16. ¿Cómo cancelo mi suscripción?",
            answer:
            'Ve a la sección "Suscripción" en tu panel de administración, haz clic en "Cancelar Suscripción" y confirma la acción.',
        },
        {
            question: "17. ¿Cómo obtengo más información sobre las funcionalidades avanzadas?",
            answer:
            "Contáctanos a través de correo electrónico (soporte@tupagina.com) o teléfono (+52 55 1234 5678) para obtener más información.",
        },
        {
            question: "18. ¿Cómo reporto un problema técnico?",
            answer:
            'Ve a la sección "Soporte" en tu panel de administración, describe el problema con detalle y adjunta capturas de pantalla si es necesario.',
        },
        {
            question: "19. ¿Cómo puedo mejorar la visibilidad de mi club?",
            answer:
            "Asegúrate de que la información de tu club esté completa y actualizada, publica promociones y solicita a tus clientes que dejen reseñas en la plataforma.",
        },
        {
            question: "20. ¿Cómo accedo a los tutoriales y guías?",
            answer:
            'Puedes acceder a tutoriales y guías en la sección "Ayuda" de tu panel de administración. Ahí encontrarás videos y documentos paso a paso.',
        },
        ]);
  
      // Función para abrir WhatsApp
      const openWhatsApp = () => {
        const phoneNumber = "6643654383";
        const message = "Hola Padelplay, necesito soporte técnico.";
        const url = `https://wa.me/${phoneNumber}?text=${encodeURIComponent(message)}`;
        window.open(url, "_blank");
      };
  
      // Función para regresar
      const goBack = () => {
        router.back();
      };
  
      return {
        faqs,
        openWhatsApp,
        goBack,
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
  
  .transparent-card {
    background-color: rgba(255, 255, 255, 0.3); /* Fondo translúcido */
    border-radius: 8px;
  }
  
  .fixed-bottom-right {
    position: fixed;
    bottom: 80px;
    right: 20px;
    z-index: 1000;
  }
  
  .text-h5 {
    font-size: 1.5rem;
    font-weight: bold;
    margin-bottom: 16px;
  }
  
  .text-h6 {
    font-size: 1.25rem;
    font-weight: bold;
    margin-bottom: 8px;
  }
  
  .q-mb-md {
    margin-bottom: 16px;
  }
  
  .q-mb-sm {
    margin-bottom: 8px;
  }
  </style>