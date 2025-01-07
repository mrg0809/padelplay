<template>
  <q-footer class="bg-primary text-white">
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
        { name: "torneos", label: "Torneos", icon: "sports_tennis" },
        { name: "asociaciones", label: "Asociaciones", icon: "group" },
        { name: "perfil", label: "Perfil", icon: "account_circle" },
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
    position: fixed;
    bottom: 0;
    width: 100%;
  }
  </style>
  