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
  
  try {
    // Step 1: Get all reservation payments first
    let baseQuery = supabase
      .from("payment_orders")
      .select(`
        id, order_date, total_amount, payment_method, payment_status, 
        transaction_id, event_type, event_id, club_commission, player_commission, 
        is_full_payment, recipient_id, user_id
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
      return [];
    }
    
    console.log('DEBUG: All reservation payments before filtering:', allReservationPayments);
    
    if (!allReservationPayments || allReservationPayments.length === 0) {
      console.log('DEBUG: No reservation payments found');
      return [];
    }
    
    // Step 2: For each payment, get the reservation details
    const paymentIds = allReservationPayments.map(p => p.event_id).filter(Boolean);
    
    if (paymentIds.length === 0) {
      console.log('DEBUG: No event_ids found in reservation payments');
      return [];
    }
    
    console.log('DEBUG: Looking for reservations with IDs:', paymentIds);
    
    // Get reservations that match these payment event_ids
    const { data: reservations, error: reservationFetchError } = await supabase
      .from("reservations")
      .select(`
        id, court_id, reservation_date, start_time, end_time,
        courts(id, name, club_id)
      `)
      .in("id", paymentIds);
      
    if (reservationFetchError) {
      console.log('ERROR fetching reservations:', reservationFetchError);
      return [];
    }
    
    console.log('DEBUG: Found reservations:', reservations);
    
    // Step 3: Filter reservations for this club and create lookup
    const clubReservations = reservations ? reservations.filter(r => 
      r.courts && r.courts.club_id === club_id
    ) : [];
    
    const clubReservationIds = new Set(clubReservations.map(r => r.id));
    
    console.log('DEBUG: Club reservations:', clubReservations);
    console.log('DEBUG: Club reservation IDs:', Array.from(clubReservationIds));
    
    // Step 4: Filter payments to only include those for club reservations
    const clubPayments = allReservationPayments.filter(payment => 
      clubReservationIds.has(payment.event_id)
    );
    
    console.log('DEBUG: Filtered club payments:', clubPayments);
    
    // Step 5: Get user data for the filtered payments from players table
    if (clubPayments.length > 0) {
      const userIds = [...new Set(clubPayments.map(p => p.user_id).filter(Boolean))];
      
      if (userIds.length > 0) {
        const { data: players, error: playersError } = await supabase
          .from("players")
          .select("user_id, first_name, last_name, email, phone, photo_url")
          .in("user_id", userIds);
          
        if (!playersError && players) {
          // Add player data to payments
          const playerLookup = {};
          players.forEach(player => {
            // Create a profile-like object for compatibility
            playerLookup[player.user_id] = {
              id: player.user_id,
              full_name: `${player.first_name || ''} ${player.last_name || ''}`.trim(),
              email: player.email,
              phone: player.phone,
              photo_url: player.photo_url
            };
          });
          
          clubPayments.forEach(payment => {
            if (payment.user_id && playerLookup[payment.user_id]) {
              payment.profiles = playerLookup[payment.user_id];
            }
          });
        } else if (playersError) {
          console.log('ERROR fetching player data:', playersError);
        }
      }
      
      // Add reservation data to payments
      const reservationLookup = {};
      clubReservations.forEach(reservation => {
        reservationLookup[reservation.id] = reservation;
      });
      
      clubPayments.forEach(payment => {
        if (payment.event_id && reservationLookup[payment.event_id]) {
          payment.reservations = reservationLookup[payment.event_id];
        }
      });
    }
    
    console.log('DEBUG: Final club payments with profile and reservation data:', clubPayments);
    
    // Handle non-reservation event types if specified
    if (eventType && eventType !== 'reservation') {
      // For non-reservation event types, try the original approach
      let query = supabase
        .from("payment_orders")
        .select(`
          id, order_date, total_amount, payment_method, payment_status, 
          transaction_id, event_type, event_id, club_commission, player_commission, 
          is_full_payment, recipient_id, user_id
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
    // Use the same step-by-step approach as the main function
    let baseQuery = supabase
      .from("payment_orders")
      .select(`
        total_amount, club_commission, player_commission, order_date, payment_status, event_id
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
    
    if (!allReservationPayments || allReservationPayments.length === 0) {
      return [];
    }
    
    // Get reservations for these payments
    const paymentIds = allReservationPayments.map(p => p.event_id).filter(Boolean);
    
    if (paymentIds.length === 0) {
      return [];
    }
    
    const { data: reservations, error: reservationError } = await supabase
      .from("reservations")
      .select(`
        id,
        courts(club_id)
      `)
      .in("id", paymentIds);
      
    if (reservationError) {
      console.log('ERROR fetching reservations for summary:', reservationError);
      return [];
    }
    
    // Filter to only include payments for this club's courts
    const clubReservationIds = new Set(
      reservations ? reservations
        .filter(r => r.courts && r.courts.club_id === club_id)
        .map(r => r.id)
      : []
    );
    
    const clubPayments = allReservationPayments.filter(payment => 
      clubReservationIds.has(payment.event_id)
    );
    
    console.log('DEBUG: Payment summary - filtered club payments:', clubPayments);
    
    return clubPayments;
    
  } catch (error) {
    console.error('ERROR in getClubPaymentSummary:', error);
    return [];
  }
};