import { supabase } from "../supabase";

/**
 * Debug function to understand payment_orders structure and relationships
 */
export const debugPaymentOrders = async () => {
  console.log('=== DEBUG: Payment Orders Analysis ===');
  
  // 1. Get sample payment_orders to understand structure
  const { data: samplePayments, error: sampleError } = await supabase
    .from("payment_orders")
    .select("*")
    .limit(10);
  
  console.log('Sample payment_orders:', { samplePayments, sampleError });
  
  // 2. Check unique values in key fields
  const { data: recipientIds, error: recipientError } = await supabase
    .from("payment_orders")
    .select("recipient_id")
    .not("recipient_id", "is", null);
    
  console.log('Unique recipient_ids in payment_orders:', { recipientIds, recipientError });
  
  // 3. Check event_types
  const { data: eventTypes, error: eventError } = await supabase
    .from("payment_orders")
    .select("event_type")
    .not("event_type", "is", null);
    
  console.log('Event types in payment_orders:', { eventTypes, eventError });
  
  // 4. Check payment_status values
  const { data: statuses, error: statusError } = await supabase
    .from("payment_orders")
    .select("payment_status")
    .not("payment_status", "is", null);
    
  console.log('Payment statuses in payment_orders:', { statuses, statusError });
  
  // 5. Try to understand user_id to profiles relationship
  const { data: userProfiles, error: profileError } = await supabase
    .from("payment_orders")
    .select(`
      user_id,
      profiles(id, full_name, email)
    `)
    .limit(5);
    
  console.log('Payment orders with profile data:', { userProfiles, profileError });
  
  return {
    samplePayments,
    recipientIds,
    eventTypes,
    statuses,
    userProfiles
  };
};

/**
 * Try different approaches to find club-related payments
 */
export const debugClubPaymentApproaches = async (clubId) => {
  console.log('=== DEBUG: Club Payment Approaches for clubId:', clubId, '===');
  
  // Approach 1: Filter by recipient_id
  const { data: approach1, error: error1 } = await supabase
    .from("payment_orders")
    .select("*")
    .eq("recipient_id", clubId)
    .limit(5);
    
  console.log('Approach 1 - recipient_id filter:', { approach1, error1 });
  
  // Approach 2: Join with reservations and courts
  const { data: approach2, error: error2 } = await supabase
    .from("payment_orders")
    .select(`
      *,
      reservations!inner(id, court_id, courts!inner(id, club_id))
    `)
    .eq("reservations.courts.club_id", clubId)
    .eq("event_type", "reservation")
    .limit(5);
    
  console.log('Approach 2 - reservations/courts join:', { approach2, error2 });
  
  // Approach 3: Check if there are any payments at all
  const { data: anyPayments, error: anyError } = await supabase
    .from("payment_orders")
    .select("*")
    .limit(5);
    
  console.log('Approach 3 - any payments exist:', { anyPayments, anyError });
  
  // Approach 4: Check clubs table to see if club_id is valid
  const { data: clubCheck, error: clubError } = await supabase
    .from("clubs")
    .select("*")
    .eq("id", clubId);
    
  console.log('Approach 4 - club validity check:', { clubCheck, clubError });
  
  // Approach 5: Check if there are courts for this club
  const { data: courtsCheck, error: courtsError } = await supabase
    .from("courts")
    .select("*")
    .eq("club_id", clubId)
    .limit(3);
    
  console.log('Approach 5 - courts for this club:', { courtsCheck, courtsError });
  
  // Approach 6: Check reservations for this club
  const { data: reservationsCheck, error: reservationsError } = await supabase
    .from("reservations")
    .select(`
      *,
      courts!inner(club_id)
    `)
    .eq("courts.club_id", clubId)
    .limit(3);
    
  console.log('Approach 6 - reservations for this club:', { reservationsCheck, reservationsError });
  
  return {
    approach1,
    approach2,
    anyPayments,
    clubCheck,
    courtsCheck,
    reservationsCheck
  };
};