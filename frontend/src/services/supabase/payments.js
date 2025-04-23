import { supabase } from "../supabase";

export const getClubPaymentOrders = async (user_id) => {
    const { data, error } = await supabase
      .from("payment_orders")
      .select("id, order_date, total_amount, payment_method, payment_status, transaction_id, event_type, event_id, club_comission, player_comission, is_full_payment")
      .eq("user_id", recipient_id)
  
    if (error) throw new Error(error.message);
    return data;
  };