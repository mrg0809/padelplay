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
  
  // New approach: Query payments by linking through event_id for reservations
  // The event_id should contain the reservation.id when event_type is 'reservation'
  try {
    let baseQuery = supabase
      .from("payment_orders")
      .select(`
        id, order_date, total_amount, payment_method, payment_status, 
        transaction_id, event_type, event_id, club_commission, player_commission, 
        is_full_payment, recipient_id, user_id,
        profiles(full_name),
        reservations(id, court_id, reservation_date, start_time, end_time, courts(id, name, club_id))
      `)
      .eq("event_type", "reservation");

    // Apply date filters
    if (startDate && endDate) {
      baseQuery = baseQuery.gte("order_date", startDate).lte("order_date", endDate);
    } else if (startDate) {
      baseQuery = baseQuery.gte("order_date", startDate);
    }

    const { data: allReservationPayments, error: reservationError } = await baseQuery.order("order_date", { ascending: false });
    
    if (reservationError) {
      console.log('ERROR in reservation payments query:', reservationError);
    }
    
    console.log('DEBUG: All reservation payments before filtering:', allReservationPayments);
    
    // Filter the results to only include payments for reservations at this club's courts
    const clubPayments = allReservationPayments ? allReservationPayments.filter(payment => 
      payment.reservations && payment.reservations.courts && payment.reservations.courts.club_id === club_id
    ) : [];
    
    console.log('DEBUG: Filtered club payments:', clubPayments);
    
    // If we want specific event types, filter further
    if (eventType && eventType !== 'reservation') {
      // For non-reservation event types, try the original approach
      let query = supabase
        .from("payment_orders")
        .select(`
          id, order_date, total_amount, payment_method, payment_status, 
          transaction_id, event_type, event_id, club_commission, player_commission, 
          is_full_payment, recipient_id, user_id,
          profiles(full_name)
        `)
        .eq("recipient_id", club_id)
        .eq("event_type", eventType);
        
      // Apply date filters
      if (startDate && endDate) {
        query = query.gte("order_date", startDate).lte("order_date", endDate);
      } else if (startDate) {
        query = query.gte("order_date", startDate);
      }
      
      const { data: nonReservationData, error: nonReservationError } = await query.order("order_date", { ascending: false });
      
      if (nonReservationError) {
        console.log('ERROR in non-reservation query:', nonReservationError);
        return clubPayments; // Return reservation payments as fallback
      }
      
      return nonReservationData || [];
    }
    
    return clubPayments;
    
  } catch (error) {
    console.error('ERROR in getClubPaymentOrdersWithFilters:', error);
    return [];
  }
};

export const getClubPaymentSummary = async (club_id, startDate = null, endDate = null) => {
  try {
    // Use the same approach as the filtered function
    let baseQuery = supabase
      .from("payment_orders")
      .select(`
        total_amount, club_commission, player_commission, order_date, payment_status,
        reservations(id, courts(club_id))
      `)
      .eq("event_type", "reservation")
      .eq("payment_status", "approved");

    // Apply date filters
    if (startDate && endDate) {
      baseQuery = baseQuery.gte("order_date", startDate).lte("order_date", endDate);
    } else if (startDate) {
      baseQuery = baseQuery.gte("order_date", startDate);
    }

    const { data: allReservationPayments, error } = await baseQuery;
    
    if (error) {
      console.log('ERROR in payment summary query:', error);
      return [];
    }
    
    // Filter to only include payments for this club's courts
    const clubPayments = allReservationPayments ? allReservationPayments.filter(payment => 
      payment.reservations && payment.reservations.courts && payment.reservations.courts.club_id === club_id
    ) : [];
    
    console.log('DEBUG: Payment summary - filtered club payments:', clubPayments);
    
    return clubPayments;
    
  } catch (error) {
    console.error('ERROR in getClubPaymentSummary:', error);
    return [];
  }
};