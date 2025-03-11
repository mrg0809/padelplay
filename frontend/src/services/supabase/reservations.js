import { supabase } from "../supabase";

export const fetchReservations = async (selectedDate, clubId) => {
    const { data, error } = await supabase
      .from("reservations")
      .select(`
          start_time,
          end_time,
          court_id,
          player_id,
          total_price,
          is_paid,
          courts(name),
          profiles(full_name),
          payment_orders(total_amount, payment_status, club_commission, player_commission, additional_items)
      `)
      .eq("reservation_date", selectedDate)
      .eq("courts.club_id", clubId);
  
    if (error) throw new Error(error.message);
    return data;
  };