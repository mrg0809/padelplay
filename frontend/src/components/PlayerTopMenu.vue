<template>
    <q-btn flat round dense icon="menu" @click="onMenu" />
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