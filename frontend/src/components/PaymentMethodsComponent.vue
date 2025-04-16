<template>
    <q-page class="q-pa-md">

    <q-card>
      <q-card-section class="card-methods"> 
      <h4 class="q-mt-none q-mb-md text-white">Mis Métodos de Pago</h4>
  
      <q-list bordered separator v-if="!isLoadingMethods && savedMethods.length > 0">
        <q-item-label header class="text-grey-7">Tarjetas Guardadas</q-item-label>
        <q-item v-for="method in savedMethods" :key="method.id">
          <q-item-section avatar>
            <q-icon :name="getBrandIcon(method.brand)" size="lg" color="white" />
          </q-item-section>
          <q-item-section>
            <q-item-label>{{ getBrandName(method.brand) }} terminada en {{ method.last4 }}</q-item-label>
            <q-item-label caption>Expira: {{ String(method.expMonth).padStart(2, '0') }}/{{ method.expYear }}</q-item-label>
          </q-item-section>
          <q-item-section side>
            <q-btn icon="delete" color="negative" flat round dense @click="confirmDeleteMethod(method.id)" title="Eliminar tarjeta" />
          </q-item-section>
        </q-item>
      </q-list>
      <div v-if="!isLoadingMethods && savedMethods.length === 0 && !showAddCardForm" class="text-center text-grey q-pa-lg">
        <q-icon name="mdi-credit-card-off-outline" size="lg" />
        <p class="q-mt-sm">No tienes tarjetas guardadas.</p>
      </div>
      <div v-if="isLoadingMethods" class="text-center q-pa-lg">
        <q-spinner color="primary" size="md"/>
      </div>

        </q-card-section>
    </q-card>  
  
      <div class="q-mt-lg">
        <q-btn
          v-if="!showAddCardForm"
          label="Añadir Nueva Tarjeta"
          color="green"
          icon="add_card"
          @click="prepareAddCardForm" :loading="isLoadingClientSecret"
          push
        />
  
        <q-card flat bordered v-if="showAddCardForm" class="q-pa-md">
          <q-card-section class="q-pb-none">
            <div class="text-h6">Añadir Tarjeta</div>
          </q-card-section>
          <q-card-section>
            <div v-if="stripeKey && elementsClientSecret" class="stripe-elements-container">
              <StripeElements
                ref="elementsRef" :stripe-key="stripeKey"
                :instance-options="stripeInstanceOptions"
                :elements-options="elementsOptions"
              >
                <StripeElement
                  ref="cardElementRef" type="card"
                  :options="cardElementOptions"
                  @change="onCardElementChange"
                />
              </StripeElements>
               <div v-if="cardError" class="text-negative q-mt-sm text-caption">{{ cardError }}</div>
            </div>
             <div v-else-if="setupIntentError" class="text-negative q-pa-sm">
                  {{ setupIntentError }}
             </div>
             <div v-else class="text-center q-my-md">
                  <q-spinner color="primary" size="sm" />
                  Iniciando formulario seguro...
             </div>
          </q-card-section>
          <q-card-section v-if="addCardError" class="text-negative">
            {{ addCardError }}
          </q-card-section>
          <q-card-actions align="right">
            <q-btn label="Cancelar" flat color="grey" @click="cancelAddCard" />
            <q-btn
              label="Guardar Tarjeta"
              color="primary"
              @click="saveNewCard"
              :loading="isSavingCard || isLoadingClientSecret"
              :disable="isLoadingClientSecret || !elementsClientSecret || !cardElementComplete"
              push
            />
          </q-card-actions>
        </q-card>
      </div>
    </q-page>
  </template>
  
  <script setup>
  import { ref, onMounted, shallowRef, computed, nextTick } from 'vue';
  import { loadStripe } from '@stripe/stripe-js';
  import { StripeElements, StripeElement } from 'vue-stripe-js'; 
  import { useQuasar } from 'quasar';
  import { useUserStore } from 'src/stores/userStore';
  import api from 'src/services/api';
  
  // --- Configuración ---
  const $q = useQuasar();
  const userStore = useUserStore();
  const stripeKey = ref(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY); 
  
  // --- Estado ---
  const savedMethods = ref([]);
  const isLoadingMethods = ref(false);
  const showAddCardForm = ref(false);
  const elementsRef = ref(null);       
  const cardElementRef = ref(null);    
  const isSavingCard = ref(false);
  const isLoadingClientSecret = ref(false); // Nuevo estado para carga de clientSecret
  const addCardError = ref(null);
  const cardError = ref(null);
  const cardElementComplete = ref(false);
  const setupIntentError = ref(null); // Error al obtener client secret
  const elementsClientSecret = ref(null); // Para guardar el clientSecret obtenido

  const stripeInstance = shallowRef(null);
  const stripeLoadingError = ref(null); 
  
  const stripeInstanceOptions = ref({
      // Opciones de instancia de Stripe (locale, etc.)
      // locale: 'es'
  });
  const elementsOptions = computed(() => ({ 
      clientSecret: elementsClientSecret.value,
      appearance: { theme: 'night', labels: 'floating' }, 
  }));
  const cardElementOptions = ref({
    style: {
        base: {
            iconColor: '#c4f0ff',
            color: '#fff',
            fontWeight: '500',
            fontFamily: 'Roboto, Open Sans, Segoe UI, sans-serif',
            fontSize: '16px',
            fontSmoothing: 'antialiased',
            ':-webkit-autofill': { color: '#fce883' },
            '::placeholder': { color: '#87bbfd' },
         },
         invalid: {
            iconColor: '#ffc7ee', 
            color: '#ffc7ee',
         },
    },
    hidePostalCode: true,
    });
  
  // --- Métodos ---
  const fetchSavedMethods = async () => {
    isLoadingMethods.value = true;
    try {
        const response = await api.get('/payments/payment-methods'); 
        savedMethods.value = response.data || [];
    } catch (error) { /* ... manejo de error ... */ }
      finally { isLoadingMethods.value = false; }
    };
    const confirmDeleteMethod = (pmId) => {
        $q.dialog({
            title: 'Confirmar',
            message: '¿Estás seguro de que quieres eliminar esta tarjeta?',
            cancel: { label: 'Cancelar', flat: true },
            ok: { label: 'Eliminar', color: 'negative', push: true },
            persistent: true,
            dark: true,
            class: 'bg-black' 
        }).onOk(async () => {
            await deleteMethod(pmId);
        });
    }
    const deleteMethod = async (pmId) => {
        $q.loading.show({ message: 'Eliminando...' });
        try {
            await api.delete(`/payments/payment-methods/${pmId}`);
            $q.notify({ type: 'positive', message: 'Tarjeta eliminada correctamente.' });
            await fetchSavedMethods(); 
        } catch (error) {
            console.error("Error deleting payment method:", error);
            $q.notify({ type: 'negative', message: error.response?.data?.detail || 'Error al eliminar la tarjeta.' });
        } finally {
            $q.loading.hide();
        }
    };

    const getBrandIcon = (brand) => {
        const icons = {
            visa: 'img:/icons/visa.svg', 
            mastercard: 'img:/icons/mastercard.svg',
            amex: 'img:/icons/amex.svg',
            // ... otras marcas
        };
        return icons[brand] || 'mdi-credit-card'; 
    };

    const getBrandName = (brand) => {
        const names = {
            visa: 'Visa',
            mastercard: 'Mastercard',
            amex: 'American Express',
            // ...
        };
        return names[brand] || brand.charAt(0).toUpperCase() + brand.slice(1); 
    };

  const onCardElementChange = (event) => {
      cardElementComplete.value = event.complete;
      cardError.value = event.error ? event.error.message : null;
  };
  
  const cancelAddCard = () => {
      showAddCardForm.value = false;
      addCardError.value = null;
      cardError.value = null;
      setupIntentError.value = null;
      elementsClientSecret.value = null; // Limpiar secret
      cardElementComplete.value = false; // Resetear estado de completado
  };
  
  const prepareAddCardForm = async () => {
      isLoadingClientSecret.value = true;
      showAddCardForm.value = true; 
      setupIntentError.value = null; 
      elementsClientSecret.value = null; 
      cardElementComplete.value = false; 
    
  
      try {
          const response = await api.post('/payments/setup-intent');
          const clientSecret = response.data?.clientSecret;
          if (!clientSecret) {
               throw new Error("No se recibió la configuración de pago del servidor.");
          }
          // Guardar el clientSecret para que lo usen las options y la confirmación
          elementsClientSecret.value = clientSecret;
          console.log("Client Secret obtenido para SetupIntent");
  
          // Esperar a que Vue actualice el DOM y se renderice StripeElements con el nuevo secret
          await nextTick();
  
      } catch (error) {
          console.error("Error fetching client secret for SetupIntent:", error);
          setupIntentError.value = error.response?.data?.detail || error.message || "Error al iniciar el formulario de pago.";
          showAddCardForm.value = false; // Ocultar si falla la preparación
      } finally {
          isLoadingClientSecret.value = false;
      }
  };
  
  
  const saveNewCard = async () => {
    // Obtener instancia de Stripe desde la referencia de <StripeElements>
    const stripe = elementsRef.value?.instance;
    // Obtener instancia del elemento de tarjeta desde la referencia de <StripeElement>
    // La propiedad podría ser .stripeElement o .value dependiendo de la librería vue-stripe-js
    // Inspecciona cardElementRef.value en Vue DevTools si no estás seguro. Probemos con .stripeElement
    const cardElementInstance = cardElementRef.value?.stripeElement;

    // Validaciones
    if (!stripe || !cardElementInstance) {
        addCardError.value = "El formulario de pago no está listo (instancias no encontradas).";
        console.error("Error: Instancia de Stripe o CardElement no encontrada en refs. Verifica 'elementsRef' y 'cardElementRef'.", { stripeRef: elementsRef.value, cardRef: cardElementRef.value });
        return;
    }
    if (!cardElementComplete.value) {
        addCardError.value = "Por favor, completa los datos de la tarjeta.";
        return;
    }
    if (!elementsClientSecret.value) {
        addCardError.value = "Falta la configuración de pago (Client Secret).";
        return;
    }

    isSavingCard.value = true;
    addCardError.value = null;
    cardError.value = null;

    try {
        // --- USAR confirmCardSetup ---
        console.log("Llamando a confirmCardSetup con clientSecret:", elementsClientSecret.value);
        const { error, setupIntent } = await stripe.confirmCardSetup(
        elementsClientSecret.value, // 1. El clientSecret del SetupIntent
        {
            payment_method: {       // 2. Objeto payment_method
            card: cardElementInstance, // La instancia específica del Card Element
            billing_details: {    // Detalles de facturación
                name: userStore.userName || 'Nombre No Disponible', // Obtener de tu userStore
                email: userStore.userEmail || undefined,          // Obtener de tu userStore
            },
            },
            expand: ['payment_method'] // Opcional: para obtener datos del PM guardado en la respuesta
        }
        // Ya NO se pasa 'elements' ni 'confirmParams' con 'return_url' aquí
        );
        // --- FIN confirmCardSetup ---

        if (error) {
        // Manejar errores (tarjeta inválida, error de red, fallo de autenticación si no hubo redirect)
        console.error("Stripe confirmCardSetup error:", error);
        addCardError.value = error.message || "Ocurrió un error al guardar la tarjeta.";
        } else {
        // Si no hay error, verificar el estado del SetupIntent
        if (setupIntent.status === 'succeeded') {
            console.log("SetupIntent Succeeded:", setupIntent);
            const paymentMethod = setupIntent.payment_method;
            let brand = 'tarjeta';
            let last4 = '****';
            if (typeof paymentMethod === 'object' && paymentMethod?.card) {
                brand = paymentMethod.card.brand;
                last4 = paymentMethod.card.last4;
            }
            $q.notify({ type: 'positive', message: `Tarjeta ${getBrandName(brand)} terminada en ${last4} guardada.` });
            cancelAddCard(); 
            await fetchSavedMethods(); 
        } else if (setupIntent.status === 'requires_action') {
            console.warn("SetupIntent requires_action después de confirmCardSetup. Status:", setupIntent.status);
            addCardError.value = 'Se requiere autenticación adicional o la acción no se completó.';
        } else {
            // Otros estados posibles ('processing', etc.)
            console.warn("SetupIntent status:", setupIntent.status);
            addCardError.value = `El estado de la configuración fue: ${setupIntent.status}. Intenta de nuevo.`;
        }
        }
    } catch (error) {
        console.error("Error in saveNewCard function execution:", error);
        addCardError.value = error.response?.data?.detail || error.message || "Error inesperado al guardar la tarjeta.";
    } finally {
        isSavingCard.value = false;
    }
    };
  
  
  onMounted(() => {
    fetchSavedMethods();
  });
  
  </script>
  
  <style scoped>
  .stripe-elements-container {
      padding: 10px;
      border: 1px solid rgba(255, 255, 255, 0.3); /* Borde claro para visibilidad en modo oscuro */
      border-radius: 4px;
      background-color: rgba(0, 0, 0, 0.1); /* Fondo ligeramente diferente */
  }

  .card-methods {
    background-image: url("../assets/texturafondo.png");
    background-size: cover;
  }
  
  
  </style>