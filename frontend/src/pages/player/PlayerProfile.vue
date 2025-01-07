<template>
  <q-layout view="hHh lpR fFf" class="bg-dark text-white">
    <!-- Encabezado -->
    <q-header elevated class="bg-primary text-white">
      <q-toolbar>
        <q-toolbar-title>Perfil del Jugador</q-toolbar-title>
        <q-btn flat round icon="arrow_back" @click="goBack" label="REGRESAR" />
      </q-toolbar>
    </q-header>

    <!-- Contenido Principal -->
    <q-page-container>
      <q-page class="q-pa-md">
        <q-card flat bordered class="bg-dark text-white">
          <!-- Foto del jugador -->
          <q-card-section class="q-pb-none">
            <div class="text-center">
              <q-avatar size="120px" class="q-my-md">
                <template v-if="player.photo_url">
                  <img :src="player.photo_url" alt="Foto del jugador" />
                </template>
                <template v-else>
                  <q-icon name="person" size="70px" />
                </template>
              </q-avatar>
              <q-btn
                flat
                dense
                color="secondary"
                icon="edit"
                label="Editar información"
                class="q-my-sm"
                @click="editProfile"
              />
            </div>
          </q-card-section>

          <!-- Información del jugador -->
          <q-card-section>
            <q-list dense class="bg-dark text-white">
              <q-item>
                <q-item-section side>
                  <q-icon name="badge" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Nombre</q-item-label>
                  <q-item-label caption>{{ player.first_name }} {{ player.last_name }}</q-item-label>
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
                  <q-icon name="phone" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Teléfono</q-item-label>
                  <q-item-label caption>{{ player.phone || "No proporcionado" }}</q-item-label>
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

              <q-item>
                <q-item-section side>
                  <q-icon name="star" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Nivel o categoría</q-item-label>
                  <q-item-label caption>{{ player.category || "No especificado" }}</q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </q-card-section>
        </q-card>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script>
import { ref, onMounted } from "vue";
import { supabase } from "../../services/supabase";
import { useQuasar } from "quasar";

export default {
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
  </style>
  