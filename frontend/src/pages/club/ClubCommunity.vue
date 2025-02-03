<template>
    <q-layout view="hHh lpR fFf" class="body text-white">
      <!-- Encabezado -->
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
                <q-btn icon="add" color="black" class="q-mb-xl fixed-bottom-right" size="lg" glossy round @click="showCreatePostDialog = true" />
              </div>
  
              <!-- Lista de Posts -->
              <q-list bordered class="q-mt-md">
                <q-item v-for="post in posts" :key="post.id" class="q-mb-sm">
                  <q-item-section>
                    <q-item-label>{{ post.content }}</q-item-label>
                    <q-item-label caption>{{ formatDate(post.created_at) }}</q-item-label>
                    <!-- Mostrar multimedia si existe -->
                    <div v-if="post.media_url" class="q-mt-sm">
                      <img
                        :src="post.media_url"
                        style="max-width: 100%; border-radius: 8px;"
                        alt="Imagen del post"
                      />
                    </div>
                    <!-- Mostrar reacciones -->
                    <div class="q-mt-sm">
                      <q-chip v-for="(count, type) in post.reactions" :key="type">
                        <span>{{ reactionEmojis[type] }} {{ count }}</span>
                      </q-chip>
                    </div>
                  </q-item-section>
                  <q-item-section side>
                    <q-btn flat icon="delete" color="negative" @click="deletePost(post.id)" />
                  </q-item-section>
                </q-item>
              </q-list>
            </q-tab-panel>
          </q-tab-panels>
        </q-page>
      </q-page-container>
  
      <!-- Diálogo para crear un nuevo post -->
      <q-dialog v-model="showCreatePostDialog">
        <q-card class="q-pa-md bg-black" style="min-width: 300px">
          <q-card-section>
            <div class="text-h6">Nuevo Post</div>
          </q-card-section>
          <q-card-section>
            <q-input
              v-model="newPostContent"
              type="textarea"
              label="Escribe tu post"
              autogrow
            />
            <q-file
              v-model="newPostMedia"
              label="Subir imagen o video"
              accept="image/*, video/*"
              class="q-mt-md"
            />
          </q-card-section>
          <q-card-actions align="right">
            <q-btn flat label="Cancelar" color="negative" v-close-popup />
            <q-btn flat label="Publicar" color="green" @click="createPost" v-close-popup />
          </q-card-actions>
        </q-card>
      </q-dialog>
  
      <ClubNavigationMenu />
    </q-layout>
  </template>
  
  <script>
  import { ref, onMounted } from "vue";
  import { supabase } from "src/services/supabase";
  import { useRouter } from "vue-router";
  import { useUserStore } from "src/stores/userStore";
  import api from "../../api";
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
      const posts = ref([]); // Lista de posts
      const userStore = useUserStore();
      const newPostContent = ref(""); // Contenido del nuevo post
      const newPostMedia = ref(null); // Archivo multimedia seleccionado
      const showCreatePostDialog = ref(false); // Controlar visibilidad del diálogo
      const reactionEmojis = {
        like: "👍",
        love: "❤️",
        laugh: "😂",
        wow: "😮",
        sad: "😢",
        angry: "😡",
        };
  
      // Obtener los usuarios seguidos y seguidores
      const fetchFollowedUsers = async () => {
        try {
          const { data: followedData, error: followedError } = await supabase
            .from("follows")
            .select("followed_id")
            .eq("follower_id", userStore.userId);
  
          if (followedError) throw followedError;
  
          const followedIds = followedData.map((follow) => follow.followed_id);
          const { data: profilesData, error: profilesError } = await supabase
            .from("profiles")
            .select("id, full_name, user_type, club_id")
            .in("id", followedIds);
  
          if (profilesError) throw profilesError;
  
          const { data: playersData, error: playersError } = await supabase
            .from("players")
            .select("user_id, photo_url")
            .in("user_id", followedIds);
  
          if (playersError) throw playersError;
  
          const clubIds = profilesData
            .filter((profile) => profile.user_type === "club")
            .map((profile) => profile.club_id);
  
          const { data: clubsData, error: clubsError } = await supabase
            .from("clubs")
            .select("id, logo_url")
            .in("id", clubIds);
  
          if (clubsError) throw clubsError;
  
          followedUsers.value = profilesData.map((profile) => {
            const player = playersData.find((p) => p.user_id === profile.id);
            const club = clubsData.find((c) => c.id === profile.club_id);
  
            return {
              id: profile.id,
              name: profile.full_name,
              photo_url: profile.user_type === "player"
                ? player?.photo_url
                : club?.logo_url || "default-avatar.png",
              type: profile.user_type,
            };
          });
        } catch (error) {
          console.error("Error al obtener usuarios seguidos:", error);
        }
      };
  
      const fetchFollowers = async () => {
        try {
          const { data: followersData, error: followersError } = await supabase
            .from("follows")
            .select("follower_id")
            .eq("followed_id", userStore.userId);
  
          if (followersError) throw followersError;
  
          const followerIds = followersData.map((follow) => follow.follower_id);
          const { data: profilesData, error: profilesError } = await supabase
            .from("profiles")
            .select("id, full_name, user_type, club_id")
            .in("id", followerIds);
  
          if (profilesError) throw profilesError;
  
          const { data: playersData, error: playersError } = await supabase
            .from("players")
            .select("user_id, photo_url")
            .in("user_id", followerIds);
  
          if (playersError) throw playersError;
  
          const clubIds = profilesData
            .filter((profile) => profile.user_type === "club")
            .map((profile) => profile.club_id);
  
          const { data: clubsData, error: clubsError } = await supabase
            .from("clubs")
            .select("id, logo_url")
            .in("id", clubIds);
  
          if (clubsError) throw clubsError;
  
          followers.value = profilesData.map((profile) => {
            const player = playersData.find((p) => p.user_id === profile.id);
            const club = clubsData.find((c) => c.id === profile.club_id);
  
            return {
              id: profile.id,
              name: profile.full_name,
              photo_url: profile.user_type === "player"
                ? player?.photo_url
                : club?.logo_url || "default-avatar.png",
              type: profile.user_type,
            };
          });
        } catch (error) {
          console.error("Error al obtener seguidores:", error);
        }
      };
  
      // Obtener posts del club
      const fetchPosts = async () => {
        try {
            const response = await api.get(`community/posts/club/${userStore.clubId}`);
            console.log("Datos recibidos:", response.data);
            posts.value = response.data.posts;
        } catch (error) {
            console.error("Error al obtener posts:", error);
        }
        };

        // Crear un nuevo post
        const createPost = async () => {
          try {
            let mediaUrl = null;

            // Crear el post sin media_url inicialmente
            const postResponse = await api.post("/community/posts", {
              club_id: userStore.clubId,
              content: newPostContent.value,
            });
            console.log(postResponse.data.data[0].id)
            const postId = postResponse.data.data[0].id; // Obtener el ID del post recién creado

            // Subir el archivo si existe
            if (newPostMedia.value) {
              const formData = new FormData();
              formData.append("file", newPostMedia.value);

              const uploadResponse = await api.post(`/community/posts/upload-media?post_id=${postId}`, formData, {
                headers: {
                  "Content-Type": "multipart/form-data",
                },
              });
            }

            // Agregar el nuevo post a la lista
            posts.value.unshift(postResponse.data);
            newPostContent.value = ""; // Limpiar el campo de texto
            newPostMedia.value = null; // Limpiar el archivo multimedia
          } catch (error) {
            console.error("Error al crear post:", error);
          }
        };

        // Eliminar un post
       const deletePost = async (postId) => {
        try {
            await api.delete(`community/posts/${postId}`, {
            data: { club_id: userStore.clubId },
            });
            posts.value = posts.value.filter((post) => post.id !== postId); // Eliminar el post de la lista
        } catch (error) {
            console.error("Error al eliminar post:", error);
        }
        };
  
      // Formatear fecha
      const formatDate = (dateString) => {
        if (!dateString) return "Fecha no disponible"; // Manejar casos donde dateString es null o undefined
        const date = new Date(dateString);
        if (isNaN(date.getTime())) {
            return "Fecha no disponible"; // Manejar fechas inválidas
        }
        return date.toLocaleString(); // Formatear la fecha
        };
  
      // Cargar datos al montar el componente
      onMounted(() => {
        fetchFollowedUsers();
        fetchFollowers();
        fetchPosts();
      });

      const goBack = () => {
        router.back();
      };
  
      return {
        tab,
        followedUsers,
        followers,
        posts,
        newPostContent,
        showCreatePostDialog,
        createPost,
        deletePost,
        formatDate,
        goBack,
        reactionEmojis,
        newPostMedia,
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

  .fixed-bottom-right {
  position: fixed;
  bottom: 80px;
  right: 20px;
  z-index: 1000;
  }
</style>