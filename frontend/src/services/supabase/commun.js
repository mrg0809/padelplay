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