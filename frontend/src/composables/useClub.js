import { ref } from "vue";
import { getClubDetails } from "@/services/supabase/clubs";
import { getTournamentsByClub } from "@/services/supabase/tournaments";
import { fetchClubPosts } from "@/services/api/community";
import L from "leaflet";

export function useClub() {
  const clubDetails = ref(null);
  const tournaments = ref([]);
  const posts = ref([]);
  const loading = ref(false);
  const coordinates = ref(null);

  const fetchClubData = async (clubId) => {
    loading.value = true;
    try {
      clubDetails.value = await getClubDetails(clubId);
      tournaments.value = await getTournamentsByClub(clubId);
      posts.value = await fetchClubPosts(clubId);
      
      if (clubDetails.value?.geolocation?.coordinates) {
        coordinates.value = {
          lat: clubDetails.value.geolocation.coordinates[1],
          lng: clubDetails.value.geolocation.coordinates[0],
        };
      } else if (clubDetails.value?.latitude && clubDetails.value?.longitude) {
        coordinates.value = {
          lat: clubDetails.value.latitude,
          lng: clubDetails.value.longitude,
        };
      }
    } catch (error) {
      console.error("Error fetching club data:", error);
    } finally {
      loading.value = false;
    }
  };

  const initMap = () => {
    if (!coordinates.value) return;
    setTimeout(() => {
      const mapElement = document.getElementById("map");
      if (mapElement && !mapElement._leaflet_id) {
        const map = L.map("map").setView([coordinates.value.lat, coordinates.value.lng], 15);
        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
          attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        }).addTo(map);

        L.marker([coordinates.value.lat, coordinates.value.lng]).addTo(map)
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
    fetchClubData,
    initMap,
  };
}
