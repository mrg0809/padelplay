import { supabase } from "../supabase";

export const fetchAvailableCourts = async (clubId, date) => {
  try {
    const { data, error } = await supabase
      .from("courts")
      .select("*")
      .eq("club_id", clubId)
      .gte("available_date", date);
      
    if (error) throw error;
    return data;
  } catch (error) {
    console.error("Error al obtener canchas:", error.message);
    return [];
  }
};