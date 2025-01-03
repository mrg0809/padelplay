<template>
    <q-layout view="hHh lpR fFf" class="bg-dark text-white">
      <q-header class="bg-primary text-white">
        <q-toolbar>
          <q-toolbar-title>Crear Torneo</q-toolbar-title>
        </q-toolbar>
      </q-header>
  
      <q-page-container>
        <q-page class="q-pa-md">
          <q-form @submit.prevent="createTournament">
            <q-input v-model="form.name" label="Nombre del Torneo" outlined dense required />
            <q-input v-model="form.start_date" label="Fecha de Inicio" type="date" outlined dense required />
            <q-input v-model="form.start_time" label="Hora de Inicio" type="time" outlined dense required />
            <q-select v-model="form.category" :options="categories" label="Categoría" outlined dense required />
            <q-select v-model="form.gender" :options="genders" label="Género" outlined dense required />
            <q-select v-model="form.system" :options="systems" label="Sistema de Competencia" outlined dense required />
            <q-input v-model.number="form.max_pairs" label="Máximo de Parejas" type="number" outlined dense required />
            <q-input v-model.number="form.price_per_pair" label="Precio por Pareja" type="number" outlined dense required />
            <q-input v-model="form.prize" label="Premio" outlined dense required />
            <q-checkbox
              v-for="court in courts"
              :key="court.id"
              v-model="form.courts_used"
              :label="court.name"
              :val="court.id"
              outlined
              dense
            />
            <q-btn type="submit" label="Crear Torneo" color="primary" class="q-mt-md" />
          </q-form>
        </q-page>
      </q-page-container>
    </q-layout>
  </template>
  
  <script>
  import { supabase } from "src/services/supabase";
  
  export default {
    name: "CreateTournament",
    data() {
      return {
        form: {
          name: "",
          start_date: "",
          start_time: "",
          category: "",
          gender: "",
          system: "",
          max_pairs: null,
          price_per_pair: null,
          prize: "",
          courts_used: [],
        },
        categories: ["primera", "segunda", "tercera", "cuarta", "quinta", "libre"],
        genders: ["mixto", "varonil", "femenil"],
        systems: ["eliminacion directa", "round robin", "combinado"],
        courts: [],
      };
    },
    async mounted() {
      const { data, error } = await supabase.from("courts").select("id, name").eq("club_id", this.clubId);
      if (!error) this.courts = data;
    },
    methods: {
      async createTournament() {
        try {
          const { data, error } = await supabase.from("tournaments").insert(this.form);
          if (error) throw new Error(error.message);
          this.$q.notify({ type: "positive", message: "Torneo creado exitosamente" });
          this.$router.push("/dashboard/club");
        } catch (err) {
          this.$q.notify({ type: "negative", message: `Error: ${err.message}` });
        }
      },
    },
  };
  </script>
  