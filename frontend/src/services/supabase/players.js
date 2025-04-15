import { supabase } from "../supabase";

export async function fetchPlayer(userId) {
  try {
    const { data, error } = await supabase
    .from("players")
    .select("*")
    .eq("user_id", userId)
    .single();
    
    if (error) throw error;
    return data;
  } catch (err) {
    console.error("Error al obtener datos del jugador:", err.message);
    return null;
  }
}
