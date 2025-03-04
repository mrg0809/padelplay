import { ref } from "vue";
import { getClubDetails } from "../services/supabase/clubs";
import { getTournamentsByClub } from "../services/supabase/tournaments";
import { fetchClubPosts } from "../services/api/community"; 
import L from "leaflet";
import { extractCoordinates } from "../helpers/clubUtils";

export function useClub() {
  const clubDetails = ref(null);
  const tournaments = ref([]);
  const posts = ref([]);
  const loading = ref(false);
  const coordinates = ref(null);
  const map = ref(null);

  const fetchClubData = async (clubId) => {
    loading.value = true;
    try {
      const data = await getClubDetails(clubId);
      clubDetails.value = data;
      
      const tournamentData = await getTournamentsByClub(clubId);
      tournaments.value = tournamentData;

      const postsData = await fetchClubPosts(clubId);
      posts.value = postsData;
    } catch (error) {
      console.error("Error fetching club data:", error);
    } finally {
      // Extract coordinates after all data is loaded
      coordinates.value = extractCoordinates(clubDetails.value);
      loading.value = false;
    }
  };

  const initMap = () => {
    if (!coordinates.value || !coordinates.value.lat) {
     console.log("No coordinates available for map");
     return;
   }
   console.log("Initializing map with coordinates:", coordinates.value);
   setTimeout(() => {
     const mapElement = document.getElementById("map");
     if (mapElement && !mapElement._leaflet_id) {
       map.value = L.map("map").setView([coordinates.value.lat, coordinates.value.lng], 15);
       L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
         attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
       }).addTo(map.value);

       // Add marker for the club location
       L.marker([coordinates.value.lat, coordinates.value.lng]).addTo(map.value)
         .bindPopup(clubDetails.value.name)
         .openPopup();
     }
   }, 100);
  };

  return {
    clubDetails,
    tournaments,
    posts,
    loading,
    coordinates,
    map,
    fetchClubData,
    initMap,
  };
}
