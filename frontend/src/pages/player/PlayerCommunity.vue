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
                      <img :src="getPlayerAvatar(player.photo_url)" />
                    </q-avatar>
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>{{ formatPlayerName(player) }}</q-item-label>
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
                      <img :src="getPlayerAvatar(player.photo_url)" />
                    </q-avatar>
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>{{ formatPlayerName(player) }}</q-item-label>
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
                      <img :src="getPlayerAvatar(player.photo_url)" />
                    </q-avatar>
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>{{ formatPlayerName(player) }}</q-item-label>
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
import { useUserStore } from "src/stores/userStore";
import PlayerNavigationMenu from "src/components/PlayerNavigationMenu.vue";
import NotificationBell from "src/components/NotificationBell.vue";
import BannerPromoScrolling from "src/components/BannerPromoScrolling.vue";
import { fetchFollowing, fetchFollowers, fetchSuggestedPlayers, isFollowingPlayer, unfollowPlayerSupabase, followPlayerSupabase } from 'src/services/supabase/community';
import { searchPlayersByName } from 'src/services/supabase/commun';
import { getPlayerAvatar, formatPlayerName } from 'src/helpers/communityUtils';

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
    const userStore = useUserStore();
    const following = ref([]);
    const followers = ref([]);
    const suggestedPlayers = ref([]);
    const isLoading = ref(true);

    // Load following players
    const loadFollowing = async () => {
      try {
        console.log("Loading following for user:", userStore.userId);
        following.value = await fetchFollowing(userStore.userId);
      } catch (error) {
        console.error("Error loading following:", error);
      }
    };

    // Load followers
    const loadFollowers = async () => {
      try {
        followers.value = await fetchFollowers(userStore.userId);
      } catch (error) {
        console.error("Error loading followers:", error);
      }
    };

    // Load suggested players
    const loadSuggestedPlayers = async () => {
      searching.value = true;
      try {
        suggestedPlayers.value = await fetchSuggestedPlayers(userStore.userId);
      } catch (error) {
        console.error("Error loading suggested players:", error);
      } finally {
        searching.value = false;
      }
    };

    // Search players by name
    const searchPlayers = async () => {
      searching.value = true;
      try {
        const players = await searchPlayersByName(searchQuery.value.trim());
        
        // Update the appropriate list based on active tab
        if (selectedTab.value === "suggestions") {
          suggestedPlayers.value = players;
        }
      } catch (error) {
        console.error("Error searching players:", error);
      } finally {
        searching.value = false;
      }
    };

    // Check if current user is following a player
    const isFollowing = (playerId) => {
      return following.value && isFollowingPlayer(following.value, playerId);
    };

    // Observe changes in the selected tab and load data accordingly
    watch(selectedTab, (newTab) => {
      if (newTab === "following") {
        loadFollowing();
      } else if (newTab === "followers") {
        loadFollowers();
      } else if (newTab === "suggestions") {
        loadSuggestedPlayers();
      }
    });

    // Load data when the component mounts
    onMounted(() => {
        if (userStore.userId) {
            isLoading.value = false;
            loadFollowing();
            loadFollowers();
            loadSuggestedPlayers();
        } else {
            console.error("No user ID found in userStore");
            isLoading.value = false;
        }
    });

    // Follow a player
    const followPlayer = async (playerId) => {
      try {
        await followPlayerSupabase(userStore.userId, playerId);
        // Reload lists after following
        loadFollowing();
        loadFollowers();
        loadSuggestedPlayers();
      } catch (error) {
        console.error('Error following player:', error);
        // Handle error, e.g., show a message to the user
      }
    };

    // Unfollow a player
    const unfollowPlayer = async (playerId) => {
      try {
        await unfollowPlayerSupabase(userStore.userId, playerId);
        // Reload lists after unfollowing
        loadFollowing();
        loadFollowers();
        loadSuggestedPlayers();
      } catch (error) {
        console.error("Error unfollowing player:", error);
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
      unfollowPlayer,
      getPlayerAvatar,
      formatPlayerName
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
