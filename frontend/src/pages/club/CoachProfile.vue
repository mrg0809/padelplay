<template>
    <q-layout view="hHh lpR fFf" class="body text-white">
      <q-header elevated class="bg-primary text-white">
        <div class="header-content">
          <div class="greeting">
            <img src="/src/assets/padelplay.png" alt="Logo" class="logo-icon" />
            Perfil del Coach
          </div>
          <div class="header-icons">
            <q-btn flat round icon="arrow_back" @click="goBack" />
          </div>
        </div>
      </q-header>
  
      <q-page-container>
        <q-page class="q-pa-md">
          <div class="q-mb-md text-center">
            <!-- Foto centrada -->
            <q-avatar size="200px" class="q-mb-md">
              <img :src="coach.photo_url || 'default-avatar.png'" />
            </q-avatar>
            <!-- Nombre y enfoque -->
            <div class="text-h5">{{ coach.name }}</div>
            <div class="text-caption text-white">{{ coach.coach_focus }}</div>
          </div>
  
          <!-- Pestañas -->
          <q-tabs v-model="tab" align="justify" class="bg-black text-white">
            <q-tab name="info" label="Información" />
            <q-tab name="prices" label="Precios" />
            <q-tab name="availability" label="Disponibilidad" />
          </q-tabs>
  
          <!-- Contenido de las pestañas -->
          <q-tab-panels v-model="tab" animated class="bg-black">
            <!-- Pestaña de Información -->
            <q-tab-panel name="info">
              <q-card class="bg-transparent">
                <q-card-section>
                  <q-item-label class="text-bold">Resumen:</q-item-label>
                  <q-item-label>{{ coach.resume }}</q-item-label>
                </q-card-section>
                <q-card-section>
                  <q-item-label class="text-bold">Categoría Jugador:</q-item-label>
                  <q-item-label>{{ coach.category }}</q-item-label>
                </q-card-section>
                <q-card-section>
                  <q-item-label class="text-bold">Género:</q-item-label>
                  <q-item-label>{{ coach.gender }}</q-item-label>
                </q-card-section>
                <q-card-actions align="right">
                  <q-btn color="primary" label="Editar" @click="openEditInfoDialog" />
                </q-card-actions>
              </q-card>
            </q-tab-panel>
  
            <!-- Pestaña de Precios -->
            <q-tab-panel name="prices">
              <q-card class="bg-transparent">
                <q-card-section>
                  <q-item-label class="text-bold">Individual:</q-item-label>
                  <q-item-label>$ {{ coach.price_for_one }}</q-item-label>
                </q-card-section>
                <q-card-section>
                  <q-item-label class="text-bold">Pareja:</q-item-label>
                  <q-item-label>$ {{ coach.price_for_two }}</q-item-label>
                </q-card-section>
                <q-card-section>
                  <q-item-label class="text-bold">3 personas:</q-item-label>
                  <q-item-label>$ {{ coach.price_for_three }}</q-item-label>
                </q-card-section>
                <q-card-section>
                  <q-item-label class="text-bold">4 personas:</q-item-label>
                  <q-item-label>$ {{ coach.price_for_four }}</q-item-label>
                </q-card-section>
                <q-card-actions align="right">
                  <q-btn color="primary" label="Editar" @click="openEditPricesDialog" />
                </q-card-actions>
              </q-card>
            </q-tab-panel>
  
            <!-- Pestaña de Disponibilidad -->
            <q-tab-panel name="availability">
              <q-card class="bg-transparent">
                <q-card-section>
                  <q-list bordered>
                    <q-item v-for="(schedule, index) in coach.schedule" :key="index" class="q-mb-md">
                      <q-item-section>
                        <div class="text-bold">{{ schedule.day }}</div>
                        <q-item-label v-if="schedule.start_time && schedule.end_time">
                          {{ schedule.start_time }} - {{ schedule.end_time }}
                        </q-item-label>
                        <q-item-label v-else>
                          No disponible
                        </q-item-label>
                      </q-item-section>
                    </q-item>
                  </q-list>
                </q-card-section>
                <q-card-actions align="right">
                  <q-btn color="primary" label="Editar" @click="openEditAvailabilityDialog" />
                </q-card-actions>
              </q-card>
            </q-tab-panel>
          </q-tab-panels>
        </q-page>
      </q-page-container>
  
      <!-- Diálogo para editar información -->
      <q-dialog v-model="isEditInfoDialogOpen">
        <q-card class="bg-black text-white">
          <q-card-section>
            <div class="text-h6">Editar Información</div>
          </q-card-section>
          <q-card-section>
            <q-input v-model="editInfoData.resume" label="Resumen" filled type="textarea" />
            <q-input v-model="editInfoData.focus" label="Enfoque" filled type="textarea" />
          </q-card-section>
          <q-card-actions align="right">
            <q-btn flat label="Cancelar" color="red" v-close-popup />
            <q-btn flat label="Guardar" color="green" @click="saveInfo" />
          </q-card-actions>
        </q-card>
      </q-dialog>
  
      <!-- Diálogo para editar precios -->
      <q-dialog v-model="isEditPricesDialogOpen">
        <q-card class="bg-black text-white">
          <q-card-section>
            <div class="text-h6">Editar Precios</div>
          </q-card-section>
          <q-card-section>
            <q-input v-model="editPricesData.price_for_one" label="Individual" filled type="number" />
            <q-input v-model="editPricesData.price_for_two" label="Pareja" filled type="number" />
            <q-input v-model="editPricesData.price_for_three" label="3 personas" filled type="number" />
            <q-input v-model="editPricesData.price_for_four" label="4 personas" filled type="number" />
          </q-card-section>
          <q-card-actions align="right">
            <q-btn flat label="Cancelar" color="red" v-close-popup />
            <q-btn flat label="Guardar" color="green" @click="savePrices" />
          </q-card-actions>
        </q-card>
      </q-dialog>
  
      <!-- Diálogo para editar disponibilidad -->
      <q-dialog v-model="isEditAvailabilityDialogOpen">
        <q-card class="bg-black text-white">
          <q-card-section>
            <div class="text-h6">Editar Disponibilidad</div>
          </q-card-section>
          <q-card-section>
            <q-list bordered>
              <q-item v-for="(schedule, index) in editAvailabilityData" :key="index" class="q-mb-md">
                <q-item-section>
                  <div class="text-bold">{{ schedule.day }}</div>
                  <q-toggle v-model="schedule.is_open" label="¿Disponible?" dense color="primary" />
                </q-item-section>
                <q-item-section v-if="schedule.is_open">
                  <q-input v-model="schedule.start_time" label="Hora de inicio" filled mask="time" :rules="['time']" />
                  <q-input v-model="schedule.end_time" label="Hora de fin" filled mask="time" :rules="['time']" />
                </q-item-section>
              </q-item>
            </q-list>
          </q-card-section>
          <q-card-actions align="right">
            <q-btn flat label="Cancelar" color="red" v-close-popup />
            <q-btn flat label="Guardar" color="green" @click="saveAvailability" />
          </q-card-actions>
        </q-card>
      </q-dialog>
  
      <ClubNavigationMenu />
    </q-layout>
  </template>
  
  <script>
  import { ref, onMounted } from "vue";
  import { useRoute, useRouter } from "vue-router";
  import ClubNavigationMenu from "src/components/ClubNavigationMenu.vue";
  import api from "../../services/api"; 
  import { supabase } from "src/services/supabase";
  
  export default {
    name: "CoachProfile",
    components: {
      ClubNavigationMenu,
    },
    setup() {
      const router = useRouter();
      const route = useRoute();
      const tab = ref("info"); // Pestaña activa por defecto
      const coach = ref({
        id: null,
        name: "",
        photo_url: "",
        coach_focus: "",
        resume: "",
        focus: "",
        category: "",
        gender: "",
        price_for_one: null,
        price_for_two: null,
        price_for_three: null,
        price_for_four: null,
        schedule: [],
      });
  
      // Diálogos
      const isEditInfoDialogOpen = ref(false);
      const isEditPricesDialogOpen = ref(false);
      const isEditAvailabilityDialogOpen = ref(false);
  
      // Datos para editar
      const editInfoData = ref({
        resume: "",
        focus: "",
      });
  
      const editPricesData = ref({
        price_for_one: null,
        price_for_two: null,
        price_for_three: null,
        price_for_four: null,
      });
  
      const editAvailabilityData = ref([]);
  
      // Días de la semana
      const daysOfWeek = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"];
  
      // Función para obtener los datos del coach
      const fetchCoachData = async () => {
        const coachId = route.params.id;
        try {
          const { data, error } = await supabase
            .from("coaches")
            .select(`
              id, 
              name,
              price_for_one,
              price_for_two,
              price_for_three,
              price_for_four,
              coach_resume,
              coach_focus,
              availability, 
              players(gender, photo_url, category)
            `)
            .eq("id", coachId)
            .single();
  
          if (error) throw error;
  
          coach.value = {
            id: data.id,
            name: data.name,
            photo_url: data.players.photo_url,
            coach_focus: data.coach_focus,
            resume: data.coach_resume,
            focus: data.coach_focus,
            category: data.players.category,
            gender: data.players.gender,
            price_for_one: data.price_for_one,
            price_for_two: data.price_for_two,
            price_for_three: data.price_for_three,
            price_for_four: data.price_for_four,
            schedule: data.availability || [],
          };
  
          // Inicializar datos de edición
          editInfoData.value = {
            resume: data.coach_resume,
            focus: data.coach_focus,
          };
  
          editPricesData.value = {
            price_for_one: data.price_for_one,
            price_for_two: data.price_for_two,
            price_for_three: data.price_for_three,
            price_for_four: data.price_for_four,
          };
  
          // Inicializar disponibilidad con todos los días de la semana
          editAvailabilityData.value = daysOfWeek.map((day) => {
            const existingSchedule = data.availability.find((s) => s.day === day);
            return existingSchedule || { day, is_open: false, start_time: "", end_time: "" };
          });
        } catch (err) {
          console.error("Error obteniendo datos del coach:", err.message);
        }
      };
  
      // Función para abrir el diálogo de edición de información
      const openEditInfoDialog = () => {
        editInfoData.value = {
          resume: coach.value.resume,
          focus: coach.value.focus,
        };
        isEditInfoDialogOpen.value = true;
      };
  
      // Función para abrir el diálogo de edición de precios
      const openEditPricesDialog = () => {
        editPricesData.value = {
          price_for_one: coach.value.price_for_one,
          price_for_two: coach.value.price_for_two,
          price_for_three: coach.value.price_for_three,
          price_for_four: coach.value.price_for_four,
        };
        isEditPricesDialogOpen.value = true;
      };
  
      // Función para abrir el diálogo de edición de disponibilidad
      const openEditAvailabilityDialog = () => {
        editAvailabilityData.value = daysOfWeek.map((day) => {
          const existingSchedule = coach.value.schedule.find((s) => s.day === day);
          return existingSchedule || { day, is_open: false, start_time: "", end_time: "" };
        });
        isEditAvailabilityDialogOpen.value = true;
      };
  
      // Función para guardar la información editada
      const saveInfo = async () => {
        try {
          const response = await api.put(`coaches/edit-info/${coach.value.id}`, {
            coach_resume: editInfoData.value.resume,
            coach_focus: editInfoData.value.focus,
          });
  
          if (response.data) {
            coach.value.resume = editInfoData.value.resume;
            coach.value.focus = editInfoData.value.focus;
            isEditInfoDialogOpen.value = false;
          }
        } catch (err) {
          console.error("Error actualizando información:", err.message);
        }
      };
  
      // Función para guardar los precios editados
      const savePrices = async () => {
        try {
          const response = await api.put(`coaches/edit-prices/${coach.value.id}`, {
            price_for_one: editPricesData.value.price_for_one,
            price_for_two: editPricesData.value.price_for_two,
            price_for_three: editPricesData.value.price_for_three,
            price_for_four: editPricesData.value.price_for_four,
          });
  
          if (response.data) {
            coach.value.price_for_one = editPricesData.value.price_for_one;
            coach.value.price_for_two = editPricesData.value.price_for_two;
            coach.value.price_for_three = editPricesData.value.price_for_three;
            coach.value.price_for_four = editPricesData.value.price_for_four;
            isEditPricesDialogOpen.value = false;
          }
        } catch (err) {
          console.error("Error actualizando precios:", err.message);
        }
      };
  
      // Función para guardar la disponibilidad editada
      const saveAvailability = async () => {
        try {
          const availability = editAvailabilityData.value
            .filter((s) => s.is_open)
            .map((s) => ({ day: s.day, start_time: s.start_time, end_time: s.end_time }));
  
          const response = await api.put(`coaches/edit-availability/${coach.value.id}`, {
            availability,
          });
  
          if (response.data) {
            coach.value.schedule = availability;
            isEditAvailabilityDialogOpen.value = false;
          }
        } catch (err) {
          console.error("Error actualizando disponibilidad:", err.message);
        }
      };
  
      // Función para regresar
      const goBack = () => {
        router.back();
      };
  
      onMounted(fetchCoachData);
  
      return {
        coach,
        tab,
        isEditInfoDialogOpen,
        isEditPricesDialogOpen,
        isEditAvailabilityDialogOpen,
        editInfoData,
        editPricesData,
        editAvailabilityData,
        openEditInfoDialog,
        openEditPricesDialog,
        openEditAvailabilityDialog,
        saveInfo,
        savePrices,
        saveAvailability,
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
  </style>