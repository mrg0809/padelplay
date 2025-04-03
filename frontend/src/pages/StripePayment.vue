<template>
  <q-layout view="hHh lpR fFf" class="bg-dark text-white">
    <q-header elevated class="text-white">
      <div class="header-content">
        <div class="greeting">
          <img src="/src/assets/padelplay.png" alt="Logo" class="logo-icon" />
        </div>
        <div class="header-icons">
          <q-btn flat round icon="close" @click="goBack" />
        </div>
      </div>
    </q-header>
    <q-page-container>
      <q-page class="q-pa-md">
        <q-card class="text-white">
          <q-card-section>
            <h3 class="text-white q-mt-none q-mb-md">Selecciona tu Método de Pago</h3>
          </q-card-section>

          <q-card-section class="q-pt-none">
            <div v-if="isLoadingMethods" class="text-center q-my-md">
               <q-spinner color="primary" size="sm" /> Cargando métodos...
            </div>
             <q-list bordered separator dark v-if="!isLoadingMethods && savedMethods.length > 0">
               <q-item-label header class="text-grey-5">Usar tarjeta guardada</q-item-label>
               <q-item v-for="method in savedMethods" :key="method.id" tag="label" v-ripple>
                 <q-item-section avatar top>
                   <q-radio v-model="selectedMethodId" :val="method.id" color="primary" />
                 </q-item-section>
                 <q-item-section avatar>
                    <q-icon :name="getBrandIcon(method.brand)" size="md" />
                 </q-item-section>
                 <q-item-section>
                   <q-item-label>{{ getBrandName(method.brand) }} terminada en {{ method.last4 }}</q-item-label>
                   <q-item-label caption class="text-grey-5">
                     Expira: {{ String(method.expMonth).padStart(2, '0') }}/{{ method.expYear }}
                   </q-item-label>
                 </q-item-section>
               </q-item>
            </q-list>

            <q-item tag="label" v-ripple class="q-mt-md" :class="{'bg-grey-9': selectedMethodId === 'new'}" >
                 <q-item-section avatar top>
                   <q-radio v-model="selectedMethodId" val="new" color="primary" />
                 </q-item-section>
                 <q-item-section>
                   <q-item-label>Usar nueva tarjeta</q-item-label>
                 </q-item-section>
            </q-item>
          </q-card-section>
           <q-card-section v-if="selectedMethodId === 'new'">
             <p class="text-caption text-grey-5 q-mb-sm">Introduce los datos de tu nueva tarjeta:</p>
            <div id="stripe-payment-element" class="stripe-payment-element-container">
               </div>
             <div v-if="paymentElementError" class="text-negative q-mt-sm text-caption">{{ paymentElementError }}</div>
             <div v-if="!isPaymentElementReady && selectedMethodId === 'new'" class="text-center q-pa-md">
                <q-spinner size="sm" color="primary"/> Cargando formulario...
             </div>
          </q-card-section>
           <q-card-section>
            <p class="text-h6 text-right q-mb-none">
                <strong>Total:</strong> ${{ amountToPay.toFixed(2) }}
            </p>
          </q-card-section>

          <q-card-actions align="right" class="q-pa-md">
            <q-btn
              :label="`PAGAR $${amountToPay.toFixed(2)}`"
              color="green"
              class="full-width"
              size="lg"
              push
              @click="confirmPayment"
              :loading="isProcessingPayment"
              :disable="!isReadyToPay" />
          </q-card-actions>
        </q-card>
      </q-page>
    </q-page-container>
  </q-layout>
</template>


<script>
import { ref, onMounted, computed, watch, shallowRef, nextTick } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useQuasar } from "quasar";
import { loadStripe } from "@stripe/stripe-js";
import { getBrandIcon, getBrandName  } from "src/helpers/paymentUtils";
import { finalizeCourtReservationUtil } from "src/helpers/reservationsUtils";
import api from "../services/api";

export default {
  name: "StripePayment",
  setup() {
    const route = useRoute();
    const router = useRouter();
    const $q = useQuasar();

    // --- NUEVA OBTENCIÓN DE DATOS ---
    const paymentOrderId = ref(route.query.paymentOrderId);
    const amountToPay = ref(parseFloat(route.query.amountToPay || '0'));
    const totalAmount = ref(parseFloat(route.query.totalAmount || '0'));
    const description = ref(route.query.description || 'Pago PadelPlay');
    const clubId = ref(route.query.clubId); // ID del club

    // Datos originales del resumen (pasados como JSON string)
    const baseData = computed(() => {
        try {
            return JSON.parse(route.query.baseData || '{}');
        } catch (e) {
            console.error("Error parsing baseData from query:", e);
            return {}; // Devuelve objeto vacío en caso de error
        }
    });
    const extraData = computed(() => {
         try {
            return JSON.parse(route.query.extraData || '{}');
        } catch (e) {
            console.error("Error parsing extraData from query:", e);
            return {};
        }
    });
    // Productos seleccionados (si aún los pasas y los necesitas)
     const selectedProducts = computed(() => {
         try {
            // Asume que OrderComponent lo sigue pasando si es necesario para la API final
            return JSON.parse(route.query.selectedProducts || '[]');
        } catch (e) {
            console.error("Error parsing selectedProducts from query:", e);
            return [];
        }
    });

    const stripe = ref(null);
    const paymentElement = ref(null); // Instancia específica del Payment Element
    const clientSecretRef = ref(null);
    const isProcessingPayment = ref(false);
    const isLoadingMethods = ref(false); // Carga de métodos guardados
    const savedMethods = ref([]); // Array para métodos guardados
    const selectedMethodId = ref('new'); // ID del método seleccionado ('new' o 'pm_...')
    const paymentElementError = ref(null); // Errores del PaymentElement
    const isPaymentElementReady = ref(false); // Indica si el elemento está montado y listo

    const elementsRef = ref(null);
    const cardElementRef = ref(null);
    const stripeInstance = shallowRef(null)
    const stripeLoadingError = ref(null)


    const isReadyToPay = computed(() => {
        if (!clientSecretRef.value) return false;
        if (selectedMethodId.value === 'new') {
            // If new card, elements group AND payment element must be ready
            return !!elementsRef.value?.elements && isPaymentElementReady.value; // Check elements.value too
        } else {
            // If saved card, just need the ID
            return !!selectedMethodId.value && selectedMethodId.value !== 'new';
        }
    });

    const fetchSavedMethods = async () => {
      isLoadingMethods.value = true;
      savedMethods.value = []; // Limpiar
      try {
        const response = await api.get('/payments/payment-methods'); // Tu endpoint
        savedMethods.value = response.data || [];
        // Si hay métodos guardados, seleccionar el primero por defecto
        if (savedMethods.value.length > 0) {
          selectedMethodId.value = savedMethods.value[0].id;
        } else {
          selectedMethodId.value = 'new'; // Si no hay, default a nueva tarjeta
        }
      } catch (error) {
        console.error("Error fetching saved payment methods:", error);
        selectedMethodId.value = 'new'; // Fallback a nueva tarjeta
        // No notificar necesariamente, puede que el usuario no tenga tarjetas
      } finally {
        isLoadingMethods.value = false;
      }
    };

    const getClientSecret = async (amount) => {
      try {
        // Usa el paymentOrderId y amountToPay obtenidos de la ruta
        if (!paymentOrderId.value || !amount || amount <= 0) {
             throw new Error("Falta ID de orden o el monto es inválido para crear PaymentIntent.");
        }
        const amountInCents = Math.round(amount * 100);
        const response = await api.post("payments/create-payment-intent", { // Endpoint para CREAR payment intent
          payment_order_id: paymentOrderId.value,
          amount: amountInCents,
          // Podrías enviar metadata aquí si tu backend lo necesita
          metadata: {
              item_type: baseData.value?.type,
              item_id: baseData.value?.id,
              description: description.value,
          }
        });
        console.log("Client Secret response:", response.data);
        if (!response.data?.clientSecret) {
            throw new Error("Respuesta inválida del servidor: No se recibió clientSecret.");
        }
        return response.data.clientSecret;
      } catch (error) {
        console.error("Error al obtener clientSecret:", error);
        $q.notify({ type: "negative", message: error.message || "Error al preparar el pago." });
        return null;
      }
    };


// --- Montar Payment Element (Modificado) ---
    const mountPaymentElement = () => {
        // Verificar Stripe y la referencia al componente Elements
        if (!stripeInstance.value || !elementsRef.value || selectedMethodId.value !== 'new' || !clientSecretRef.value) {
            isPaymentElementReady.value = false;
            if (paymentElement.value) { paymentElement.value.destroy(); paymentElement.value = null; }
            return;
        }

        // Obtener el grupo de Elements DESDE LA REFERENCIA del componente <StripeElements>
        const elementsGroup = elementsRef.value?.elements;
        if (!elementsGroup) {
            console.error("Fallo al obtener Elements group desde elementsRef.");
            paymentElementError.value = "Error al inicializar formulario (E-Group Ref).";
            isPaymentElementReady.value = false;
            return;
        }

        if (!paymentElement.value) {
            console.log("Montando Payment Element usando Elements group de ref...");
            try {
                // Crear el Payment Element usando el grupo de la ref
                paymentElement.value = elementsGroup.create("payment", { /* options */ });
                paymentElement.value.mount("#stripe-payment-element");
                isPaymentElementReady.value = false;
                paymentElementError.value = null;
                paymentElement.value.on('ready', () => {
                    console.log("Payment Element listo.");
                    isPaymentElementReady.value = true;
                });
                // Payment Element no tiene evento 'change' como CardElement, la validación es más implícita
                // Puedes escuchar 'change' en 'elementsGroup' si necesitas reaccionar a cambios generales
                // elementsGroup.on('change', (event) => { ... });
            } catch(error) {
                console.error("Error montando Payment Element:", error);
                paymentElementError.value = "Error al cargar formulario de tarjeta.";
                isPaymentElementReady.value = false;
            }
        }
    };

    // Inicializar Stripe y obtener datos iniciales
    const setup = async () => {
      isLoadingMethods.value = true; // Marcar carga inicial
      try {
        // Cargar Stripe.js
        stripe.value = await loadStripe(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY);
        if (!stripe.value) throw new Error("No se pudo cargar Stripe.js");

        // Cargar métodos guardados
        await fetchSavedMethods(); // Esto establece selectedMethodId

        // Obtener client secret (siempre necesario para confirmar)
        clientSecretRef.value = await getClientSecret(amountToPay.value);
        if (!clientSecretRef.value) throw new Error("No se pudo obtener la información de pago.");

        // Intentar montar el elemento si es necesario (si 'new' fue el default)
        await nextTick(); // Esperar a que el DOM se actualice con v-if
        mountPaymentElement();

      } catch (error) {
        console.error("Error en la configuración inicial de pago:", error);
        $q.notify({
          type: "negative",
          message: error.message || "Error al inicializar el pago. Intenta refrescar.",
          timeout: 0,
          actions: [{ label: 'Cerrar', handler: () => {} }]
        });
        // Podrías deshabilitar toda la página o redirigir
      } finally {
        isLoadingMethods.value = false; // Terminar carga inicial
      }
    };

    // Observador para montar/desmontar el elemento cuando cambia la selección
    watch(selectedMethodId, async (newValue) => {
        console.log("Método seleccionado cambiado a:", newValue);
        paymentElementError.value = null; // Limpiar errores
        await nextTick(); // Esperar al DOM
        if (newValue === 'new') {
            mountPaymentElement();
        } else {
            // Si se selecciona una tarjeta guardada, destruir el elemento si existe
            if (paymentElement.value) {
                console.log("Desmontando Payment Element...");
                paymentElement.value.destroy();
                paymentElement.value = null;
                isPaymentElementReady.value = false;
            }
        }
    });
    // Observador para montar elemento si clientSecret llega DESPUÉS de seleccionar 'new'
    watch(clientSecretRef, async (newSecret) => {
        if(newSecret && selectedMethodId.value === 'new') {
            await nextTick();
            mountPaymentElement();
        }
    });


    const confirmPayment = async () => {
      // Usar la instancia de Stripe cargada en onMounted
      const stripe = stripeInstance.value;
      // Obtener el grupo de Elements DESDE LA REFERENCIA del componente <StripeElements>
      const elementsGroup = elementsRef.value?.elements;

      if (!stripe || !clientSecretRef.value || !selectedMethodId.value) {
          $q.notify({ type: "negative", message: "Sistema de pago no inicializado correctamente." });
          return;
      }

      isProcessingPayment.value = true;
      $q.loading.show({ message: 'Procesando pago...' });
      paymentElementError.value = null;

      let error = null;
      let paymentIntent = null;

      try {
          if (selectedMethodId.value === 'new') {
              // --- Pagar con NUEVA tarjeta usando Payment Element ---
              // Verificar que el grupo de elements exista y que el botón esté habilitado (isReadyToPay)
              if (!elementsGroup || !isReadyToPay.value) {
                  throw new Error("El formulario de nueva tarjeta no está listo.");
              }
              console.log("Confirmando pago con Payment Element...");
              console.log("Stripe Instance:", stripe);
              console.log("Elements Group Instance:", elementsGroup); // <- Log del grupo correcto

              const result = await stripe.confirmPayment({
                  elements: elementsGroup, // <--- Pasar el grupo obtenido de la Ref
                  confirmParams: {
                      return_url: `${window.location.origin}/payment-complete`,
                  },
                  redirect: 'if_required',
              });
              error = result.error;
              paymentIntent = result.paymentIntent;

          } else {
              // --- Pagar con tarjeta GUARDADA (pm_...) usando confirmCardPayment ---
              console.log(`Confirmando pago con tarjeta guardada: ${selectedMethodId.value}`);
              const result = await stripe.confirmCardPayment(
                  clientSecretRef.value,
                  { payment_method: selectedMethodId.value }
                  // No necesita return_url aquí normalmente
              );
              error = result.error;
              paymentIntent = result.paymentIntent;
          }

          // --- Manejar Resultado ---
          if (error) {
              console.error("Error al confirmar el pago:", error);
              $q.notify({ type: "negative", message: `Error: ${error.message}` });
              if(selectedMethodId.value === 'new') paymentElementError.value = error.message;
          } else if (paymentIntent) {
              console.log("Resultado confirmación:", paymentIntent);
              await handlePaymentIntentStatus(paymentIntent); // Procesar estado
          } else if (!error && selectedMethodId.value !== 'new') {
              console.warn("Confirmación con tarjeta guardada no devolvió error ni paymentIntent.");
              $q.notify({type: 'warning', message: 'Estado de pago incierto. Verifica tus operaciones.'});
          }
          // Si hubo redirección, el código no llegará aquí.

      } catch (error) {
          console.error("Excepción durante confirmPayment:", error);
          $q.notify({ type: "negative", message: "Ocurrió un error inesperado durante el pago." });
      } finally {
          // Manejo cuidadoso del loading
          if (error || (paymentIntent && paymentIntent.status !== 'succeeded')) {
              $q.loading.hide();
              isProcessingPayment.value = false;
          } else if (!error && !paymentIntent && selectedMethodId.value !== 'new') {
                $q.loading.hide();
                isProcessingPayment.value = false;
          }
          // Si fue 'succeeded' o requiere acción/redirect, loading se maneja en otro lado
      }
    };

    const handleSuccessfulPayment = async (paymentIntent) => {
        console.log("Pago Exitoso! Procesando tipo:", baseData.value?.type, "con ID:", baseData.value?.id);
        $q.loading.show({ message: 'Confirmando reserva...' }); // Cambiar mensaje

        const context = {
          baseData: baseData.value,
          extraData: extraData.value,
          selectedProducts: selectedProducts.value,
          paymentOrderId: paymentOrderId.value,
          totalAmount: totalAmount.value,
          amountToPay: amountToPay.value
        };

        try {
            const type = baseData.value?.type;
            let result = { success: false };
            let redirectPath = '/dashboard/player'; // Ruta por defecto en caso de error o tipo desconocido

            if (type === 'court') {
                result = await finalizeCourtReservationUtil(paymentIntent, context, api, $q);
                if (result.success) {
                  redirectPath = result.path || `/player/match/${result.matchId}`; // Asume que devuelve matchId
                }
            } else if (type === 'class') {
                 const result = await finalizeClassBooking(paymentIntent);
                 success = result.success;
                 redirectPath = result.path || '/user/my-bookings'; // Ejemplo
            } else if (type === 'public_lesson') {
                 const result = await finalizePublicLessonEnrollment(paymentIntent);
                 success = result.success;
                 redirectPath = result.path || '/user/my-lessons'; // Ejemplo
            } else if (type === 'tournament') {
                 const result = await finalizeTournamentEnrollment(paymentIntent);
                 success = result.success;
                 // Asume que devuelve tournamentId en extraData o baseData
                 redirectPath = result.path || `/tournaments/${baseData.value?.id}`; // Ejemplo
            } else if (type === 'open_match_join') {
                 const result = await finalizeMatchJoin(paymentIntent);
                 success = result.success;
                 redirectPath = result.path || `/player/match/${baseData.value?.id}`; // ID del match
            } else {
                console.error(`Tipo de item desconocido: ${type}`);
                $q.notify({ type: 'negative', message: 'Error: Tipo de operación desconocida después del pago.' });
                success = false; // Marcar como no exitoso
                // No redirigir o redirigir a una página de error genérica
            }

            if (success) {
                $q.notify({ type: 'positive', message: '¡Operación completada con éxito!' });
                router.push(redirectPath); // Redirigir a la página correspondiente
            }
            // Si success es false, el error ya se notificó dentro de la función finalize...

        } catch (error) {
            // Error general al procesar post-pago
            console.error("Error procesando éxito del pago:", error);
            $q.notify({ type: "negative", message: "El pago fue exitoso, pero hubo un error al finalizar la operación." });
            // Considera redirigir a una página de 'Mis Reservas' o similar donde el usuario pueda verificar
            router.push('/user/dashboard'); // Ejemplo
        } finally {
            $q.loading.hide();
            isProcessingPayment.value = false;
        }
    };

    // --- NUEVO: Manejador de Estado del Payment Intent ---
    // Esta función se usará si confirmPayment resuelve SIN redirección,
    // o si se llama desde la página de retorno /payment-complete
    const handlePaymentIntentStatus = async (paymentIntent) => {
        switch (paymentIntent.status) {
            case 'succeeded':
                await handleSuccessfulPayment(paymentIntent);
                break;
            case 'processing':
                $q.notify({ type: 'info', message: 'El pago se está procesando. Te notificaremos cuando se complete.' });
                // Opcional: redirigir a una página de espera o dashboard
                 router.push('/user/dashboard');
                break;
            case 'requires_payment_method':
                 $q.notify({ type: 'warning', message: 'Pago fallido. Por favor, intenta con otro método de pago.' });
                 isProcessingPayment.value = false; // Permitir reintento
                 $q.loading.hide();
                break;
            default:
                 $q.notify({ type: 'negative', message: 'Algo salió mal con el pago.' });
                 isProcessingPayment.value = false;
                 $q.loading.hide();
                break;
        }
    };

    const finalizeClassBooking = async (paymentIntent) => {
         console.log("Finalizando reserva de clase privada...");
          try {
             const payload = { /* ... Construye payload para API /class-bookings ... */
                 club_id: baseData.value.clubId,
                 coach_id: baseData.value.id,
                 booking_date: extraData.value.date, // Pasado en extraData desde CoachDetails
                 booking_time: extraData.value.time, // Pasado en extraData
                 participants: baseData.value.participants,
                 price_paid: amountToPay.value, // El monto pagado
                 payment_order_id: paymentOrderId.value,
                 payment_intent_id: paymentIntent.id,
                 additional_items: selectedProducts.value,
             };
             console.log("Payload para /class-bookings:", payload);
             // const response = await api.post("/class-bookings", payload); // LLAMADA REAL
              // Simulación
              await new Promise(res => setTimeout(res, 1000));
              const response = { data: { booking_id: 'classbook123' } };

             console.log("Respuesta de API /class-bookings:", response.data);
             if (!response.data?.booking_id) throw new Error("La API no confirmó la reserva de clase.");
             return { success: true, path: '/user/my-bookings' }; // Ejemplo de ruta post-éxito
          } catch (error) {
               console.error("Error en finalizeClassBooking:", error);
               $q.notify({ type: 'negative', message: error.response?.data?.detail || error.message || "Error al confirmar la reserva de clase." });
              return { success: false };
          }
    };

    const finalizePublicLessonEnrollment = async (paymentIntent) => {
         console.log("Finalizando inscripción a clase pública...");
          try {
             const payload = { /* ... Construye payload para API /lesson-enrollments ... */
                lesson_id: baseData.value.id,
                club_id: baseData.value.clubId, // Podría obtenerse del lesson_id en backend
                price_paid: amountToPay.value,
                payment_order_id: paymentOrderId.value,
                payment_intent_id: paymentIntent.id,
                additional_items: selectedProducts.value,
                // user_id se obtiene del token en backend
             };
             console.log("Payload para /lesson-enrollments:", payload);
            //  const response = await api.post("/lesson-enrollments", payload); // LLAMADA REAL
             // Simulación
             await new Promise(res => setTimeout(res, 1000));
             const response = { data: { enrollment_id: 'lessonenroll123' } };

             console.log("Respuesta de API /lesson-enrollments:", response.data);
              if (!response.data?.enrollment_id) throw new Error("La API no confirmó la inscripción a la clase.");
             return { success: true, path: '/user/my-lessons' };
          } catch (error) {
              console.error("Error en finalizePublicLessonEnrollment:", error);
               $q.notify({ type: 'negative', message: error.response?.data?.detail || error.message || "Error al confirmar la inscripción a clase." });
              return { success: false };
          }
    };

     const finalizeTournamentEnrollment = async (paymentIntent) => {
         console.log("Finalizando inscripción a torneo...");
          try {
              const payload = { /* ... Construye payload para API /tournament-enrollments ... */
                tournament_id: baseData.value.id,
                price_paid: amountToPay.value, // La mitad pagada
                payment_order_id: paymentOrderId.value,
                payment_intent_id: paymentIntent.id,
                additional_items: selectedProducts.value,
                 // user_id se obtiene del token en backend
              };
             console.log("Payload para /tournament-enrollments:", payload);
            //  const response = await api.post("/tournament-enrollments", payload); // LLAMADA REAL
              // Simulación
             await new Promise(res => setTimeout(res, 1000));
             const response = { data: { enrollment_id: 'tournenroll123' } };

              console.log("Respuesta de API /tournament-enrollments:", response.data);
              if (!response.data?.enrollment_id) throw new Error("La API no confirmó la inscripción al torneo.");
              return { success: true, path: `/tournaments/${baseData.value.id}` }; // Volver al detalle del torneo
          } catch (error) {
               console.error("Error en finalizeTournamentEnrollment:", error);
               $q.notify({ type: 'negative', message: error.response?.data?.detail || error.message || "Error al confirmar la inscripción al torneo." });
              return { success: false };
          }
    };

     const finalizeMatchJoin = async (paymentIntent) => {
         console.log("Finalizando unión a partido...");
          try {
              const payload = { /* ... Construye payload para API /matches/{id}/join o similar ... */
                // match_id se usa en la URL del endpoint o se pasa en body
                team_number: extraData.value.teamToJoin,
                slot_index: extraData.value.slotIndex,
                price_paid: amountToPay.value,
                payment_order_id: paymentOrderId.value,
                payment_intent_id: paymentIntent.id,
                 // user_id se obtiene del token en backend
              };
              const matchId = baseData.value.id;
             console.log(`Payload para PATCH /matches/${matchId}/join:`, payload); // Asume endpoint PATCH
            //  const response = await api.patch(`/matches/${matchId}/join`, payload); // LLAMADA REAL
              // Simulación
             await new Promise(res => setTimeout(res, 1000));
             const response = { data: { success: true, /* match data? */ } }; // Backend debe confirmar

             console.log("Respuesta de API /matches/join:", response.data);
              if (!response.data?.success) throw new Error("La API no confirmó la unión al partido."); // O como sea que el backend confirme
             return { success: true, path: `/player/match/${matchId}` }; // Ir al detalle del partido
          } catch (error) {
              console.error("Error en finalizeMatchJoin:", error);
               $q.notify({ type: 'negative', message: error.response?.data?.detail || error.message || "Error al confirmar la unión al partido." });
              return { success: false };
          }
    };

    const goBack = () => {
      router.back()
    }

    onMounted(async () => {
    // Parsear datos de la ruta una vez
      let parsedBaseData = {}
      let parsedExtraData = {}
      let parsedSelectedProducts = []
      try {
          baseData.value = JSON.parse(route.query.baseData || '{}');
          extraData.value = JSON.parse(route.query.extraData || '{}');
          selectedProducts.value = JSON.parse(route.query.selectedProducts || '[]');
      } catch (e) {
          console.error("Error parsing data from route query:", e);
          $q.notify({ type: 'negative', message: 'Error al leer los datos de la orden.' });
          // Podrías redirigir o mostrar un estado de error permanente
          return;
      }
      console.log('Parsed baseData:', baseData.value);

      // Validar datos esenciales después de parsear
      if (!paymentOrderId.value || amountToPay.value <= 0 || !baseData.value?.type) {
          console.error("Faltan datos esenciales después de parsear o falta 'type' en baseData:", { query: route.query, baseData: baseData.value });
          $q.notify({ type: 'negative', message: 'Información de pago incompleta. Por favor, vuelve a intentarlo.', timeout: 0, actions: [{ label: 'Volver', handler: goBack }] });
          return;
      }

      await setup(); // Llamar a la función principal de configuración
    });

    return {
      amountToPay,
      confirmPayment,
      goBack,
      isProcessingPayment,
      savedMethods,
      selectedMethodId,
      isLoadingMethods,
      getBrandIcon,
      getBrandName,
      isReadyToPay,
      isPaymentElementReady,
      paymentElementError,
    };
  },
};
</script>

<style scoped>

.home {
      background-color: #dddddd;
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
  
.logo-icon {
    width: 60px; /* Ajusta el tamaño del logo */
    height: 60px;
  }

.q-card {
  background-image: url(src/assets/texturafondo.png);
  background-size: cover;
  max-width: 400px;
  margin: auto;
  color: #fff; /* Texto blanco para visibilidad */
  border-radius: 8px; /* Bordes redondeados */
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2); /* Sombra para destacar */
}

.text-primary {
  color: #4caf50; /* Verde primario */
}

.q-card-section {
  padding: 16px;
}

.q-item__section--avatar {
   min-width: 40px; /* Ajustar si los iconos/radio necesitan más espacio */
}
/* Hacer que el item seleccionado tenga un fondo diferente */
.q-item.bg-grey-9 {
   background-color: rgba(255, 255, 255, 0.1) !important;
}

</style>