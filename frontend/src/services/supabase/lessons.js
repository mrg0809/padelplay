import { supabase } from "../supabase";

export const getLessonDetails = async (lessonId) => {
    const { data, error } = await supabase
      .from("lessons")
      .select("id, name, description, court_id, duration, coach, lesson_date, lesson_time, price, coaches(name), players")
      .eq("id", lessonId);
  
    if (error) throw new Error(error.message);
    return data;
  };


export const getPrivateLessonDeatails = async (lessonId) => {
  const { data: lessonData, error } = await supabase
    .from("lessons")
    .select("id, club_id, court_id, coach, players, participants, lesson_date, lesson_time, price, coaches(name), clubs(name, latitude, longitude), courts(name), payment_orders(total_amount, payment_status, additional_items, is_full_payment)")
    .eq("id", lessonId)
    .single();

  if (error) throw new Error(error.message);

  const playerIds = lessonData.players;
  
  let playerDetails = [];
  
  if (playerIds?.length > 0) {
    const { data: playersData, error: playersError } = await supabase
      .from("players")
      .select("user_id, first_name, last_name, photo_url")
      .in("user_id", playerIds);

    if (playersError) throw new Error(playersError.message);

    playerDetails = playersData;
  }
  return {
    ...lessonData,
    playerDetails,
  }
};


export const getPlayerLessonPhotos = async (players) => {
  const { data, error } = await supabase
    .from("players")
    .select("user_id, photo_url")
    .in("user_id", players);

  if (error) throw new Error(error.message);
  return data;
};
