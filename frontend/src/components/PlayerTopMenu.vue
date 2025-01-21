<template>
    <q-btn flat round dense icon="o_menu" @click="onMenu" size="lg" />
</template>
  
  <script>
  
  export default {
    name: "PlayerTopMenu",
    data() {
      return {
      };
    },
    methods: {
      onMenu() {
        this.$router.push("/player/topmenu");
      },
    },
  };
  </script>