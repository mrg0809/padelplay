import { ref } from "vue";
import api from "src/services/api";

export function useReactions(posts, playerId) {
  const isMenuVisible = ref({});

  const toggleMenu = (postId) => {
    isMenuVisible.value[postId] = !isMenuVisible.value[postId];
  };

  const setReaction = async (reactionType, postId) => {
    try {
      const post = posts.value.find((p) => p.id === postId);
      const existingReaction = post.reactions[reactionType];

      if (existingReaction) {
        await api.delete("community/unreact", {
          data: { post_id: postId, player_id: playerId },
        });
      } else {
        await api.post("community/react", {
          post_id: postId,
          player_id: playerId,
          reaction_type: reactionType,
        });
      }

      posts.value = posts.value.map((p) =>
        p.id === postId
          ? {
              ...p,
              reactions: {
                ...p.reactions,
                [reactionType]: existingReaction ? undefined : (p.reactions[reactionType] || 0) + 1,
              },
            }
          : p
      );
    } catch (error) {
      console.error("Error al manejar la reacción:", error);
    }
  };

  return { isMenuVisible, toggleMenu, setReaction };
}
