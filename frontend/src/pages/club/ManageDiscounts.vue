<template>
    <q-layout view="hHh lpR fFf" class="bg-dark text-white">
      <q-header class="bg-primary text-white">
        <q-toolbar>
          <q-toolbar-title>Gestionar Promociones</q-toolbar-title>
          <q-btn flat round icon="arrow_back" @click="goBack" label="REGRESAR" />
        </q-toolbar>
      </q-header>
      <q-page-container>
        <q-page class="q-pa-md">
          <q-card dark class="q-pa-md bg-dark">
            <q-card-section>
              <h2 class="text-h5 text-white">Gestión de Descuentos y Promociones</h2>
            </q-card-section>
  
            <q-form @submit.prevent="submitDiscount">
              <q-card-section class="q-gutter-y-md"> 
                <q-select
                  v-model="form.type"
                  :options="discountTypes"
                  label="Tipo"
                  option-value="value"
                  option-label="label"
                  dense
                  outlined
                  dark
                  required
                  @update:model-value="resetInputs" 
                />

                <q-input
                  v-model="form.name" 
                  label="Nombre de promo"
                  type="text"
                  dense
                  outlined
                  dark
                  min="0"
                  required
                />
   
                <q-input
                  v-model.number="form.fixed_price" 
                  label="Precio Fijo"
                  type="number"
                  dense
                  outlined
                  dark
                  min="0"
                  required
                />
  
                <q-select
                ref="applicableDaysSelectRef"
                v-model="form.applicable_days"
                :options="daysOfWeek"
                label="Días Aplicables"
                multiple
                option-value="value"
                option-label="label"
                dense
                outlined
                dark
                use-chips 
                >
                <template v-slot:append>
                    <q-btn 
                    round 
                    dense 
                    flat 
                    icon="check" 
                    @click="closeSelect" 
                    />
                </template>
                </q-select>
  
                <q-select
                v-model="form.start_time"
                :options="timeOptions"
                label="Hora de Inicio"
                outlined
                dense
                dark
                required
                />

                <q-select
                v-model="form.end_time"
                :options="timeOptions"
                label="Hora de Fin"
                outlined
                dense
                dark
                required
                />
  
                <q-input
                  v-model="form.start_date"
                  label="Fecha de Inicio"
                  type="date"
                  dense
                  outlined
                  dark
                />
  
                <q-input
                  v-model="form.end_date"
                  label="Fecha de Fin"
                  type="date"
                  dense
                  outlined
                  dark
                />
  
                <q-input
                  v-model="form.description"
                  label="Descripción"
                  type="textarea"
                  dense
                  outlined
                  dark
                />
              </q-card-section>
  
              <q-card-actions align="right">
                <q-btn label="Guardar" type="submit" color="primary" />
              </q-card-actions>
            </q-form>
  
            <q-separator spaced />
  
            <q-card-section v-if="discounts.length">
              <h3 class="text-h6 text-white">Descuentos y Promociones Actuales</h3>
              <q-list dark>
                <q-item v-for="discount in discounts" :key="discount.id" clickable>
                  <q-item-section>
                    <q-item-label>{{ discount.name }}</q-item-label>
                    <q-item-label caption>
                      Tipo: {{ discount.type }} | Vigencia: {{ discount.start_date || 'Indefinido' }} -
                      {{ discount.end_date || 'Indefinido' }}
                    </q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </q-card-section>
          </q-card>
        </q-page>
      </q-page-container>
      <ClubNavigationMenu />
    </q-layout>
  </template>
  
  <script>
  import { onMounted, reactive, ref } from 'vue';
  import ClubNavigationMenu from 'src/components/ClubNavigationMenu.vue';
  import { useQuasar } from "quasar";
  import api from "../../api";
  
  export default {
    components: { ClubNavigationMenu },
    methods: {
      goBack() {
        this.$router.back();
      },
    },
    setup() {
      const $q = useQuasar();
      const form = reactive({
        club_id: null, // Agregar club_id al formulario
        type: null,
        discount_percentage: null,
        fixed_price: null,
        applicable_days: [],
        start_time: null,
        end_time: null,
        start_date: null,
        end_date: null,
        description: "",
      });
      const discounts = ref([]);
  
      const fetchDiscounts = async () => {
        try {
          const response = await api.get("/promo");
          discounts.value = response.data;
        } catch (error) {
          $q.notify({
            type: "negative",
            message: "Error al cargar los descuentos",
          });
        }
      };

      const fetchClubId = () => {
        const token = localStorage.getItem("token");
        if (token) {
            const base64Url = token.split(".")[1];
            const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
            const payload = JSON.parse(atob(base64));
            return payload.club_id;
        }
        return null; // Devuelve null si no se encuentra el club_id
        };
  
        const submitDiscount = async () => {
            try {
                // Validar y ajustar los datos del formulario
                form.club_id = fetchClubId(); // Obtener el club_id
                form.type = form.type.value; // Extraer el valor de 'type'
                form.applicable_days = form.applicable_days.map(day => day.value); // Extraer los valores numéricos

                // Llamada a la API
                await api.post("/promo", form);
                $q.notify({
                type: "positive",
                message: "Descuento o promoción creado exitosamente",
                });
                fetchDiscounts(); // Actualizar la lista de descuentos
                resetInputs(); // Restablecer los campos del formulario
            } catch (error) {
                console.error("Error en submitDiscount:", error.response || error);
                $q.notify({
                type: "negative",
                message: error.response?.data?.detail || "Error al guardar el descuento o promoción",
                });
            }
            };
  
      // Función para restablecer los campos del formulario
      const resetInputs = () => {
        form.discount_percentage = 0;
        form.fixed_price = 0;
        form.applicable_days = [];
        form.start_time = null;
        form.end_time = null;
        form.start_date = null;
        form.end_date = null;
        form.description = "";
      };
  
      onMounted(() => {
        fetchDiscounts();
      });
  
      const discountTypes = [
        { label: "Descuento", value: "discount" },
      ];
  
      const daysOfWeek = [
        { label: "Lunes", value: 1 },
        { label: "Martes", value: 2 },
        { label: "Miércoles", value: 3 },
        { label: "Jueves", value: 4 },
        { label: "Viernes", value: 5 },
        { label: "Sábado", value: 6 },
        { label: "Domingo", value: 0 },
      ];

      const timeOptions = Array.from({ length: 48 }, (_, index) => {
        const hours = Math.floor(index / 2);
        const minutes = index % 2 === 0 ? "00" : "30";
        return `${hours.toString().padStart(2, "0")}:${minutes}`;
        });
        
      const applicableDaysSelectRef = ref(null);

      const closeSelect = () => {
        if (applicableDaysSelectRef.value) {
            applicableDaysSelectRef.value.hidePopup();
        }
      };
  
  
      return {
        form,
        discounts,
        discountTypes,
        daysOfWeek,
        submitDiscount,
        resetInputs,
        timeOptions,
        applicableDaysSelectRef,
        closeSelect,
      };
    },
  };
  </script>
  
  <style scoped>
  .q-card {
    max-width: 600px;
    margin: auto;
  }
  </style>
  
  <style scoped>
  .q-card {
    max-width: 600px;
    margin: auto;
  }
  </style>
  