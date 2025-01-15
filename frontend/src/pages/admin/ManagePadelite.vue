<template>
    <q-layout view="hHh lpR fFf" class="bg-dark text-white">
      <q-header elevated class="bg-primary text-white">
        <q-toolbar>
          <q-toolbar-title>Cargar Resultados</q-toolbar-title>
        </q-toolbar>
      </q-header>
  
      <q-page-container class="q-pa-md">
        <div v-for="grupo in grupos" :key="grupo.nombre" class="q-mb-md">
          <div class="text-h6">{{ grupo.nombre }}</div>
          <q-separator />
          <div v-for="partido in grupo.partidos" :key="partido.id" class="q-my-md">
            <div class="row items-center">
              <div class="col-4">{{ partido.equipo1 }}</div>
              <q-input
                v-model.number="partido.puntaje_equipo1"
                type="number"
                dense
                style="max-width: 80px"
              />
              <div class="col-1 text-center">vs</div>
              <q-input
                v-model.number="partido.puntaje_equipo2"
                type="number"
                dense
                style="max-width: 80px"
              />
              <div class="col-4">{{ partido.equipo2 }}</div>
            </div>
          </div>
        </div>
  
        <q-btn color="primary" label="Guardar Resultados" @click="guardarResultados" />
      </q-page-container>
    </q-layout>
  </template>
  
  <script>
  import { ref } from "vue";
  import { supabase } from "src/services/supabase";
  
  export default {
    name: "CargarResultados",
    setup() {
      const grupos = ref([
        {
          nombre: "GRUPO A",
          partidos: [
            { id: 1, equipo1: "WOOR", equipo2: "kPetrom", puntaje_equipo1: null, puntaje_equipo2: null },
            { id: 2, equipo1: "DIA", equipo2: "LIOLI", puntaje_equipo1: null, puntaje_equipo2: null },
            // ... más partidos del grupo A
          ],
        },
        // ... otros grupos
      ]);
  
      const guardarResultados = async () => {
        try {
          for (const grupo of grupos.value) {
            for (const partido of grupo.partidos) {
              await supabase
                .from("partidos")
                .update({
                  puntaje_equipo1: partido.puntaje_equipo1,
                  puntaje_equipo2: partido.puntaje_equipo2,
                })
                .eq("id", partido.id);
            }
          }
  
          // Mostrar mensaje de éxito
          console.log("Resultados guardados correctamente");
        } catch (error) {
          // Mostrar mensaje de error
          console.error("Error al guardar los resultados:", error);
        }
      };
  
      return {
        grupos,
        guardarResultados,
      };
    },
  };
  </script>