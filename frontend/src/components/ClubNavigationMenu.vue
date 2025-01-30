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
          { name: "inicio", label: "Inicio", icon: "o_home" },
          { name: "agenda", label: "agenda", icon: "o_calendar_month" },
          { name: "perfil", label: "Perfil", icon: "o_account_circle" },
        ],
      };
    },
    methods: {
      onTabChange(tabName) {
        this.$router.push(`/club/${tabName}`);
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
    