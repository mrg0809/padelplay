<template>
    <q-layout view="hHh lpR fFf" class="bg-dark text-white">
      <q-header elevated class="text-white">
        <div class="header-content">
          <div class="greeting">
            <img src="/src/assets/padelplay.png" alt="Logo" class="logo-icon" />
          </div>
          <div class="header-icons">
            <NotificationBell />
          </div>
        </div>
        <BannerPromoScrolling />
      </q-header>
      <q-page-container class="home">
        <q-page class="q-pa-md">
            <div v-if="isLoading">
                <q-inner-loading :showing="true" size="xl" color="primary" />
             </div>
             <div v-else> 
          <div class="search-bar">
            <q-input
              v-model="searchQuery"
              filled
              dense
              placeholder="Buscar jugador por nombre"
              @input="searchPlayers"
              class="text-dark"
            >
              <template v-slot:prepend>
                <q-icon name="search" class="text-primary" />
              </template>
            </q-input>
          </div>
  
          <q-tabs v-model="selectedTab" align="justify" class="text-white">
            <q-tab name="following" label="Siguiendo" />
            <q-tab name="followers" label="Seguidores" />
            <q-tab name="suggestions" label="Sugerencias" />
          </q-tabs>
  
          <q-separator class="q-my-md" color="white" />
  
          <q-tab-panels v-model="selectedTab" animated>
            <q-tab-panel name="following">
              <q-list v-if="following.length > 0">
                <q-item v-for="player in following" :key="player.user_id" clickable @click="viewPlayerProfile(player.user_id)">
                  <q-item-section avatar>
                    <q-avatar>
                      <img :src="player.photo_url || '/src/assets/logo.jpeg'" />
                    </q-avatar>
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>{{ player.first_name }} {{ player.last_name }}</q-item-label>
                    <q-item-label caption>{{ player.category }}</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
              <div v-else class="text-center">No estás siguiendo a nadie.</div>
            </q-tab-panel>
  
            <q-tab-panel name="followers">
              <q-list v-if="followers.length > 0">
                <q-item v-for="player in followers" :key="player.user_id" clickable @click="viewPlayerProfile(player.user_id)">
                  <q-item-section avatar>
                    <q-avatar>
                      <img :src="player.photo_url || '/src/assets/logo.jpeg'" />
                    </q-avatar>
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>{{ player.first_name }} {{ player.last_name }}</q-item-label>
                    <q-item-label caption>{{ player.category }}</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
              <div v-else class="text-center">No tienes seguidores.</div>
            </q-tab-panel>
  
            <q-tab-panel name="suggestions">
              <q-list v-if="suggestedPlayers.length > 0">
                <q-item v-for="player in suggestedPlayers" :key="player.user_id" clickable @click="viewPlayerProfile(player.user_id)">
                  <q-item-section avatar>
                    <q-avatar>
                      <img :src="player.photo_url || '/src/assets/logo.jpeg'" />
                    </q-avatar>
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>{{ player.first_name }} {{ player.last_name }}</q-item-label>
                    <q-item-label caption>{{ player.category }}</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                      <q-btn
                        v-if="!isFollowing(player.user_id)"
                        color="primary"
                        label="Seguir"
                        size="sm"
                        @click.stop="followPlayer(player.user_id)"
                      />
                      <q-btn v-else color="red" label="Dejar de seguir" size="sm" @click.stop="unfollowPlayer(player.user_id)"/>
                  </q-item-section>
                </q-item>
              </q-list>
              <div v-else class="text-center">No hay sugerencias.</div>
            </q-tab-panel>
          </q-tab-panels>
        </div>  
        </q-page>
      </q-page-container>
      <PlayerNavigationMenu />
    </q-layout>
  </template>
  
  <script>
import { ref, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import { supabase } from "../../services/supabase";
import { useUser } from 'src/composables/useUser'; // Importa el composable del usuario
import PlayerNavigationMenu from "src/components/PlayerNavigationMenu.vue";
import NotificationBell from "src/components/NotificationBell.vue";
import BannerPromoScrolling from "src/components/BannerPromoScrolling.vue";

export default {
  components: {
    PlayerNavigationMenu,
    BannerPromoScrolling,
    NotificationBell,
  },
  setup() {
    const router = useRouter();
    const searchQuery = ref("");
    const searching = ref(false);
    const selectedTab = ref("following"); // Pestaña seleccionada por defecto
    const following = ref([]);
    const followers = ref([]);
    const suggestedPlayers = ref([]);
    const { user, isLoading } = useUser(); 

    // Función para obtener la lista de jugadores a los que sigue el usuario actual
    const fetchFollowing = async () => {
      try {
        const { data, error } = await supabase
          .from("follows")
          .select(`
            followed_id:followed_id (
              user_id,
              first_name,
              last_name,
              photo_url,
              category
            )
          `)
          .eq("follower_id", user.value.id);

        if (error) throw error;
        following.value = data.map(item => item.followed_id);
      } catch (error) {
        console.error("Error fetching following:", error);
      }
    };

    // Función para obtener la lista de seguidores del usuario actual
    const fetchFollowers = async () => {
      try {
        const { data, error } = await supabase
          .from("follows")
          .select(`
            follower_id:follower_id (
              user_id,
              first_name,
              last_name,
              photo_url,
              category
            )
          `)
          .eq("followed_id", user.value.id);

        if (error) throw error;
        followers.value = data.map(item => item.follower_id);
      } catch (error) {
        console.error("Error fetching followers:", error);
      }
    };

    // Función para obtener sugerencias de jugadores para seguir
    const fetchSuggestedPlayers = async () => {
      searching.value = true;
      try {
        // Obtener los IDs de los jugadores que el usuario actual ya sigue
        const { data: followingIdsData, error: followingIdsError } = await supabase
          .from("follows")
          .select("followed_id")
          .eq("follower_id", user.value.id);

        if (followingIdsError) throw followingIdsError;
        const followingIds = followingIdsData.map((f) => f.followed_id);

        // Obtener todos los jugadores excepto los que el usuario actual ya sigue y el usuario actual
        const { data: players, error } = await supabase
          .from("players")
          .select("*")
          .neq("user_id", user.value.id)
          .not("user_id", "in", `(${followingIds.join(",")})`);

        if (error) throw error;

        suggestedPlayers.value = players;
      } catch (error) {
        console.error("Error fetching suggested players:", error);
      } finally {
        searching.value = false;
      }
    };

    // Busca jugadores basado en el texto ingresado
    const searchPlayers = async () => {
      searching.value = true;
      try {
        // Modifica la consulta para buscar por nombre
        const { data, error } = await supabase
          .from("players")
          .select("*")
          .ilike("first_name", `%${searchQuery.value}%`); // Búsqueda insensible a mayúsculas/minúsculas

        if (error) throw error;

        // Si la pestaña de sugerencias está activa, actualiza la lista de sugerencias
        if (selectedTab.value === "suggestions") {
          suggestedPlayers.value = data;
        }
      } catch (error) {
        console.error("Error searching players:", error);
      } finally {
        searching.value = false;
      }
    };

    // Función para determinar si el usuario actual sigue a otro jugador
    const isFollowing = (playerId) => {
      return following.value.some((p) => p.user_id === playerId);
    };

    // Observar cambios en la pestaña seleccionada y cargar datos en consecuencia
    watch(selectedTab, (newTab) => {
      if (newTab === "following") {
        fetchFollowing();
      } else if (newTab === "followers") {
        fetchFollowers();
      } else if (newTab === "suggestions") {
        fetchSuggestedPlayers();
      }
    });

    // Cargar datos al montar el componente
    onMounted(() => {
        if (!isLoading.value && user.value) {
            fetchFollowing();
            fetchFollowers();
            fetchSuggestedPlayers();
        }
    });

    watch(isLoading, (newIsLoading) => {
         if (!newIsLoading && user.value) {
             console.log("isLoading changed to false, user.value:", user.value);
             fetchFollowing();
             fetchFollowers();
             fetchSuggestedPlayers();
         }
     });
    
    //Funcion para seguir
    const followPlayer = async (playerId) => {
        try {
            const response = await fetch('/.netlify/functions/follow-player', {
                method: 'POST',
                headers: {
                'Content-Type': 'application/json',
                },
                body: JSON.stringify({ followed_id: playerId }),
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Error al seguir al jugador');
            }
            const data = await response.json();
            console.log('Follow successful:', data);
            // Recargar las listas después de seguir
            fetchFollowing();
            fetchFollowers();
            fetchSuggestedPlayers();

        } catch (error) {
            console.error('Error following player:', error);
            // Manejar el error, por ejemplo, mostrando un mensaje al usuario
        }
    };

    // Función para dejar de seguir a un jugador
    const unfollowPlayer = async (playerId) => {
      const { error } = await supabase
        .from('follows')
        .delete()
        .eq('follower_id', user.value.id)
        .eq('followed_id', playerId);

      if (error) {
        console.error("Error unfollowing player:", error);
      } else {
        // Recargar las listas después de dejar de seguir
        fetchFollowing();
        fetchFollowers();
        fetchSuggestedPlayers();
      }
    };

    return {
      searchQuery,
      searching,
      selectedTab,
      following,
      followers,
      isLoading,
      suggestedPlayers,
      searchPlayers,
      isFollowing,
      viewPlayerProfile: (playerId) => {
        router.push(`/player/${playerId}`);
      },
      followPlayer,
      unfollowPlayer
    };
  },
};
</script>
  
<style>

    .home {
        background-color: #dddddd;
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
  .search-bar {
  background-color: white;
  height: 30px;
  width: 100%;
  margin-bottom: 16px;
  border-radius: 80px;
}

.search-bar q-input {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
}


</style>
  