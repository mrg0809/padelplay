import { supabase } from "../supabase";

export const getTournamentsByClub = async (clubId) => {
  const { data, error } = await supabase
    .from("tournaments")
    .select("id, name, start_date, category, gender")
    .eq("club_id", clubId);

  if (error) throw Error(error.message);
  return data || [];
}


export const fetchTournaments = async (filters) => {
  let query = supabase.from("tournaments").select("*");

  if (filters.city) {
    query = query.eq("city", filters.city);
  }
  if (filters.category) {
    query = query.eq("category", filters.category);
  }
  if (filters.gender) {
    query = query.eq("gender", filters.gender);
  }

  const { data, error } = await query;

  if (error) {
    console.error("Error fetching tournaments:", error);
    return [];
  }

  return data;
};

