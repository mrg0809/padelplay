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
            <q-btn flat round dense icon="o_share" class="absolute-top-right" /> 

            <div class="text-center"> 
              <q-avatar size="120px" class="q-my-md">
                <template v-if="player.photo_url">
                  <img :src="player.photo_url" alt="Foto del jugador" />
                </template>
                <template v-else>
                  <q-icon name="person" size="120px" />
                </template>
              </q-avatar>
              <h4 class="q-ma-none">{{ player.first_name }}</h4> 
            </div>
          </q-card-section>

          <q-card-section class="q-pa-md text-center">  
            <q-list dense class="text-white">
              <q-item>
                <q-item-section side>
                  <q-icon name="star" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Nivel o categoría</q-item-label>
                  <q-item-label caption>{{ player.category || "No especificado" }}</q-item-label>
                </q-item-section>
              </q-item>

              <q-item>
                <q-item-section side>
                  <q-icon name="cake" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Fecha de nacimiento</q-item-label>
                  <q-item-label caption>{{ formatDate(player.birth_date) }}</q-item-label>
                </q-item-section>
              </q-item>

              <q-item>
                <q-item-section side>
                  <q-icon name="transgender" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Género</q-item-label>
                  <q-item-label caption>{{ player.gender || "No especificado" }}</q-item-label>
                </q-item-section>
              </q-item>

              <q-item>
                <q-item-section side>
                  <q-icon name="sports_tennis" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Mano preferida</q-item-label>
                  <q-item-label caption>{{ player.preferred_hand || "No especificado" }}</q-item-label>
                </q-item-section>
              </q-item>

              <q-item>
                <q-item-section side>
                  <q-icon name="group_work" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Posición en pista</q-item-label>
                  <q-item-label caption>{{ player.position || "No especificado" }}</q-item-label>
                </q-item-section>
              </q-item>

            </q-list>
            <q-btn
              flat
              dense
              color="white"
              icon="edit"
              label="Editar"
              class="q-my-sm"
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
                @click="editProfile"
              />

              <q-btn
                flat
                dense
                color="white"
                icon="o_calendar_month"
                label="Eventos"
                class="q-my-sm"
                stack
                @click="editProfile"
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
    goBack() {
      this.$router.back();
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
  }
  
  .greeting {
    display: flex;
    align-items: center;
  }
  
  .logo-icon {
    width: 40px;
    height: 40px;
    margin-right: 10px;
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
  flex-wrap: wrap; 
  gap: 0px; 
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
  