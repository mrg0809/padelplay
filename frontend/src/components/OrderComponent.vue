<template>
    <q-layout view="hHh lpR fFf" class="bg-dark text-white">
      <q-header elevated class="text-white">
        <div class="header-content">
          <div class="greeting">
            <img src="/src/assets/padelplay.png" alt="Logo" class="logo-icon" />
          </div>
          <div class="header-icons">
            </div>
        </div>
        </q-header>
  
      <q-page-container class="home"> <q-page class="q-pa-md">
          <q-card class="text-white"> <q-card-section>
              <h3 class="text-white">{{ props.summaryTitle }}</h3>
            </q-card-section>
            <q-card-section>
              <p v-for="(detail, index) in props.itemDetails" :key="index">
                <strong>{{ detail.label }}:</strong> {{ detail.value }}
              </p>
              <q-separator dark spaced="sm" />
              <p><strong>Precio Base:</strong> ${{ props.baseData.price?.toFixed(2) || '0.00' }}</p>
                <div v-if="selectedProducts.length > 0">
                <p><strong>Adicionales:</strong> ${{ productTotal.toFixed(2) }}</p>
                <ul class="q-ml-md q-mb-sm" style="list-style-type: none; padding-left: 0;">
                    <li v-for="item in selectedProducts" :key="item.product.id" class="text-caption">
                       <q-icon name="mdi-cart-outline" size="xs" class="q-mr-xs"/> {{ item.product.name }} x {{ item.quantity }} - ${{ (item.product.price * item.quantity).toFixed(2) }}
                    </li>
                  </ul>
              </div>
              <p><strong>Subtotal:</strong> ${{ subtotalBeforeCommission.toFixed(2) }}</p>
              <p><strong>Comisión ({{ props.commissionRate }}%):</strong> ${{ commissionAmount.toFixed(2) }}</p>
              <q-separator dark spaced="sm" />
              <p class="text-h6">
                <strong>Total a pagar:</strong> ${{ total.toFixed(2) }}
                <q-icon name="o_info" size="sm" class="cursor-help q-ml-xs">
                    <q-tooltip anchor="top middle" self="bottom middle" :offset="[0, 10]" class="bg-grey-9 text-body2">
                    Precio total (Base + Adicionales + Comisión del {{ props.commissionRate }}%).
                    </q-tooltip>
                </q-icon>
              </p>
            </q-card-section>
  
            <q-card-section class="q-pt-none">
              <q-toggle
                v-if="props.showPublicToggle"
                v-model="isPublicMatch"
                checked-icon="check"
                color="green"
                label="Partido Público (otros podrán unirse)"
                class="q-mb-sm"
               />
  
              <q-option-group
                v-if="props.allowPaymentSplit && props.baseData.participants > 1"
                v-model="paymentOption"
                :options="paymentOptions"
                color="green"
                inline
                dense
              />
               <div v-else-if="props.baseData.participants > 1" class="text-caption q-mt-sm">
                  Nota: El pago es individual por participante.
               </div>
  
            </q-card-section>
  
            <q-card-actions align="right" class="q-pa-md">
              <q-btn icon="mdi-basket-plus-outline" label="Productos" color="primary" @click="showProductDialog" dense/>
              <q-btn
                :label="paymentButtonLabel"
                color="green"
                icon-right="mdi-credit-card-outline"
                @click="goToPayment"
                :loading="isProcessingPayment"
                padding="sm lg"
              />
            </q-card-actions>
          </q-card>
        </q-page>
      </q-page-container>
  


      <q-dialog v-model="productDialog">
         <q-card style="min-width: 300px; max-width: 400px" class="bg-grey-2 text-black">
            <q-card-section class="row items-center q-pb-none bg-primary text-white"> <div class="text-h6">Añadir Productos</div>
               <q-space />
               <q-btn icon="close" flat round dense v-close-popup />
            </q-card-section>

            <q-card-section style="max-height: 60vh; overflow-y: auto;"> <div v-if="isLoadingProducts" class="text-center q-pa-md">
                  <q-spinner-dots color="primary" size="40px" />
                  <div class="q-mt-sm">Cargando...</div>
              </div>
              <div v-else-if="!products || products.length === 0" class="text-grey-7 q-pa-md text-center">
                  No hay productos adicionales disponibles en este club.
              </div>
              <div v-else v-for="product in products" :key="product.id" class="q-mb-xs">
                <q-item dense>
                  <q-item-section>
                    <q-item-label class="text-weight-medium text-black">{{ product.name }}</q-item-label>
                    <q-item-label caption>${{ product.price.toFixed(2) }}</q-item-label>
                  </q-item-section>

                  <q-item-section side top>
                    <div class="row items-center no-wrap">
                      <q-btn
                        icon="mdi-minus"
                        color="negative"
                        round dense flat
                        size="sm"
                        @click="decreaseQuantity(product.id)"
                        :disable="!productQuantities[product.id] || productQuantities[product.id] <= 0"
                        class="q-mr-xs"
                       />
                       <span class="text-h6 text-black text-weight-bold q-mx-xs" style="min-width: 25px; text-align: center;">
                        {{ productQuantities[product.id] || 0 }}
                      </span>
                      <q-btn
                        icon="mdi-plus"
                        color="positive"
                        round dense flat
                        size="sm"
                        @click="increaseQuantity(product.id)"
                        class="q-ml-xs"
                       />
                    </div>
                  </q-item-section>
                  </q-item>
                 <q-separator spaced="xs" />
              </div>
            </q-card-section>

            <q-separator />

            <q-card-actions align="right" class="q-pa-md">
              <q-btn label="Cancelar" color="grey-7" flat v-close-popup />
              <q-btn label="Aceptar" color="primary" push @click="addProductToOrder" />
            </q-card-actions>
          </q-card>
      </q-dialog>
  
      <PlayerNavigationMenu />
    </q-layout>
  </template>
  
  <script setup>
  import { ref, computed, watch, reactive } from "vue";
  import { useRouter } from "vue-router";
  import { useQuasar, QSpinnerCube } from "quasar";
  import { getProductsByClub } from "src/services/supabase/products";
  import { useUserStore } from "src/stores/userStore";
  import api from "../services/api";
  import PlayerNavigationMenu from "src/components/PlayerNavigationMenu.vue";
  
  const props = defineProps({
    summaryTitle: { type: String, required: true, default: 'Resumen' },
    itemDetails: { type: Array, required: true, default: () => [] },
    baseData: { type: Object, required: true },
    commissionRate: { type: Number, default: 4 },
    showPublicToggle: { type: Boolean, default: false },
    allowPaymentSplit: { type: Boolean, default: false },
    extraData: { type: Object, default: () => ({}) }
  });
  
  // --- Inicialización ---
  const router = useRouter();
  const $q = useQuasar();
  const userStore = useUserStore();
  const products = ref([]);
  const productQuantities = reactive({}); 
  const selectedProducts = ref([]);
  const productDialog = ref(false);
  const isLoadingProducts = ref(false);
  const isPublicMatch = ref(false);
  const isProcessingPayment = ref(false);
  
  // Default paymentOption: si se permite split, default a 'partial', sino 'total'
  const paymentOption = ref(props.allowPaymentSplit && props.baseData?.participants > 1 ? 'partial' : 'total');
  
  // --- Computed Properties ---
  const subtotalBeforeCommission = computed(() => {
    const basePrice = props.baseData?.price || 0;
    return basePrice + productTotal.value;
    });

  const commissionAmount = computed(() => {
    return subtotalBeforeCommission.value * (props.commissionRate / 100);
    });
  
  const productTotal = computed(() => {
    return selectedProducts.value.reduce(
      (acc, item) => acc + item.product.price * item.quantity,
      0
    );
  });
  
  const total = computed(() => {
    return subtotalBeforeCommission.value + commissionAmount.value;
    });
  
  // Opciones dinámicas para el QOptionGroup
  const paymentOptions = computed(() => [
    { label: `Pagar mi parte (1/${props.baseData?.participants || 1})`, value: "partial" },
    { label: "Pagar el total", value: "total" },
  ]);
  
  // Label dinámico del botón de pago
  const paymentButtonLabel = computed(() => {
    const participants = props.baseData?.participants || 1;
    let amount = total.value;
    if (props.allowPaymentSplit && participants > 1 && paymentOption.value === "partial") {
      amount = total.value / participants;
    }
    return `Pagar $${amount.toFixed(2)}`;
  });
  
  // --- Métodos ---
  const loadProducts = async () => {
    if (!props.baseData?.clubId) {
      products.value = [];
      return;
    }
    isLoadingProducts.value = true;
    try {
      const clubProducts = await getProductsByClub(props.baseData.clubId);
      products.value = clubProducts || [];
      products.value.forEach(product => {
        if (productQuantities[product.id] === undefined) {
           productQuantities[product.id] = 0;
        }
      });
    } catch (error) {
      console.error("Error al cargar productos:", error);
      products.value = [];
      $q.notify({ type: 'warning', message: 'No se pudieron cargar los productos adicionales.' });
    } finally {
      isLoadingProducts.value = false;
    }
  };
  
  const showProductDialog = () => {
    if (products.value.length === 0 && props.baseData?.clubId) {
        loadProducts();
    } else {
         if (selectedProducts.value.length === 0) {
             products.value.forEach(p => { productQuantities[p.id] = 0 });
         }
    }
    productDialog.value = true;
  };
  
    const decreaseQuantity = (productId) => {
    if (productQuantities[productId] === undefined || productQuantities[productId] === null || isNaN(Number(productQuantities[productId]))) {
        productQuantities[productId] = 0;
    }

    const currentQuantity = Number(productQuantities[productId]);
    if (currentQuantity > 0) {
        productQuantities[productId] = currentQuantity - 1;
    }
    };

    const increaseQuantity = (productId) => {
    // Asegurarse de que la propiedad existe y es un número antes de operar
    if (productQuantities[productId] === undefined || productQuantities[productId] === null || isNaN(Number(productQuantities[productId]))) {
        productQuantities[productId] = 0; // Inicializar si es necesario
    }
    const currentQuantity = Number(productQuantities[productId]);
    // Podrías añadir un límite máximo si quisieras, ej: if (currentQuantity < 99)
    productQuantities[productId] = currentQuantity + 1;
    };
  
  
  const addProductToOrder = () => {
    selectedProducts.value = products.value
      .filter(product => productQuantities[product.id] && Number(productQuantities[product.id]) > 0)
      .map(product => ({
        product: { id: product.id, name: product.name, price: product.price },
        quantity: Number(productQuantities[product.id])
      }));
    productDialog.value = false;
  };
  
  const goToPayment = () => {
    // Go directly to MercadoPago payment processing
    processPayment('mercadopago');
  };
  
  const processPayment = async (paymentMethod) => {
    isProcessingPayment.value = true; // Start loading indicator
    $q.loading.show({ spinner: QSpinnerCube, message: 'Generando orden de pago...' });
    
    try {
      const participants = props.baseData?.participants || 1;
      let amountToPay = total.value;
      let payTotalFlag = true;
  
      if (props.allowPaymentSplit && participants > 1 && paymentOption.value === "partial") {
        amountToPay = total.value / participants;
        payTotalFlag = false;
      }
  
      const apiPayload = {
          total_price: total.value,
          pay_total: payTotalFlag,
          item_id: props.baseData?.id,
          item_type: props.baseData?.type,
          club_id: props.baseData?.clubId,
          recipient_id: props.baseData?.recipient_user_id,
          participants: participants,
          // Include selected products if backend needs them for the order
          products: selectedProducts.value.map(p => ({ id: p.product.id, quantity: p.quantity })),
          // Include isPublicMatch if applicable and backend needs it
          is_public: props.showPublicToggle ? isPublicMatch.value : undefined,
          // Include extraData if relevant for the backend
          // ...props.extraData
      };
  
      console.log("Enviando a API /payment_order_and_split_payment:", apiPayload);
  
      const responsePaymentOrder = await api.post("payments/payment_order_and_split_payment", apiPayload);
  
      const payment_order_id = responsePaymentOrder.data?.payment_order_id; // Use optional chaining
      if (!payment_order_id) {
        throw new Error("Respuesta inválida del servidor: No se recibió payment_order_id.");
      }
  
      // Navigate based on payment method selection
      if (paymentMethod === 'stripe') {
        // Navigate to StripePayment
        router.push({
          name: "StripePayment",
          query: {
            paymentOrderId: payment_order_id,
            amountToPay: amountToPay.toFixed(2),
            totalAmount: total.value.toFixed(2),
            description: props.summaryTitle,
            clubId: props.baseData?.clubId,
            baseData: JSON.stringify(props.baseData || {}),         
            extraData: JSON.stringify(props.extraData || {}),    
            selectedProducts: JSON.stringify(selectedProducts.value || []),
            itemDetails: JSON.stringify(props.itemDetails || []),
            paymentOption: paymentOption.value,
          },
        });
      } else if (paymentMethod === 'mercadopago') {
        // Navigate to MercadoPago payment flow
        const cartItems = [
          {
            id: props.baseData?.id || 'item_1',
            title: props.summaryTitle,
            quantity: 1,
            unit_price: amountToPay
          }
        ];

        // Get current user info from store
        const userInfo = {
          email: userStore.email || 'user@example.com',
          name: userStore.fullName || 'Usuario'
        };

        const paymentData = {
          cartItems: cartItems,
          userInfo: userInfo,
          externalReference: payment_order_id,
          metadata: {
            payment_order_id: payment_order_id,
            club_id: props.baseData?.clubId,
            item_type: props.baseData?.type,
            amount_to_pay: amountToPay,
            payment_option: paymentOption.value
          }
        };

        // Store payment data for MercadoPago page
        localStorage.setItem('mercadoPaymentData', JSON.stringify(paymentData));

        // Navigate to MercadoPago payment page
        router.push({ name: 'MercadoPayment' });
      }
    } catch (error) {
      console.error("Error en processPayment:", error);
      const errorMessage = error.response?.data?.message || error.message || 'Error al procesar el pago. Por favor intente de nuevo.';
      $q.notify({ type: "negative", message: errorMessage });
    } finally {
      isProcessingPayment.value = false; // Stop loading indicator
      $q.loading.hide();
    }
  };
  
  // --- Watchers ---
  watch(() => props.baseData?.clubId, (newClubId, oldClubId) => {
      if (newClubId && newClubId !== oldClubId) {
          // Resetear estado de productos si cambia el club
          products.value = [];
          selectedProducts.value = [];
          Object.keys(productQuantities).forEach(key => delete productQuantities[key]); // Limpiar cantidades
          loadProducts();
      }
  }, { immediate: true }); 
  

  watch(() => props.allowPaymentSplit, (allowSplit) => {
      if (!allowSplit) {
          paymentOption.value = 'total';
      } else if (props.baseData?.participants > 1) {
           paymentOption.value = 'partial';
      } else {
           paymentOption.value = 'total'; // Si solo hay 1 participante
      }
  }, { immediate: true });
  
  
  </script>
  
  <style scoped>

  .home {
     min-height: calc(100vh - 50px);
  }
  
  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 16px;
    background-color: #000000;
  }
  
  .greeting { display: flex; align-items: center; gap: 8px; }
  .header-icons { display: flex; gap: 2px; align-items: center; }
  .logo-icon { width: 60px; height: 60px; }
  
  .q-card {
    background-image: url(../assets/texturafondo.png);
    background-size: cover;
    background-position: center center;
    background-color: rgba(0, 0, 0, 0.6); 
    background-blend-mode: overlay; /* Mezclar fondo con imagen */
    max-width: 450px; 
    margin: 16px auto;
    color: #fff;
    border-radius: 8px;
    box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);
  }
  
  h3 { color: #FFF; margin-bottom: 1rem; font-weight: 500; }
  
  p { margin-bottom: 0.5rem; line-height: 1.5; }
  p strong { color: #b3e5fc; /* Un color resaltado para labels */ }
  
  .q-separator--dark { background: rgba(255, 255, 255, 0.3); }
  
  .text-h6 strong { font-weight: 600; }
  
  .q-dialog .q-card { /* Estilo específico para el diálogo de productos */
      background-image: none; /* Quitar imagen de fondo */
      background-color: #f5f5f5; /* Fondo claro para el diálogo */
      color: #333; /* Texto oscuro */
       max-width: 400px;
  }
  .q-dialog .q-item__label--caption { color: #666; }
  .q-dialog .q-separator { background: #e0e0e0; }
  
  /* Asegurar buen contraste en toggle/option group */
  .q-option-group .q-radio__label, .q-toggle__label {
      color: #fff; /* Asegurar que las etiquetas sean blancas */
  }
  
  </style>