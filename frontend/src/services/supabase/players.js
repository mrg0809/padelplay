import { supabase } from "../supabase";

export async function fetchPlayer() {
  try {
    const { data, error } = await supabase.from("players").select("*").single();
    if (error) throw error;
    return data;
  } catch (err) {
    console.error("Error al obtener datos del jugador:", err.message);
    return null;
  }
}
