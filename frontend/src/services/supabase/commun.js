import { supabase } from "../supabase";

export const fetchCities = async () => {
  try {
      const { data, error } = await supabase.rpc("get_unique_cities");
      if (error) {
          console.error("Error fetching cities:", error.message);
          return []; 
      }
      
      return data.map((city) => ({
          label: city,
          value: city,
      }));
  } catch (error) {
      console.error("Unexpected error fetching cities:", error.message);
      return []; 
  }
};

export const searchPlayersByName = async (searchQuery) => {
    try {
      if (!searchQuery || searchQuery.trim() === '') return [];
      const { data, error } = await supabase
        .from("players")
        .select("user_id, first_name, last_name, photo_url, category")
        .ilike("first_name", `%${searchQuery}%`);
  
      if (error) throw error;
      return data;
    } catch (error) {
      console.error("Error searching players:", error);
      throw error;
    }
  };