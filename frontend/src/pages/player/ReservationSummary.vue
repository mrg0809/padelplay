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
  
      <q-page-container>
        <q-page class="q-pa-md">
          <q-card class="text-white">
            <q-card-section>
              <h3 class="text-white">Resumen de Reserva</h3>
            </q-card-section>
            <q-card-section>
              <p><strong>Club:</strong> {{ reservationDetails.clubName }}</p>
              <p><strong>Cancha:</strong> {{ reservationDetails.courtName }}</p>
              <p><strong>Fecha:</strong> {{ reservationDetails.date }}</p>
              <p><strong>Horario:</strong> {{ reservationDetails.time }} hrs.</p>
              <p><strong>Duración:</strong> {{ reservationDetails.duration }} minutos</p>
              <p><strong>Precio:</strong> ${{ reservationDetails.price.toFixed(2) }}</p>
              <p><strong>Subtotal:</strong> ${{ subtotal.toFixed(2) }}</p>
              <p><strong>Adicionales:</strong> ${{ productTotal }}</p>
              <ul class="q-ml-lg">
                <li v-for="item in selectedProducts" :key="item.product.id">
                  {{ item.product.name }} x {{ item.quantity }} - ${{ (item.product.price * item.quantity).toFixed(2) }}
                </li>
              </ul>
              <p>
                <strong>Total a pagar:</strong> ${{ total.toFixed(2) }}
                <q-icon name="o_info" size="xs" class="cursor-help">
                    <q-tooltip anchor="top middle" self="bottom middle" :offset="[0, 10]">
                    Precio total con impuestos y comisiones incluidas
                    </q-tooltip>
                </q-icon>
              </p>
            </q-card-section>
  
            <q-card-section>
              <q-toggle 
              v-model="isPublicMatch"
              checked-icon="check"
              color="green"
              label="Partido Público" />
              <q-option-group
              v-model="paymentOption"
              color="green"
              :options="paymentOptions" />
            </q-card-section>
  
            <q-card-actions align="right">
              <q-btn label="Agregar Productos" color="primary" @click="showProductDialog" />
              <q-btn 
                :label="paymentButtonLabel"
                color="green" 
                @click="goToPayment" 
              />  
            </q-card-actions>
          </q-card>
        </q-page>
      </q-page-container>
  
      <q-dialog v-model="productDialog">
        <q-card>
          <q-card-section>
            <div v-for="product in products" :key="product.id" class="q-mb-md">
              <q-item>
                <q-item-section>
                  <q-item-label>{{ product.name }} - ${{ product.price.toFixed(2) }}</q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-input v-model="productQuantities[product.id]" type="number" min="0" />
                </q-item-section>
              </q-item>
            </div>
          </q-card-section>
          <q-card-actions align="right">
            <q-btn label="Aceptar" color="primary" @click="addProductToOrder" />
            <q-btn label="Cancelar" color="grey-dark" v-close-popup />
          </q-card-actions>
        </q-card>
      </q-dialog>
      <PlayerNavigationMenu />
    </q-layout>
  </template>
  
  <script>
  import { ref, computed, onMounted } from "vue";
  import { useRoute, useRouter } from "vue-router";
  import { useQuasar } from "quasar";
  import { getProductsByClub } from "src/services/supabase/products";
  import api from "../../services/api";
  import PlayerNavigationMenu from "src/components/PlayerNavigationMenu.vue";
  
  export default {
    components: {
      PlayerNavigationMenu,
    },
    setup() {
      const route = useRoute();
      const router = useRouter();
      const $q = useQuasar();
  
      const reservationDetails = ref({
        clubId: route.query.clubId || "",
        clubName: route.query.clubName || "Club no especificado",
        courtId: route.query.courtId || "",
        courtName: route.query.courtName || "Cancha no especificada",
        date: route.query.date || "Fecha no especificada",
        time: route.query.time || "Hora no especificada",
        duration: route.query.duration || 0,
        price: parseFloat(route.query.price) || 0,
      });
  
      const commission = ref(4);
      const subtotal = ref(reservationDetails.value.price + (commission.value * reservationDetails.value.price) / 100);
  
      const products = ref();
      const productQuantities = ref({});
      const selectedProducts = ref([]);
      const productDialog = ref(false);
      const isPublicMatch = ref(false);
      const paymentOption = ref("partial");
      const paymentOptions = ref([
        { label: "Pagar mi parte", value: "partial" },
        { label: "Pagar el total", value: "total" },
      ]);
      const paymentButtonLabel = computed(() => {
        const amount = paymentOption.value === "total" ? total.value.toFixed(2) : (total.value / 4).toFixed(2);
        return `Continuar al pago de $${amount}`;
        });

      const productTotal = computed(() => { // Agregamos el computed property
      if (selectedProducts.value && Array.isArray(selectedProducts.value)) {
        return selectedProducts.value.reduce(
          (acc, item) => acc + item.product.price * item.quantity,
          0
        );
      }
      return 0; // Retorna 0 si no hay productos
    })

      const total = computed(() => {
        return subtotal.value + productTotal.value;
      });
  
      const showProductDialog = () => {
        productDialog.value = true;
      };
  
      const addProductToOrder = () => {
        selectedProducts.value = products.value.filter(product => productQuantities.value[product.id] > 0).map(product => ({
          product: product,
          quantity: productQuantities.value[product.id]
        }));
        productDialog.value = false;
      };
  
      const goToPayment = async () => {
        try {
          const amount = paymentOption.value === "total" ? total.value : total.value / 4;
          const responsePaymentOrder = await api.post("payments/payment_order_and_split_payment", {
            total_price: total.value,
            pay_total: paymentOption.value === "total",
          });

          const payment_order_id = responsePaymentOrder.data.payment_order_id;

          router.push({
            name: "StripePayment",
            query: {
              reservationDetails: JSON.stringify({
                ...reservationDetails.value,
                payment_order_id: payment_order_id,
              }),
              total: total.value,
              paymentOption: paymentOption.value,
              selectedProducts: JSON.stringify(selectedProducts.value),
              isPublicMatch: isPublicMatch.value,
              amountToPay: amount,
            },
          });
        } catch (error) {
          console.error("Error al obtener payment_order:", error);
          $q.notify({
            type: "negative",
            message: "Error al generar orden de pago. Por favor intente de nuevo.",
          });
        }
      };
  
      onMounted(async () => {
        products.value = await getProductsByClub(reservationDetails.value.clubId);
        products.value.forEach(product => productQuantities.value[product.id] = 0);
      });
  
      return {
        reservationDetails,
        commission,
        subtotal,
        products,
        productQuantities,
        selectedProducts,
        productDialog,
        isPublicMatch,
        paymentOption,
        paymentOptions,
        total,
        showProductDialog,
        addProductToOrder,
        goToPayment,
        productTotal,
        paymentButtonLabel,
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
  background-image: url(../../assets/texturafondo.png);
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
</style>