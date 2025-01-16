<template>
  <q-footer class="text-white">
    <q-tabs align="justify" class="q-pa-xs" active-color="white" @update:model-value="onTabChange">
      <q-tab
        v-for="tab in tabs"
        :key="tab.name"
        :name="tab.name"
        :label="tab.label"
        :icon="tab.icon"
        class="text-white"
      />
    </q-tabs>
  </q-footer>
</template>

<script>
export default {
  data() {
    return {
      tabs: [
        { name: "inicio", label: "Inicio", icon: "home" },
        { name: "torneos", label: "Torneos", icon: "emoji_events" },
        { name: "reservas", label: "Reservas", icon: "event" },
        { name: "perfil", label: "Perfil", icon: "person_outline" },
      ],
    };
  },
  methods: {
    onTabChange(tabName) {
      this.$router.push(`/player/${tabName}`);
    },
  },
};
</script>

  
  <style scoped>
  .q-footer {
    background: #000000;
    position: fixed;
    bottom: 0;
    width: 100%;
  }
  </style>
  