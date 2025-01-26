<template>
  <q-layout view="hHh lpR fFf" class="bg-dark text-white">

    <q-header elevated class="text-white">
      <div class="header-content">
        <div class="greeting">
          <img src="/src/assets/padelplay.png" alt="Logo" class="logo-icon" />
        </div>

        <div class="header-icons">
          <NotificationBell />
          <PlayerTopMenu />
          </div>
      </div>
      <BannerPromoScrolling />
    </q-header>

    <q-page-container>
      <q-page class="q-pa-md">
        <q-card flat bordered class="text-white profile-card">
          <q-card-section class="q-pb-none relative">
            <q-btn flat round dense icon="query_stats" class="absolute-top-left" /> 
            <q-btn flat round dense icon="o_share" class="absolute-top-right" @click="shareProfile" /> 

            <div class="text-center"> 
              <q-avatar size="120px" class="q-my-md" @click="triggerFileUpload">
                <template v-if="player.photo_url">
                  <img :src="player.photo_url" alt="Foto del jugador" />
                </template>
                <template v-else>
                  <q-btn icon="person" flat dense size="70px" />
                </template>
              </q-avatar>
              
              <h4 class="q-ma-none">{{ player.first_name }}</h4> 
              <input
                type="file"
                ref="fileInput"
                class="hidden"
                @change="handleFileUpload"
              />
            </div>
          </q-card-section>

          <q-card-section class="q-pa-md text-center">  
            <q-list dense class="text-white">
              <q-item>
                  <q-item-label>Categoría: {{ player.category || "No especificado" }}</q-item-label>
              </q-item>

              <q-item>
                  <q-item-label>Fecha de nacimiento:  {{ formatDate(player.birth_date) }} </q-item-label>
              </q-item>

              <q-item>
                  <q-item-label>Género: {{ player.gender || "No especificado" }}</q-item-label>
              </q-item>

              <q-item>
                  <q-item-label>Mano preferida: {{ player.preferred_hand || "No especificado" }}</q-item-label>
              </q-item>

              <q-item>
                  <q-item-label>Posición en pista: {{ player.position || "No especificado" }}</q-item-label>
              </q-item>

            </q-list>
            <q-btn
              flat
              dense
              color="white"
              icon="o_edit"
              label="Editar"
              class="q-my-sm"
              stack
              @click="editProfile"
            />
          </q-card-section>
        </q-card>

        <q-card flat bordered class="text-white profile-card q-mt-md"> 
          <q-card-section class="q-pb-none">
            <div class="icon-buttons text-center"> 
              <q-btn
                flat
                dense
                color="white"
                icon="o_group"
                label="Comunidad"
                class="q-my-sm"
                stack
                @click="goToCommunity"
              />

              <q-btn
                flat
                dense
                color="white"
                icon="o_redeem"
                label="Recompensas"
                class="q-my-sm"
                stack
                @click="editProfile"
              />

              <q-btn
                flat
                dense
                color="white"
                icon="o_history"
                label="Historial"
                class="q-my-sm"
                stack
                @click="editProfile"
              />
            </div>
          </q-card-section>
        </q-card>
      </q-page>
    </q-page-container>
    <PlayerNavigationMenu />
  </q-layout>
</template>

<script>
import { ref, onMounted } from "vue";
import api from "../../api";
import { supabase } from "../../services/supabase";
import { useQuasar } from "quasar";
import PlayerNavigationMenu from "src/components/PlayerNavigationMenu.vue";
import PlayerTopMenu from "src/components/PlayerTopMenu.vue";
import NotificationBell from "src/components/NotificationBell.vue";
import BannerPromoScrolling from "src/components/BannerPromoScrolling.vue";

export default {
  components: {
    BannerPromoScrolling,
    NotificationBell,
    PlayerNavigationMenu,
    PlayerTopMenu,
  },

  data() {
    return {
      player: {
        first_name: "",
        last_name: "",
        birth_date: "",
        phone: "",
        gender: "",
        preferred_hand: "",
        position: "",
        photo_url: null,
        category: "sexta",
      },
      categories: ["primera", "segunda", "tercera", "cuarta", "quinta", "sexta", "profesional"],
    };
  },
  methods: {
    async fetchPlayer() {
      try {
        const { data, error } = await supabase.from("players").select("*").single();
        if (error) throw error;
        this.player = data;
      } catch (err) {
        console.error("Error al obtener datos del jugador:", err.message);
      }
    },
    formatDate(date) {
      if (!date) return "No especificado";
      const options = { year: "numeric", month: "long", day: "numeric" };
      return new Date(date).toLocaleDateString("es-MX", options);
    },
    editProfile() {
      this.$router.push("/player/editarinfo");
    },
    async shareProfile() {
      if (navigator.share) {
        try {
          await navigator.share({
            title: `Perfil de ${this.player.first_name}`,
            text: `Mira el perfil de ${this.player.first_name}, categoría ${this.player.category}.`,
            url: window.location.href,
          });
          console.log("Perfil compartido exitosamente");
        } catch (err) {
          console.error("Error al compartir el perfil:", err.message);
        }
      } else {
        alert("La funcionalidad de compartir no es compatible con este dispositivo.");
      }
    },
    triggerFileUpload() {
      this.$refs.fileInput.click(); // Simula el clic en el input de archivo
    },
    async handleFileUpload(event) {
      const file = event.target.files[0];
      if (file) {
        if (file.size > 2 * 1024 * 1024) {
          this.$q.notify({
            type: "negative",
            message: "El archivo es demasiado grande (máximo 2MB).",
          });
          return;
        }
        if (!file.type.startsWith("image/")) {
          this.$q.notify({
            type: "negative",
            message: "El archivo debe ser una imagen.",
          });
          return;
        }

        this.uploadPhoto(file);
      }
    },
    async uploadPhoto(file) {
      const formData = new FormData();
      formData.append("file", file);

      try {
        const response = await api.post("/players/upload-photo", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
            Authorization: `Bearer ${localStorage.getItem("token")}`, // Incluye el token
          },
        });

        this.player.photo_url = response.data.photo_url;

        this.$q.notify({
          type: "positive",
          message: "Foto de perfil actualizada exitosamente",
        });
      } catch (error) {
        console.error("Error al subir foto de perfil:", error.message);
        this.$q.notify({
          type: "negative",
          message: "Error al subir foto de perfil",
        });
      }
    },
    goBack() {
      this.$router.back();
    },
    goToCommunity() {
      this.$router.push("/player/community");
    },
  },
  mounted() {
    this.fetchPlayer();
  },
};
</script>

<style scoped>
  .q-list {
    margin-top: 20px;
  }
  .q-item-section {
    margin-bottom: 15px;
  }

  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 16px;
    background-color: #000000; /* Fondo del encabezado */
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
    max-width: 600px;
    margin: auto;
  }
  
  .q-item {
    color: white;
  }

  .profile-card {
    background-image: url(../../assets/texturafondo.png);
    background-size: cover;
    border-radius: 20px;
    margin-bottom: 10px;
  }

  .q-card-section.text-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  }

  .q-card-section.text-center h4 {
    margin-top: 0; 
  }

  .icon-buttons {
    display: flex;
    justify-content: center; 
    width: 100%;
    flex-wrap: wrap; 
    gap: 5px; 
  }

  .q-card-section.relative {
    position: relative; 
  }

  .absolute-top-left {
    position: absolute;
    top: 10px; 
    left: 10px; 
  }

  .absolute-top-right {
    position: absolute;
    top: 10px; 
    right: 10px; 
  }
</style>
  