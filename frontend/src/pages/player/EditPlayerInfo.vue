<template>
    <q-layout view="hHh lpR fFf" class="bg-dark text-white">
        <q-header elevated class="bg-primary text-white">
        <q-toolbar>
          <q-toolbar-title>Perfil del Jugador</q-toolbar-title>
          <q-btn flat round icon="arrow_back" @click="goBack" label="REGRESAR" />
        </q-toolbar>
      </q-header>
        <q-page-container>
        <q-page padding>
        <q-card>
            <q-card-section>
            <div class="text-h6">Editar Información del Jugador</div>
            <q-btn flat round icon="arrow_back" @click="goBack" label="REGRESAR" />
            </q-card-section>
    
            <q-card-section>
            <q-form @submit="savePlayerInfo">
                <q-input v-model="playerInfo.first_name" label="Nombre" outlined dense />
                <q-input v-model="playerInfo.last_name" label="Apellido" outlined dense />
                <q-input v-model="playerInfo.birth_date" label="Fecha de Nacimiento" type="date" outlined dense />
                <q-input v-model="playerInfo.phone" label="Teléfono" outlined dense />
                
                <q-select
                v-model="playerInfo.gender"
                :options="['masculino', 'femenino', 'prefiero no decirlo']"
                label="Género"
                outlined
                dense
                />
    
                <q-select
                v-model="playerInfo.preferred_hand"
                :options="['diestro', 'zurdo', 'ambas']"
                label="Mano Preferida"
                outlined
                dense
                />
    
                <q-select
                v-model="playerInfo.position"
                :options="['reves', 'derecho', 'ambos lados']"
                label="Posición en Pista"
                outlined
                dense
                />
    
                <q-input v-model="playerInfo.photo_url" label="URL de Foto" outlined dense />
                <q-btn type="submit" label="Guardar" color="primary" class="q-mt-md" />
            </q-form>
            </q-card-section>
        </q-card>
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
          photo_url: "",
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
  