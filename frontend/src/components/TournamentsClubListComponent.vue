<template>
    <div class="q-mt-md tournament-list">
      <div
        v-for="tournament in tournaments"
        :key="tournament.id"
        class="tournament-card"
        @click="goToTournamentDetails(tournament.id)"
      >
        <h5>{{ tournament.name }}</h5>
        <p>Fecha: {{ tournament.start_date }}</p>
        <p>Categoría: {{ tournament.category }}</p>
        <p>Género: {{ tournament.gender }}</p>
      </div>
      <p v-if="!tournaments.length" class="text-center q-mt-md">
        No hay torneos disponibles en este club.
      </p>
    </div>
  </template>
  
  <script>
  export default {
    props: {
      tournaments: Array,
    },
    methods: {
      goToTournamentDetails(tournamentId) {
        this.$emit('go-to-tournament-details', tournamentId);
      },
    },
  };
  </script>
  
  <style scoped>
  .tournament-list {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 16px;
  }
  
  .tournament-card {
    background-image: url(src/assets/texturafondo.png);
    background-size: cover;
    padding: 16px;
    border-radius: 8px;
    cursor: pointer;
    transition: transform 0.3s, box-shadow 0.3s;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  }
  
  .tournament-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
  }
  
  .tournament-card h5 {
    margin: 0 0 8px;
    color: #ffd700;
  }
  
  .tournament-card p {
    margin: 4px 0;
    color: #ccc;
  }
  </style>