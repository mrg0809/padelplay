export const finalizeClassBooking = async (paymentIntent, context, api, $q) => {
    console.log("Finalizando reserva de clase privada...");
    console.log('context:', context)

    const { baseData, extraData, selectedProducts, paymentOrderId, amountToPay } = context; // Asegúrate de tener 'context' disponible
    const { itemDetails } = context; // Asume que 'context' contiene itemDetails


    try {
        // --- **EXTRAER DATOS DE itemDetails** ---
        let lessonDate = null;
        let lessonTime = null;
        let duration = 60; // Valor por defecto

        const dateDetail = itemDetails.find(detail => detail.label === "Fecha");
        if (dateDetail) {
            lessonDate = dateDetail.value;
        }

        const timeDetail = itemDetails.find(detail => detail.label === "Horario");
        if (timeDetail) {
            lessonTime = timeDetail.value.split(' ')[0]; // o una lógica para obtener la hora sin "hrs."
        }

        const durationDetail = itemDetails.find(detail => detail.label === "Duración");
        if (durationDetail) {
            const durationValue = durationDetail.value.match(/\d+/);
            if (durationValue) {
                duration = parseInt(durationValue[0], 10);
            }
        }

        if (!lessonDate || !lessonTime) {
            throw new Error("Falta la fecha o la hora de la clase.");
        }


        const payload = {
            club_id: baseData.clubId,
            coach_id: baseData.id, // O donde tengas el ID del coach
            lesson_date: lessonDate,
            lesson_time: lessonTime,
            duration: duration,
            price_paid: amountToPay,
            participants: baseData.participants,
            payment_order_id: paymentOrderId,
            payment_intent_id: paymentIntent.id,
            additional_items: selectedProducts, // O una transformación si es necesaria
        };

        console.log("Payload para /lessons/private-booking:", payload);

        const response = await api.post("/lessons/private-booking", payload);

        if (response.data && response.data.booking_id) {
            console.log("Reserva de clase privada creada:", response.data);
            return { success: true, path: '/user/my-bookings' }; // Ruta a tu página de reservas
        } else {
            console.error("Error: No se recibió booking_id en la respuesta:", response);
            throw new Error("No se pudo confirmar la reserva de la clase privada.");
        }

    } catch (error) {
        console.error("Error en finalizeClassBooking:", error);
        $q.notify({
            type: 'negative',
            message: error.response?.data?.detail || error.message || "Error al confirmar la reserva de clase.",
        });
        return { success: false };
    }
};