import { supabase } from "../supabase";

export const getClubPaymentOrders = async (club_id) => {
    const { data, error } = await supabase
      .from("payment_orders")
      .select("id, order_date, total_amount, payment_method, payment_status, transaction_id, event_type, event_id, club_commission, player_commission, is_full_payment, recipient_id")
      .eq("recipient_id", club_id)
  
    if (error) throw new Error(error.message);
    return data;
  };

export const getClubPaymentOrdersWithFilters = async (club_id, startDate = null, endDate = null, eventType = null) => {
  let query = supabase
    .from("payment_orders")
    .select(`
      id, order_date, total_amount, payment_method, payment_status, 
      transaction_id, event_type, event_id, club_commission, player_commission, 
      is_full_payment, recipient_id, user_id,
      profiles!payment_orders_user_id_fkey(full_name)
    `)
    .eq("recipient_id", club_id)
    .eq("payment_status", "approved");

  if (startDate && endDate) {
    query = query.gte("order_date", startDate).lte("order_date", endDate);
  } else if (startDate) {
    query = query.gte("order_date", startDate);
  }

  if (eventType) {
    query = query.eq("event_type", eventType);
  }

  const { data, error } = await query.order("order_date", { ascending: false });

  if (error) throw new Error(error.message);
  return data;
};

export const getClubPaymentSummary = async (club_id, startDate = null, endDate = null) => {
  let query = supabase
    .from("payment_orders")
    .select("total_amount, club_commission, player_commission, order_date")
    .eq("recipient_id", club_id)
    .eq("payment_status", "approved");

  if (startDate && endDate) {
    query = query.gte("order_date", startDate).lte("order_date", endDate);
  } else if (startDate) {
    query = query.gte("order_date", startDate);
  }

  const { data, error } = await query;

  if (error) throw new Error(error.message);
  return data;
};