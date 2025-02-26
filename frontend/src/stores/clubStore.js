// src/stores/clubStore.js
import { defineStore } from "pinia";
import { generateDays } from "@/utils/dateUtils";
import { getClubDetails } from "@/services/supabase/clubs";
import { getTournamentsByClub } from "@/services/supabase/tournaments";
import { getPostsByClub } from "@/services/supabase/community";
import L from "leaflet";

export const useClubStore = defineStore("club", {
  state: () => ({
    clubDetails: null,
    tournaments: [],
    posts: [],
    loading: false,
    coordinates: null,
    days: generateDays(new Date()),
  }),

  actions: {
    async fetchClubDetails(clubId) {
      this.loading = true;
      try {
        const data = await getClubDetails(clubId);
        if (data) {
          this.clubDetails = data;
          this.coordinates = data.geolocation?.coordinates
            ? { lat: data.geolocation.coordinates[1], lng: data.geolocation.coordinates[0] }
            : data.latitude && data.longitude
            ? { lat: data.latitude, lng: data.longitude }
            : null;
        }
      } catch (error) {
        console.error("Error al obtener detalles del club:", error.message);
      } finally {
        this.loading = false;
      }
    },

    async fetchTournaments(clubId) {
      try {
        this.tournaments = await getTournamentsByClub(clubId);
      } catch (error) {
        console.error("Error al obtener torneos:", error.message);
      }
    },

    async fetchPosts(clubId) {
      try {
        this.posts = await getPostsByClub(clubId);
      } catch (error) {
        console.error("Error al obtener posts:", error);
      }
    },

    initMap() {
      if (!this.coordinates) return;
      setTimeout(() => {
        const mapElement = document.getElementById("map");
        if (mapElement && !mapElement._leaflet_id) {
          L.map("map").setView([this.coordinates.lat, this.coordinates.lng], 13);
        }
      }, 100);
    },
  },
});
