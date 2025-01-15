<template>
    <q-layout view="hHh lpR fFf" class="bg-dark text-white">
      <q-header elevated class="bg-primary text-white">
        <q-toolbar>
          <q-toolbar-title>PADELITE</q-toolbar-title>
          <q-btn flat round icon="arrow_back" @click="goBack" label="REGRESAR" />
        </q-toolbar>
      </q-header>
  
      <q-page-container class="q-pa-md">
        <div v-if="isLoading">Cargando...</div>
        <q-carousel
          v-model="slide"
          animated
          infinite
          :autoplay="autoplay"
          transition-prev="slide-right"
          transition-next="slide-left"
          class="bg-dark text-white"
          navigation
          padding
          swipeable
          height="600px">
          <q-carousel-slide v-for="(grupo, index) in grupos" :key="grupo.nombre" :name="index + 1"
            class="column items-stretch">
            <q-card class="bg-dark text-white" @click="goToGrupo(grupo.nombre)">
              <q-card-section class="text-center">
                <div class="text-h6">GRUPO {{ grupo.nombre }}</div>
              </q-card-section>
              <q-separator />
              <q-card-section>
                <q-list>
                  <q-item v-for="(equipo) in grupo.equipos" :key="equipo.id">
                    <q-item-section avatar>
                      <q-avatar>
                        <img :src="equipo.logo" alt="Logo del equipo">
                      </q-avatar>
                    </q-item-section>
                    <q-item-section>
                      <q-item-label>{{ equipo.nombre }}</q-item-label>
                    </q-item-section>
                    <q-item-section side>
                      <q-item-label class="text-bold">{{ equipo.puntos }} PUNTOS</q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-card-section>
            </q-card>
          </q-carousel-slide>
        </q-carousel>
        <q-btn color="primary" label="Cuadro Final" @click="goToCuadroFinal" class="full-width q-mt-md" />
      </q-page-container>
  
      <PlayerNavigationMenu />
    </q-layout>
  </template>
  
  <script>
    import { ref } from "vue";
    import { useRouter } from "vue-router";
    import PlayerNavigationMenu from "src/components/PlayerNavigationMenu.vue";
    import { supabase } from "src/services/supabase";
  
    export default {
      name: "PadeliteTournament",
      components: {
        PlayerNavigationMenu,
      },
      setup() {
        const router = useRouter();
        const slide = ref(1);
        const autoplay = ref(false);
        const goBack = () => {
          router.back();
        };
        const grupos = ref([]); // Variable reactiva grupos
        const isLoading = ref(true);
  
        const obtenerGrupos = async () => {
          isLoading.value = true;
          try {
            const { data: equipos } = await supabase
              .from("padeliteteams")
              .select("*");
  
            const { data: partidos } = await supabase
              .from("padelitematches")
              .select("*");
  
            const puntajes = {};
            for (const partido of partidos) {
              const equipo1Id = partido.equipo1_id;
              const equipo2Id = partido.equipo2_id;
  
              puntajes[equipo1Id] = (puntajes[equipo1Id] || 0) + partido.puntaje_equipo1;
  
  
              puntajes[equipo2Id] = (puntajes[equipo2Id] || 0) + partido.puntaje_equipo2;
            }
  
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
  
          } catch (error) {
            console.error("Error fetching data:", error);
          } finally {
            isLoading.value = false;
          }
        };
  
        obtenerGrupos();
  
        const goToGrupo = (nombreGrupo) => {
          router.push(`/grupo/${nombreGrupo}`);
        };
  
        const goToCuadroFinal = () => {
          router.push("/padelite/cuadro-final");
        };
  
        return {
          goBack,
          grupos,
          goToGrupo,
          isLoading,
          slide,
          autoplay,
          goToCuadroFinal,
        };
      },
    };
  </script>
  
  <style scoped>
    .q-card {
      background-color: #1e1e1e;
      color: white;
      cursor: pointer;
    }
  
    .q-card:hover {
      background-color: #292929;
    }
  </style>