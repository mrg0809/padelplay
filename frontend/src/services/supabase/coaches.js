import { supabase } from "../supabase";

export const getCoachesByClub = async (clubId) => {
    const { data, error } = await supabase
      .from("coaches")
      .select("id, name, coach_focus, players(photo_url)")
      .eq("club_id", clubId);
  
    if (error) throw Error(error.message);
    return data || [];
  }

  export const getCoachDetails = async (coachId, clubId) => {
    const { data, error } = await supabase
      .from("coaches")
      .select("*, players(photo_url)")
      .eq("id", coachId)
      .eq("club_id", clubId)
      .single();
  
    if (error) {
      throw error;
    }
  
    return data;
  }