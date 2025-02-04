<template>
    <q-list bordered class="q-mt-md">
      <q-item v-for="post in posts" :key="post.id" class="q-mb-sm post">
        <q-item-section>
          <q-item-label>{{ post.content }}</q-item-label>
          <q-item-label caption>{{ formatDate(post.created_at) }}</q-item-label>
          <div v-if="post.media_url" class="q-mt-sm">
            <img
              :src="post.media_url"
              style="max-width: 100%; border-radius: 8px;"
              alt="Imagen del post"
            />
          </div>
          <div class="q-mt-sm">
            <q-chip v-for="(count, type) in post.reactions" :key="type" color="transparent">
              <span>{{ reactionEmojis[type] }} {{ count }}</span>
            </q-chip>
          </div>
          <div>
            <q-chip
              :label="selectedReaction ? reactionEmojis[selectedReaction] : '😊'"
              color="primary"
              text-color="white"
              @click="toggleMenu(post.id)"
              clickable
            />
            <q-menu v-model="isMenuVisible[post.id]">
              <q-list>
                <q-item
                  v-for="(emoji, type) in reactionEmojis"
                  :key="type"
                  clickable
                  v-close-popup
                  @click="setReaction(type, post.id)"
                >
                  <q-item-section>{{ emoji }}</q-item-section>
                </q-item>
              </q-list>
            </q-menu>
          </div>
        </q-item-section>
      </q-item>
    </q-list>
  </template>
  
  <script>
  import { ref } from 'vue';
  import api from 'src/api'; // Importa tu API
  
  export default {
    props: {
      posts: Array,
      reactionEmojis: Object,
      selectedReaction: String,
      playerId: String,
    },
    emits: ['update:posts'], // Emitir eventos para actualizar el estado
    setup(props, { emit }) {
      // Estado local para controlar la visibilidad del menú de cada post
      const isMenuVisible = ref({});
  
      // Función para abrir/cerrar el menú de un post específico
      const toggleMenu = (postId) => {
        isMenuVisible.value[postId] = !isMenuVisible.value[postId];
      };
  
      // Función para manejar la selección de una reacción
      const setReaction = async (reactionType, postId) => {
        console.log('Reacción seleccionada:', reactionType, 'para el post:', postId);
        try {
          // Verificar si el usuario ya reaccionó con este tipo de reacción
          const post = props.posts.find((p) => p.id === postId);
          const existingReaction = post.reactions[reactionType];
  
          if (existingReaction) {
            // Si ya reaccionó, eliminar la reacción
            await api.delete('community/unreact', {
              data: {
                post_id: postId,
                player_id: props.playerId,
              },
            });
          } else {
            // Si no reaccionó, agregar la reacción
            await api.post('community/react', {
              post_id: postId,
              player_id: props.playerId,
              reaction_type: reactionType,
            });
          }
  
          // Actualizar el estado local de las reacciones
          const updatedPosts = props.posts.map((p) => {
            if (p.id === postId) {
              const updatedReactions = { ...p.reactions };
              if (existingReaction) {
                // Eliminar la reacción
                delete updatedReactions[reactionType];
              } else {
                // Agregar la reacción
                updatedReactions[reactionType] = (updatedReactions[reactionType] || 0) + 1;
              }
              return { ...p, reactions: updatedReactions };
            }
            return p;
          });
  
          // Emitir el evento para actualizar las publicaciones en el componente padre
          emit('update:posts', updatedPosts);
        } catch (error) {
          console.error('Error al manejar la reacción:', error);
        }
      };
  
      // Función para formatear la fecha
      const formatDate = (dateString) => {
        if (!dateString) return "Fecha no disponible";
        const date = new Date(dateString);
        if (isNaN(date.getTime())) {
          return "Fecha no disponible";
        }
        return date.toLocaleString();
      };
  
      return {
        isMenuVisible,
        toggleMenu,
        formatDate,
        setReaction,
      };
    },
  };
  </script>
  
  <style scoped>
  .post {
    background-image: url(src/assets/texturafondo.png);
    background-size: cover;
  }
  </style>