<template>
  <q-list bordered class="q-mt-md">
    <q-item v-for="post in posts" :key="post.id" class="q-mb-sm post">
      <q-item-section>
        <q-item-label>{{ post.content }}</q-item-label>
        <q-item-label caption>{{ formatDateString(post.created_at) }}</q-item-label>
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
import { ref, computed } from "vue";
import { useReactions } from "src/composables/useReactions";
import { formatDateString } from "src/helpers/dateUtils";

export default {
  props: {
    posts: Array,
    reactionEmojis: Object,
    selectedReaction: String,
    playerId: String,
  },
  emits: ["update:posts"],
  setup(props, { emit }) {
    const posts = ref(props.posts);
    const { isMenuVisible, toggleMenu, setReaction } = useReactions(posts, props.playerId);

    return {
      isMenuVisible,
      toggleMenu,
      formatDateString,
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
