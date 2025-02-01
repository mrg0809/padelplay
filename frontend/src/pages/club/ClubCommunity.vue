<template>
    <q-layout view="hHh lpR fFf" class="body text-white">
      <q-header elevated class="bg-primary text-white">
        <div class="header-content">
          <div class="greeting">
            <img src="/src/assets/padelplay.png" alt="Logo" class="logo-icon" />
            Comunidad del Club
          </div>
          <div class="header-icons">
            <q-btn flat round icon="arrow_back" @click="goBack" />
          </div>
        </div>
      </q-header>
  
      <q-page-container>
        <q-page class="q-pa-md">
          <!-- Pestañas -->
          <q-tabs v-model="tab" align="justify" class="text-white">
            <q-tab name="followed" label="Seguidos" />
            <q-tab name="followers" label="Seguidores" />
            <q-tab name="wall" label="Wall" />
          </q-tabs>
  
          <!-- Contenido de las pestañas -->
          <q-tab-panels v-model="tab" animated class="transparent-card q-mt-md">
            <!-- Pestaña: Seguidos -->
            <q-tab-panel name="followed">
              <div v-if="followedUsers.length === 0" class="text-center q-pa-md">
                <q-icon name="people" size="2em" />
                <p class="q-mt-sm">No sigues a ningún usuario todavía.</p>
              </div>
              <q-list v-else bordered>
                <q-item v-for="user in followedUsers" :key="user.id" class="q-mb-sm">
                  <q-item-section avatar>
                    <q-avatar>
                      <img :src="user.photo_url || 'default-avatar.png'" />
                    </q-avatar>
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>{{ user.name }}</q-item-label>
                    <q-item-label caption>{{ user.type }}</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </q-tab-panel>
  
            <!-- Pestaña: Seguidores -->
            <q-tab-panel name="followers">
              <div v-if="followers.length === 0" class="text-center q-pa-md">
                <q-icon name="people" size="2em" />
                <p class="q-mt-sm">No tienes seguidores todavía.</p>
              </div>
              <q-list v-else bordered>
                <q-item v-for="user in followers" :key="user.id" class="q-mb-sm">
                  <q-item-section avatar>
                    <q-avatar>
                      <img :src="user.photo_url || 'default-avatar.png'" />
                    </q-avatar>
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>{{ user.name }}</q-item-label>
                    <q-item-label caption>{{ user.type }}</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </q-tab-panel>
  
            <!-- Pestaña: Wall -->
            <q-tab-panel name="wall">
              <div class="text-center q-pa-md">
                <q-icon name="feed" size="2em" />
                <p class="q-mt-sm">Aquí podrás crear contenido y anuncios para el club.</p>
              </div>
            </q-tab-panel>
          </q-tab-panels>
        </q-page>
      </q-page-container>
      <ClubNavigationMenu />
    </q-layout>
  </template>
  
  <script>
  import { ref, onMounted } from "vue";
  import { supabase } from "src/services/supabase";
  import { useRouter } from "vue-router";
  import { useUserStore } from "src/stores/userStore";
  import ClubNavigationMenu from "src/components/ClubNavigationMenu.vue";

  
  export default {
    name: "ClubCommunity",
    components: {
      ClubNavigationMenu,
    },
    setup() {
      const router = useRouter();
      const tab = ref("followed"); // Pestaña activa por defecto
      const followedUsers = ref([]); // Lista de usuarios seguidos
      const followers = ref([]); // Lista de seguidores
      const userStore = useUserStore();
  
      // Obtener los usuarios seguidos y seguidores
      const fetchFollowedUsers = async () => {
        try {
          const { data: followedData, error: followedError } = await supabase
            .from("follows")
            .select("followed_id")
            .eq("follower_id", userStore.userId); // Reemplaza con el ID del club actual
  
          if (followedError) throw followedError;
  
          // Obtener detalles de los usuarios seguidos
          const followedIds = followedData.map((follow) => follow.followed_id);
          const { data: usersData, error: usersError } = await supabase
            .from("profiles")
            .select("id, full_name, photo_url, user_type")
            .in("id", followedIds);
  
          if (usersError) throw usersError;
  
          followedUsers.value = usersData.map((user) => ({
            id: user.id,
            name: user.full_name,
            photo_url: user.photo_url,
            type: user.user_type,
          }));
        } catch (error) {
          console.error("Error al obtener usuarios seguidos:", error);
        }
      };
  
      const fetchFollowers = async () => {
        try {
          const { data: followersData, error: followersError } = await supabase
            .from("follows")
            .select("follower_id")
            .eq("followed_id", userStore.userId); // Reemplaza con el ID del club actual
  
          if (followersError) throw followersError;
  
          // Obtener detalles de los seguidores
          const followerIds = followersData.map((follow) => follow.follower_id);
          const { data: usersData, error: usersError } = await supabase
            .from("profiles")
            .select("id, full_name, photo_url, user_type")
            .in("id", followerIds);
  
          if (usersError) throw usersError;
  
          followers.value = usersData.map((user) => ({
            id: user.id,
            name: user.full_name,
            photo_url: user.photo_url,
            type: user.user_type,
          }));
        } catch (error) {
          console.error("Error al obtener seguidores:", error);
        }
      };
  
      // Cargar datos al montar el componente
      onMounted(() => {
        fetchFollowedUsers();
        fetchFollowers();
      });
  
      // Función para regresar
      const goBack = () => {
        router.back();
      };
  
      return {
        tab,
        followedUsers,
        followers,
        goBack,
      };
    },
  };
  </script>
  
  <style scoped>
  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 16px;
    background-color: #000000;
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
    width: 60px;
    height: 60px;
  }
  
  .body {
    background-image: url(../../assets/menu/padelcourtfloor.jpg);
    background-size: cover;
  }
  
  .transparent-card {
    background-color: rgba(255, 255, 255, 0.3);
    border-radius: 8px;
  }
  
  .q-tab-panels {
    background: transparent;
  }
  
  .q-list {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 8px;
  }
  
  .q-item {
    background: rgba(255, 255, 255, 0.2);
    border-radius: 8px;
    margin-bottom: 8px;
  }
  </style>