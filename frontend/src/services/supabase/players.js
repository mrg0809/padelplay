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

export const searchPlayers = async (query) => {
  const { data, error } = await supabase
    .from('players')
    .select('user_id, first_name, last_name, email, phone, photo_url, category')
    .or(`first_name.ilike.%${query}%,last_name.ilike.%${query}%,email.ilike.%${query}%,phone.ilike.%${query}%`)
    .not('email', 'is', null); // Filter out players without email

  if (error) {
    throw error;
  }

  return data;
};