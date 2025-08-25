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
  console.log('DEBUG: getClubPaymentOrdersWithFilters called with:', { club_id, startDate, endDate, eventType });
  
  // First, let's check what payment_orders exist and their structure
  const debugQuery = supabase
    .from("payment_orders")
    .select("*")
    .limit(10);
    
  const { data: debugData, error: debugError } = await debugQuery;
  console.log('DEBUG: Sample payment_orders data:', { debugData, debugError });
  
  // Let's also check if there are any payment_orders with recipient_id matching our club_id
  const recipientDebugQuery = supabase
    .from("payment_orders")
    .select("*")
    .eq("recipient_id", club_id)
    .limit(5);
    
  const { data: recipientDebugData, error: recipientDebugError } = await recipientDebugQuery;
  console.log('DEBUG: Payment orders with recipient_id matching club_id:', { recipientDebugData, recipientDebugError });
  
  // Check if we should try filtering by event_id and joining with reservations/courts to find club-related payments
  if (!recipientDebugData || recipientDebugData.length === 0) {
    console.log('DEBUG: No payments found with recipient_id, trying alternative approach via reservations...');
    
    // Alternative approach: Find payments for reservations at this club's courts
    const reservationPaymentsQuery = supabase
      .from("payment_orders")
      .select(`
        id, order_date, total_amount, payment_method, payment_status, 
        transaction_id, event_type, event_id, club_commission, player_commission, 
        is_full_payment, recipient_id, user_id,
        profiles!payment_orders_user_id_fkey(full_name),
        reservations!inner(id, court_id, courts!inner(club_id))
      `)
      .eq("reservations.courts.club_id", club_id)
      .eq("event_type", "reservation");
      
    if (startDate && endDate) {
      reservationPaymentsQuery = reservationPaymentsQuery.gte("order_date", startDate).lte("order_date", endDate);
    } else if (startDate) {
      reservationPaymentsQuery = reservationPaymentsQuery.gte("order_date", startDate);
    }
    
    if (eventType === 'reservation') {
      // Already filtered above
    } else if (eventType) {
      // For non-reservation event types, still try recipient_id approach
      const { data, error } = await supabase
        .from("payment_orders")
        .select(`
          id, order_date, total_amount, payment_method, payment_status, 
          transaction_id, event_type, event_id, club_commission, player_commission, 
          is_full_payment, recipient_id, user_id,
          profiles!payment_orders_user_id_fkey(full_name)
        `)
        .eq("recipient_id", club_id)
        .eq("event_type", eventType)
        .order("order_date", { ascending: false });
        
      console.log('DEBUG: Alternative query for non-reservation events:', { data, error });
      return data || [];
    }

    const { data: altData, error: altError } = await reservationPaymentsQuery.order("order_date", { ascending: false });
    console.log('DEBUG: Alternative query via reservations join:', { altData, altError });
    
    if (altError) throw new Error(altError.message);
    return altData || [];
  }
  
  // Original approach if recipient_id data exists
  let query = supabase
    .from("payment_orders")
    .select(`
      id, order_date, total_amount, payment_method, payment_status, 
      transaction_id, event_type, event_id, club_commission, player_commission, 
      is_full_payment, recipient_id, user_id,
      profiles!payment_orders_user_id_fkey(full_name)
    `)
    .eq("recipient_id", club_id);

  if (startDate && endDate) {
    query = query.gte("order_date", startDate).lte("order_date", endDate);
  } else if (startDate) {
    query = query.gte("order_date", startDate);
  }

  if (eventType) {
    query = query.eq("event_type", eventType);
  }

  const { data, error } = await query.order("order_date", { ascending: false });
  
  console.log('DEBUG: Final query result:', { data, error, queryParams: { club_id, startDate, endDate, eventType } });

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