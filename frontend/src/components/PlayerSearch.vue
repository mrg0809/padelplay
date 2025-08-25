<template>
    <q-dialog v-model="showDialog">
      <q-card style="min-width: 300px;" class="bg-black">
        <q-card-section>
          <div class="text-h6">Buscar Jugador</div>
          <q-input v-model="searchQuery" label="Nombre, Apellido, Email o Teléfono" outlined dense @update:model-value="searchPlayers" />
        </q-card-section>
        <q-list bordered separator v-if="searchResults.length > 0">
          <q-item v-for="player in searchResults" :key="player.id" clickable @click="selectPlayer(player)">
            <q-item-section avatar>
              <q-avatar size="48px">
                <img :src="player.photo_url" alt="Foto del jugador" style="border-radius: 50%;" />
              </q-avatar>
            </q-item-section>
            <q-item-section>
              <q-item-label>{{ player.first_name }} {{ player.last_name }}</q-item-label>
              <q-item-label caption>{{ player.category }}</q-item-label>
            </q-item-section>
          </q-item>
        </q-list>
        <q-card-actions align="right">
          <q-btn flat label="Cancelar" color="negative" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </template>
  
  <script setup>
  import { ref, watch } from 'vue';
  import { searchPlayers as searchPlayersService } from 'src/services/supabase/players';
  
  const props = defineProps({
    modelValue: Boolean,
  });
  
  const emit = defineEmits(['update:modelValue', 'playerSelected']);
  
  const showDialog = ref(props.modelValue);
  const searchQuery = ref('');
  const searchResults = ref([]);
  
  watch(() => props.modelValue, (val) => {
    showDialog.value = val;
  });
  
  watch(showDialog, (val) => {
    emit('update:modelValue', val);
    if (!val) {
      searchQuery.value = '';
      searchResults.value = [];
    }
  });
  
  const searchPlayers = async () => {
    if (searchQuery.value.trim() === '') {
      searchResults.value = [];
      return;
    }
    try {
      const results = await searchPlayersService(searchQuery.value);
      console.log('Search results from database:', results);
      searchResults.value = results;
    } catch (error) {
      console.error('Error al buscar jugadores:', error);
    }
  };
  
  const selectPlayer = (player) => {
    console.log('Player selected in PlayerSearch:', player);
    console.log('Player email:', player?.email);
    emit('playerSelected', player);
    showDialog.value = false;
  };
  </script>