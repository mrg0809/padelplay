import { supabase } from "../supabase";

//Buscar clubs por geolocation o por nombre
export const searchClubs = async (query, userLocation = null) => {
  try {
    if (query.trim()) {
      // Buscar por nombre
      const { data, error } = await supabase
        .from("clubs")
        .select("id, name, address, logo_url")
        .ilike("name", `%${query}%`);
      if (error) throw error;
      return data.map((club) => ({
        id: club.id,
        name: club.name,
        address: club.address,
        logo_url: club.logo_url,
      }));
    } else if (userLocation) {
      // Buscar por geolocalización
      const { latitude, longitude } = userLocation;
      const { data, error } = await supabase.rpc("calculate_distance", {
        lat: latitude,
        lng: longitude,
      });
      if (error) throw error;
      return data.map((club) => ({
        id: club.club_id,
        name: club.name,
        address: club.address,
        logo_url: club.logo_url,
        distance: club.distance,
      }));
    } else {
      return [];
    }
  } catch (error) {
    console.error("Error fetching clubs:", error.message);
    throw error;
  }
};

export async function getClubDetails(clubId) {
  try {
    const { data: clubData, error } = await supabase
      .from('clubs')
      .select("*")
      .eq("id", clubId)
      .single();

    if (error) {
      console.error("Error fetching club details:", error);
      throw error;
    }

    if (clubData && Object.keys(clubData).length > 0) {
      return clubData;
    } else {
      console.log("No club details found for ID:", clubId);
      return null;
    }
  } catch (error) {
    console.error("Error fetching club details:", error);
    throw error;
  }
}


export const fetchScheduleHours = async (clubId) => {
  const { data, error } = await supabase
    .from("schedules")
    .select("opening_time, closing_time")
    .eq("club_id", clubId);

  if (error) throw new Error(error.message);
  return data;
};


export async function fetchFirstClubs(limit = 10) {
  console.log(`Workspaceing first ${limit} clubs...`); // Log for debugging
  const { data, error } = await supabase
    .from('clubs')
    .select(`
      id,
      name,
      address,
      logo_url
      // Add other fields needed for the list display
    `)
    .order('name', { ascending: true }) // Order by name, for example
    .limit(limit);

  if (error) {
    console.error('Error fetching first clubs:', error);
    throw new Error(`Supabase error: ${error.message}`);
  }

  console.log('First clubs data:', data); // Log fetched data
  return data || []; // Return data or empty array
}