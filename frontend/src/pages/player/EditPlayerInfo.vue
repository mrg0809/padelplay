<template>
  <q-layout view="hHh lpR fFf" class="bg-dark text-white">
    <!-- Encabezado -->
    <q-header elevated class="bg-primary text-white">
     
     <div class="header-content">
     <div class="greeting">
         <img src="/src/assets/padelplay.png" alt="Logo" class="logo-icon" />
       </div>
   <!-- Iconos de la derecha -->
       <div class="header-icons">
         <q-btn flat round icon="close" @click="goBack" />
       </div>
     </div>
   
 </q-header>

    <!-- Contenido Principal -->
    <q-page-container>
      <q-page padding>
        <div class="text-h6 text-center text-black q-mb-md">Editar Información del Jugador</div>
        <q-card flat bordered class="text-white global-card">
          <q-card-section>
            
          </q-card-section>

          <q-card-section>
            <q-form @submit.prevent="savePlayerInfo" class="form-container">
              <q-input v-model="playerInfo.first_name" label="Nombre" outlined dense class="q-mb-md" />
              <q-input v-model="playerInfo.last_name" label="Apellido" outlined dense class="q-mb-md" />
              <q-input v-model="playerInfo.birth_date" label="Fecha de Nacimiento" type="date" outlined dense class="q-mb-md" />
              <q-input v-model="playerInfo.phone" label="Teléfono" outlined dense class="q-mb-md" />

              <q-select
                v-model="playerInfo.gender"
                :options="['masculino', 'femenino', 'prefiero no decirlo']"
                label="Género"
                outlined
                dense
                class="q-mb-md"
              />

              <q-select
                v-model="playerInfo.preferred_hand"
                :options="['diestro', 'zurdo', 'ambas']"
                label="Mano Preferida"
                outlined
                dense
                class="q-mb-md"
              />

              <q-select
                v-model="playerInfo.position"
                :options="['reves', 'derecho', 'ambos lados']"
                label="Posición en Pista"
                outlined
                dense
                class="q-mb-md"
              />

              <q-select
                v-model="playerInfo.category"
                :options="['primera', 'segunda', 'tercera', 'cuarta', 'quinta', 'sexta', 'profesional']"
                label="Categoría"
                outlined
                dense
                class="q-mb-md"
              />


              
            </q-form>
            
          </q-card-section>
        </q-card>
        <q-btn type="submit" label="Guardar" color="primary" class="q-mt-md full-width" @click="savePlayerInfo" />
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script>
import api from "../../api";

export default {
  data() {
    return {
      playerInfo: {
        first_name: "",
        last_name: "",
        birth_date: "",
        phone: "",
        gender: null,
        preferred_hand: null,
        position: null,
        category: "sexta",
      },
    };
  },
  methods: {
    async fetchPlayerInfo() {
      try {
        const response = await api.get("/players/");
        this.playerInfo = response.data;
      } catch (error) {
        console.error("Error al obtener información del jugador:", error);
      }
    },
    async savePlayerInfo() {
      try {
        await api.put("/players/", this.playerInfo);
        this.$q.notify({ type: "positive", message: "Información actualizada con éxito" });
      } catch (error) {
        console.error("Error al guardar información del jugador:", error);
        this.$q.notify({ type: "negative", message: "Error al guardar información" });
      }
    },
    goBack() {
      this.$router.back();
    },
  },
  mounted() {
    this.fetchPlayerInfo();
  },
};
</script>

<style scoped>

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
    width: 60px;
    height: 60px;
  }

.form-container {
  display: flex;
  flex-direction: column;
}

.global-card {
  background-image: url(../../assets/texturafondo.png);
  background-size: cover;
  border-radius: 20px;
}

.q-mb-md {
  margin-bottom: 16px;
}
</style>
