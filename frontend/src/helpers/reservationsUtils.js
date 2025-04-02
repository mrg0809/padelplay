import { endtime_calculate } from "./hourUtils";

export function getCourtPrice(court, duration) {
  if (!court) return 0;
  const prices = {
    60: court.price_per_hour || 0,
    90: court.price_per_hour_and_half || 0,
    120: court.price_per_two_hour || 0,
  };
  return prices[duration] || 0;
}


export async function finalizeCourtReservationUtil(paymentIntent, context, api, $q) {
  console.log("Finalizando reserva de cancha post-pago exitoso (Util)...");
  const { baseData, extraData, selectedProducts, paymentOrderId, totalAmount, amountToPay } = context;

  // 1. Validar datos necesarios del contexto
  if (!baseData || !extraData || !paymentOrderId) {
      console.error("Faltan datos base/extra/paymentOrder para finalizar reserva (Util)", context);
      // $q might not be available if not passed, handle differently or ensure it's passed
      if ($q) $q.notify({ type: 'negative', message: 'Error interno al finalizar la reserva (datos faltantes Util).' });
      return { success: false };
  }

  // 2. Preparar payload para la API /reservations
  try {
      const additionalItems = (selectedProducts || []).map((item) => ({
          name: item.product.name,
          price: item.product.price,
          quantity: item.quantity,
      }));

      const reservationDate = extraData.date || baseData.date;
      const startTime = extraData.time || baseData.time;
      const duration = extraData.duration || 60;

      if (!reservationDate || !startTime) {
          throw new Error("Falta la fecha o la hora de inicio en los datos extra/base.");
      }

      const endTime = endtime_calculate(startTime, duration);
      const payTotal = extraData.paymentOption === "total"; // Assumes paymentOption is in extraData

      const reservationData = {
          club_id: baseData.clubId,
          court_id: baseData.id,
          reservation_date: reservationDate,
          start_time: startTime,
          end_time: endTime,
          total_price: totalAmount, // Use totalAmount directly
          pay_total: payTotal,
          club_commission: 0,
          player_commission: 0,
          additional_items: additionalItems,
          payment_order_id: paymentOrderId,
          payment_intent_id: paymentIntent.id,
          payment_status: paymentIntent.status, // 'succeeded'
          is_public_match: extraData.isPublicMatch || false,
      };

      console.log("Payload final para POST /reservations (Util):", reservationData);

      // 3. Llamar a la API (needs 'api' instance)
      const response = await api.post("/reservations", reservationData);

      // 4. Validar respuesta
      const matchId = response.data?.match_id;
      if (!matchId) {
          console.warn("API /reservations no devolvió un match_id (Util):", response.data);
          throw new Error("No se pudo confirmar la creación del partido asociado.");
      }

      console.log("Reserva de cancha confirmada en backend (Util). Match ID:", matchId);

      // 5. Devolver éxito y datos
      return { success: true, matchId: matchId };

  } catch (error) {
      console.error("Error en finalizeCourtReservationUtil API call:", error);
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || error.message || "Error al confirmar la reserva en nuestro sistema.";
       // Use $q if available
       if ($q) $q.notify({ type: 'negative', message: `El pago se realizó, pero hubo un problema al guardar tu reserva: ${errorMessage}` });
      return { success: false };
  }
}
