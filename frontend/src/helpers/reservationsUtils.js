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
  console.log(context);
  const { baseData, extraData, selectedProducts, paymentOrderId, totalAmount, amountToPay, itemDetails } = context;
  console.log(baseData);
  // 1. Validar datos necesarios del contexto
  if (!baseData || !extraData || !paymentOrderId) {
      console.error("Faltan datos base/extra/paymentOrder para finalizar reserva (Util)", context);
      if ($q) $q.notify({ type: 'negative', message: 'Error interno al finalizar la reserva (datos faltantes Util).' });
      return { success: false };
  }

  // 2. Preparar payload para la API /reservations
  try {
      const paymentData = {
        payment_order_id: paymentOrderId,
        payment_method: paymentIntent.payment_method,
        payment_status: paymentIntent.status,
        transaction_id: paymentIntent.id,
        is_full_payment: extraData.paymentOption === "total"
      }

      const paymentResponse = await api.post("/payments/process-stripe-payment", paymentData);
      console.log(paymentResponse)
      if (!paymentResponse.data.success) {
        throw new Error(paymentResponse.data.message || "Error al actualizar el estado del pago.");
      }
      console.log('2',paymentResponse)


      const additionalItems = (selectedProducts || []).map((item) => ({
          name: item.product.name,
          price: item.product.price,
          quantity: item.quantity,
      }));

      const reservationDate = extraData.date;
      const startTime = extraData.time;
      const duration = extraData.duration;

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
