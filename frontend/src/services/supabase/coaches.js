import { supabase } from "../supabase";

export const getCoachesByClub = async (clubId) => {
    const { data, error } = await supabase
      .from("coaches")
      .select("id, name, coach_focus, players(photo_url)")
      .eq("club_id", clubId);
  
    if (error) throw Error(error.message);
    return data || [];
  }