<template>
    <q-btn flat round dense icon="menu" @click="onMenu" />
</template>
  
  <script>
  
  export default {
    name: "ClubTopMenu",
    data() {
      return {
      };
    },
    methods: {
      onMenu() {
        this.$router.push("/club/topmenu");
      },
    },
  };
  </script>