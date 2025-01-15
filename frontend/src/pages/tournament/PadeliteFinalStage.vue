<template>
    <q-layout view="hHh lpR fFf" class="bg-dark text-white">
      <q-header elevated class="bg-primary text-white">
        <q-toolbar>
          <q-toolbar-title>PADELITE</q-toolbar-title>
          <q-btn flat round icon="arrow_back" @click="goBack" label="REGRESAR" />
        </q-toolbar>
      </q-header>
      <q-page-container class="q-pa-md">
    <q-page class="flex flex-center">
      <div class="bracket q-pa-md">
        <div class="round q-mb-md">
          <h3 class="text-center q-mb-sm">Cuartos de Final</h3>
          <div class="matchup q-mb-sm" v-for="(match, index) in cuartosDeFinal" :key="index">
            <div class="team">
              <img :src="match.team1.logo" alt="Logo del equipo" class="team-logo">
              <span>{{ match.team1.nombre }}</span>
            </div>
            <div class="vs">vs</div>
            <div class="team">
              <img :src="match.team2.logo" alt="Logo del equipo" class="team-logo">
              <span>{{ match.team2.nombre }}</span>
            </div>
          </div>
        </div>
  
        <div class="round q-mb-md">
          <h3 class="text-center q-mb-sm">Semifinal</h3>
          <div class="matchup q-mb-sm" v-for="(match, index) in semifinal" :key="index">
            <div class="team">
              <span>{{ match.team1 }}</span>
            </div>
            <div class="vs">vs</div>
            <div class="team">
              <span>{{ match.team2 }}</span>
            </div>
          </div>
        </div>
  
        <div class="round">
          <h3 class="text-center q-mb-sm">Final</h3>
          <div class="matchup q-mb-sm">
            <div class="team">
              <span>{{ final.team1 }}</span>
            </div>
            <div class="vs">vs</div>
            <div class="team">
              <span>{{ final.team2 }}</span>
            </div>
          </div>
        </div>
  
        <div class="copa">
          <img src="../../assets/padelite/copa.png" alt="Copa">
        </div>
      </div>
    </q-page>
</q-page-container>
    </q-layout>
  </template>
  
  <script>
  import { ref, onMounted, watch } from "vue";
  import { supabase } from "src/services/supabase";
  
  
  export default {
    setup() {
      const grupos = ref([]);
      const cuartosDeFinal = ref([]);
      const semifinal = ref([]);
      const final = ref({});
      const goBack = () => {
          router.back();
        };
      
  
      const obtenerGrupos = async () => {
        // Obtener los equipos de Supabase
        const { data: equipos } = await supabase
          .from("padeliteteams")
          .select("*")
  
        // Obtener los resultados de los partidos
        const { data: partidos } = await supabase
          .from("padelitematches")
          .select("*")
  
        // Calcular los puntajes de cada equipo
        const puntajes = {};
        for (const partido of partidos) {
          const equipo1Id = partido.equipo1_id;
          const equipo2Id = partido.equipo2_id;
  
          puntajes[equipo1Id] = (puntajes[equipo1Id] || 0) + partido.puntaje_equipo1;
          puntajes[equipo2Id] = (puntajes[equipo2Id] || 0) + partido.puntaje_equipo2;
        }
  
        // Agrupar los equipos por grupo
        const gruposTemp = {};
        for (const equipo of equipos) {
          const grupoNombre = equipo.grupo;
          if (!gruposTemp[grupoNombre]) {
            gruposTemp[grupoNombre] = {
              nombre: grupoNombre,
              equipos: [],
            };
          }
          gruposTemp[grupoNombre].equipos.push({
            ...equipo,
            puntos: puntajes[equipo.id] || 0,
          });
  
          // Ordenar los equipos por puntos (de mayor a menor)
          gruposTemp[grupoNombre].equipos.sort((a, b) => b.puntos - a.puntos);
        }
  
        grupos.value = Object.values(gruposTemp);
      };
  
      onMounted(async () => {
        await obtenerGrupos();
  
        // Obtener los equipos clasificados a cuartos de final
        const equiposClasificados = grupos.value.map(grupo => [
          grupo.equipos[0], // Primer lugar del grupo
          grupo.equipos[1]  // Segundo lugar del grupo
        ]).flat();
  
        // Definir los enfrentamientos de cuartos de final
        cuartosDeFinal.value = [
          { team1: equiposClasificados[0], team2: equiposClasificados[7] }, // 1°A vs 2°D
          { team1: equiposClasificados[2], team2: equiposClasificados[5] }, // 1°B vs 2°C
          { team1: equiposClasificados[3], team2: equiposClasificados[4] }, // 2°B vs 1°C
          { team1: equiposClasificados[1], team2: equiposClasificados[6] }  // 2°A vs 1°D
        ];
  
        // Simular resultados de cuartos de final (reemplazar con la lógica real)
        const resultadosCuartos = cuartosDeFinal.value.map(match => Math.random() < 0.5 ? match.team1 : match.team2);
  
        // Definir los enfrentamientos de semifinal
        semifinal.value = [
          { team1: resultadosCuartos[0].nombre, team2: resultadosCuartos[1].nombre },
          { team1: resultadosCuartos[2].nombre, team2: resultadosCuartos[3].nombre }
        ];
  
        // Simular resultados de semifinal (reemplazar con la lógica real)
        const resultadosSemifinal = semifinal.value.map(match => Math.random() < 0.5 ? match.team1 : match.team2);
  
        // Definir la final
        final.value = { team1: resultadosSemifinal[0], team2: resultadosSemifinal[1] };

      });
  
      return {
        grupos,
        cuartosDeFinal,
        semifinal,
        final,
        goBack,
      };
    },
  };
  </script>
  
  <style scoped>
  .bracket {
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  
  .round {
    width: 300px;
  }
  
  .matchup {
    display: flex;
    justify-content: space-around;
    align-items: center;
    border: 1px solid #ccc;
    padding: 10px;
    border-radius: 5px;
  }
  
  .team {
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  
  .team-logo {
    width: 50px;
    height: 50px;
    object-fit: contain;
    margin-bottom: 5px;
  }
  
  .vs {
    font-weight: bold;
  }
  
  .copa {
    margin-top: 20px;
  }
  
  .copa img {
    width: 100px;
  }
  </style>