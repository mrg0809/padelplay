import { supabase } from "../supabase";

export const fetchCourts = async (clubId) => {
    const { data, error } = await supabase
      .from("courts")
      .select("id, name")
      .eq("club_id", clubId);
  
    if (error) throw new Error(error.message);
    return data;
  };


export const fetchCourtPrices = async (courtId) => {
    const { data, error } = await supabase
    .from("courts")
    .select("id, name, price_per_hour, price_per_hour_and_half, price_per_two_hour")
    .eq("id", courtId);

  if (error) throw new Error(error.message);
  return data;
}