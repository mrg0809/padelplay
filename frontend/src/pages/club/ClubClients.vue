<template>
    <q-layout view="hHh lpR fFf" class="body">
      <q-header elevated class="bg-primary text-white">
        <div class="header-content">
          <div class="greeting">
            <img src="/src/assets/padelplay.png" alt="Logo" class="logo-icon" />
            Mejores clientes
          </div>
          <div class="header-icons">
            <q-btn flat round icon="close" @click="goBack" />
          </div>
        </div>
      </q-header>
  
      <q-page-container>
        <div class="q-mt-xl"></div>
  
        <!-- Lista de clientes -->
        <q-list class="court-list">
          <q-item
            v-for="(client) in clients"
            :key="client.player_id"
            clickable
            @click="editClient(client)"
            class="text-black court-item"
          >
            <q-item-section avatar>
              <!-- Mostrar la foto del jugador -->
              <q-avatar>
                <img :src="client.photo_url || 'https://via.placeholder.com/150'" alt="Foto del jugador" />
              </q-avatar>
            </q-item-section>
            <q-item-section>
              <!-- Mostrar el nombre del jugador -->
              <q-item-label>{{ client.player_name }}</q-item-label>
              <q-item-label caption class="text-black">
                VISITAS: {{ client.visits }}
              </q-item-label>
            </q-item-section>
            <q-item-section side>
              <!-- Botón dinámico de seguir/dejar de seguir -->
              <q-btn
                :color="client.is_following ? 'negative' : 'positive'"
                :icon="client.is_following ? 'o_remove_circle' : 'o_add_circle'"
                :label="client.is_following ? 'Dejar de seguir' : 'Seguir'"
                @click.stop="toggleFollow(client)"
              />
            </q-item-section>
          </q-item>
        </q-list>
      </q-page-container>
  
      <ClubNavigationMenu />
    </q-layout>
  </template>
  
  <script>
  import { supabase } from "src/services/supabase";
  import api from "../../api";
  import { useUserStore } from "src/stores/userStore";
  import ClubNavigationMenu from "src/components/ClubNavigationMenu.vue";
  
  export default {
    components: {
      ClubNavigationMenu,
    },
    data() {
      return {
        clients: [],
        userStore: useUserStore(), // Inicializar el store de usuario
      };
    },
    methods: {
      goBack() {
        this.$router.back();
      },
      async toggleFollow(client) {
        const user = this.userStore.userId; // Obtener el usuario del store
        if (user) {
          try {
            if (client.is_following) {
              // Dejar de seguir
              await api.delete("community/unfollow", {
                data: {
                  follower_id: user,
                  followed_id: client.player_id,
                },
              });
            } else {
              // Seguir
              await api.post("community/follow", {
                follower_id: user,
                followed_id: client.player_id,
              });
            }
  
            // Actualizar el estado de seguimiento
            client.is_following = !client.is_following;
          } catch (error) {
            console.error("Error toggling follow:", error);
          }
        }
      },
      async fetchClients() {
        const user = this.userStore.userId; // Obtener el usuario del store
        if (user) {
          const clubId = this.userStore.clubId;
  
          try {
            // Obtener partidos del club
            const { data: matches, error: matchesError } = await supabase
              .from("matches")
              .select("team1_players, team2_players")
              .eq("club_id", clubId);
  
            if (matchesError) throw matchesError;
  
            // Contar visitas de jugadores
            const playerVisits = {};
            matches.forEach((match) => {
              match.team1_players.forEach((playerId) => {
                playerVisits[playerId] = (playerVisits[playerId] || 0) + 1;
              });
              match.team2_players.forEach((playerId) => {
                playerVisits[playerId] = (playerVisits[playerId] || 0) + 1;
              });
            });
  
            // Obtener nombres y fotos de los jugadores
            const { data: players, error: playersError } = await supabase
              .from("players")
              .select("user_id, first_name, last_name, photo_url")
              .in("user_id", Object.keys(playerVisits));
  
            if (playersError) throw playersError;
  
            // Combinar datos y verificar el estado de seguimiento
            this.clients = await Promise.all(
              Object.keys(playerVisits).map(async (playerId) => {
                const player = players.find((p) => p.user_id === playerId);
                const isFollowing = await this.checkIfFollowing(playerId);
  
                return {
                  player_id: playerId,
                  player_name: player ? `${player.first_name} ${player.last_name}` : "Unknown",
                  photo_url: player ? player.photo_url : null,
                  visits: playerVisits[playerId],
                  is_following: isFollowing,
                };
              })
            );
  
            // Ordenar por visitas
            this.clients.sort((a, b) => b.visits - a.visits);
          } catch (error) {
            console.error("Error fetching clients:", error);
          }
        }
      },
      async checkIfFollowing(followedId) {
        const user = this.userStore.userId; // Obtener el usuario del store
        if (user) {
          try {
            const { data, error } = await supabase
              .from("follows")
              .select("id")
              .eq("follower_id", user)
              .eq("followed_id", followedId)
              .single();
  
            if (error && error.code !== "PGRST116") { // PGRST116 es el código de "no se encontraron resultados"
              throw error;
            }
  
            return !!data; // Devuelve true si el usuario sigue al jugador, false si no
          } catch (error) {
            console.error("Error checking follow status:", error);
            return false;
          }
        }
        return false;
      },
    },
    mounted() {
      this.fetchClients();
    },
  };
  </script>
  
  <style scoped>
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
  
  .body {
    background-image: url(../../assets/menu/padelcourtfloor.jpg);
    background-size: cover;
  }
  
  .court-list {
    font-size: large;
  }
  
  .court-item {
    border-bottom: 1px solid rgba(0, 0, 0, 0.12); /* Línea divisoria sutil */
    background-color: rgba(255, 255, 255, 0.3); /* Fondo translúcido */
    margin-bottom: 8px; /* Espacio entre elementos */
    border-radius: 4px; /* Bordes redondeados */
  }
  
  .row-number {
    font-size: 1.2rem;
    font-weight: bold;
    color: #000000;
  }
  
  </style>