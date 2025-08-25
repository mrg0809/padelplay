export const finalizeClassBooking = async (paymentIntent, context, api, $q) => {
    console.log("Finalizando reserva de clase privada...");
    console.log('context:', context);

    const { baseData, extraData, selectedProducts, paymentOrderId, amountToPay, paymentOption } = context; // Incluir paymentOption
    const { itemDetails } = context;

    try {
        // Llamar a /process-stripe-payment antes de /lessons/private-booking
        const paymentData = {
            payment_order_id: paymentOrderId,
            payment_method: paymentIntent.payment_method,
            payment_status: paymentIntent.status,
            transaction_id: paymentIntent.id,
            is_full_payment: paymentOption === "total" // Usar paymentOption
        };
        const paymentResponse = await api.post("/payments/process-stripe-payment", paymentData);

        if (!paymentResponse.data || !paymentResponse.data.message) {
            throw new Error("Error al actualizar el estado del pago.");
        }

        // Añadimos un pequeño retraso antes de llamar a /lessons/private-booking
        await new Promise(resolve => setTimeout(resolve, 500));

        // --- EXTRAER DATOS DE itemDetails ---
        let lessonDate = null;
        let lessonTime = null;
        let duration = 60;

        const dateDetail = itemDetails.find(detail => detail.label === "Fecha");
        if (dateDetail) {
            lessonDate = dateDetail.value;
        }

        const timeDetail = itemDetails.find(detail => detail.label === "Horario");
        if (timeDetail) {
            lessonTime = timeDetail.value.split(' ')[0];
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
            coach_id: baseData.id,
            lesson_date: lessonDate,
            lesson_time: lessonTime,
            duration: duration,
            price_paid: amountToPay,
            participants: baseData.participants,
            payment_order_id: paymentOrderId,
            payment_intent_id: paymentIntent.id,
            additional_items: selectedProducts,
            pay_total: paymentOption === "total", // Incluir pay_total
        };

        console.log("Payload para /lessons/private-booking:", payload);

        const response = await api.post("/lessons/private-booking", payload);

        if (response.data && response.data.booking_id) {
            console.log("Reserva de clase privada creada:", response.data);
            return { success: true, path: `/player/privatelesson/${response.data.booking_id}` };
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



export const finalizePublicLessonBooking = async (paymentIntent, context, api, $q) => {
    console.log("Finalizando inscripción a clase pública...");
    console.log("context:", context);

    const { baseData, paymentOrderId } = context; // Extraer paymentOrderId del contexto

    try {
        // 1. Validar datos
        if (!paymentOrderId) {
            console.error("Falta el paymentOrderId para la inscripción a la clase pública.");
            if ($q) $q.notify({ type: 'negative', message: 'Error interno: Falta el ID de la orden de pago.' });
            return { success: false };
        }

        // 2. Llamar a /process-stripe-payment para actualizar los datos de pago
        const paymentData = {
            payment_order_id: paymentOrderId,
            payment_method: paymentIntent.payment_method,
            payment_status: paymentIntent.status,
            transaction_id: paymentIntent.id,
            is_full_payment: true, // Asumimos que las clases públicas son pago total
        };
        const paymentResponse = await api.post("/payments/process-stripe-payment", paymentData);

        if (!paymentResponse.data || !paymentResponse.data.message) {
            throw new Error("Error al actualizar el estado del pago.");
        }

        // Añadimos un pequeño retraso antes de llamar a /lessons/public-booking
        await new Promise(resolve => setTimeout(resolve, 500));

        // 3. Llamar al endpoint /lessons/public-booking/{lesson_id}
        const response = await api.post(`/lessons/public-booking/${baseData.id}`); // Usar context.lessonId

        // 4. Validar la respuesta
        if (response.data && response.data.message === "Inscripción exitosa.") {
            console.log("Inscripción a clase pública exitosa:", response.data);
            if ($q) $q.notify({ type: 'positive', message: 'Te has inscrito a la clase con éxito.' });
            return { success: true };
        } else {
            console.error("Error al inscribirse a la clase pública:", response);
            const errorMessage = response.data?.detail || response.data?.message || "No se pudo completar la inscripción.";
            if ($q) $q.notify({ type: 'negative', message: errorMessage });
            return { success: false };
        }

    } catch (error) {
        console.error("Error en finalizePublicLessonBooking:", error);
        const errorMessage = error.response?.data?.detail || error.message || "Error al inscribirse a la clase.";
        if ($q) $q.notify({ type: 'negative', message: errorMessage });
        return { success: false };
    }
};



export const finalizeMatchJoin = async (paymentIntent, context, api, $q) => {
    console.log("Finalizando unión a partido abierto...");
    console.log("context:", context);

    const { paymentOrderId, extraData } = context;
    const { matchId, slotIndex, teamToJoin } = extraData || {}; // Usar destructuring con valor por defecto

    try {
        // 1. Validar datos
        if (!paymentOrderId || !extraData || matchId === undefined || slotIndex === undefined || teamToJoin === undefined) {
            console.error("Faltan datos para la unión al partido abierto.");
            if ($q) $q.notify({ type: 'negative', message: 'Error interno: Faltan datos para unirse al partido.' });
            return { success: false };
        }

        // 2. Llamar a /payments/process-stripe-payment para actualizar los datos de pago
        const paymentData = {
            payment_order_id: paymentOrderId,
            payment_method: paymentIntent.payment_method,
            payment_status: paymentIntent.status,
            transaction_id: paymentIntent.id,
            is_full_payment: true, // Asumimos que la unión a partidos es pago total
        };
        const paymentResponse = await api.post("/payments/process-stripe-payment", paymentData);

        if (!paymentResponse.data || !paymentResponse.data.message) {
            throw new Error("Error al actualizar el estado del pago.");
        }

        // Añadimos un pequeño retraso antes de llamar a /matches/join
        await new Promise(resolve => setTimeout(resolve, 500));

        // 3. Llamar al endpoint /matches/join
        const joinData = {
            match_id: matchId,
            slot_index: slotIndex,
            team_to_join: teamToJoin,
        };
        const response = await api.post("/matches/join", joinData);

        // 4. Validar la respuesta
        if (response.data && response.data.message === "Te has unido al partido exitosamente.") {
            console.log("Unión a partido abierto exitosa:", response.data);
            if ($q) $q.notify({ type: 'positive', message: 'Te has unido al partido con éxito.' });
            return { success: true };
        } else {
            console.error("Error al unirse al partido abierto:", response);
            const errorMessage = response.data?.detail || response.data?.message || "No se pudo completar la unión al partido.";
            if ($q) $q.notify({ type: 'negative', message: errorMessage });
            return { success: false };
        }

    } catch (error) {
        console.error("Error en finalizeMatchJoin:", error);
        const errorMessage = error.response?.data?.detail || error.message || "Error al unirse al partido.";
        if ($q) $q.notify({ type: 'negative', message: errorMessage });
        return { success: false };
    }
};


export const finalizeTournamentEnrollment = async (paymentIntent, context, api, $q) => {
    console.log("Finalizando inscripción a torneo...");
    console.log("context:", context);

    const { paymentOrderId, baseData, extraData } = context;
    const { id: tournamentId } = baseData || {}; // Usar destructuring con valor por defecto
    const { partnerId } = extraData || {}; // Usar destructuring con valor por defecto

    try {
        // 1. Validar datos
        if (!paymentOrderId || !tournamentId || !partnerId) {
            console.error("Faltan datos para la inscripción al torneo.");
            if ($q) $q.notify({ type: 'negative', message: 'Error interno: Faltan datos para inscribirse al torneo.' });
            return { success: false };
        }

        // 2. Llamar a /payments/process-stripe-payment para actualizar los datos de pago
        const paymentData = {
            payment_order_id: paymentOrderId,
            payment_method: paymentIntent.payment_method,
            payment_status: paymentIntent.status,
            transaction_id: paymentIntent.id,
            is_full_payment: true, // Asumimos que la inscripción a torneos es pago total
        };
        const paymentResponse = await api.post("/payments/process-stripe-payment", paymentData);

        if (!paymentResponse.data || !paymentResponse.data.message) {
            throw new Error("Error al actualizar el estado del pago.");
        }

        // Añadimos un pequeño retraso antes de llamar a /tournaments/register-team
        await new Promise(resolve => setTimeout(resolve, 500));

        // 3. Llamar al endpoint /tournaments/register-team
        const registerData = {
            tournament_id: tournamentId,
            partner_id: partnerId, // Can be null for retas
        };
        const response = await api.post("/tournaments/register-team", registerData);

        // 4. Validar la respuesta
        const isRetas = extraData && extraData.isRetas;
        const expectedMessage = isRetas ? "Te registraste exitosamente en las retas." : "Equipo registrado exitosamente.";
        const successMessage = isRetas ? 'Te has inscrito a las retas con éxito.' : 'Te has inscrito al torneo con éxito.';
        
        if (response.data && (response.data.message === expectedMessage || response.data.message.includes("exitosamente"))) {
            console.log("Inscripción exitosa:", response.data);
            if ($q) $q.notify({ type: 'positive', message: successMessage });
            return { success: true };
        } else {
            console.error("Error al inscribirse:", response);
            const errorMessage = response.data?.detail || response.data?.message || "No se pudo completar la inscripción.";
            if ($q) $q.notify({ type: 'negative', message: errorMessage });
            return { success: false };
        }

    } catch (error) {
        console.error("Error en finalizeTournamentEnrollment:", error);
        const errorMessage = error.response?.data?.detail || error.message || "Error al inscribirse al torneo.";
        if ($q) $q.notify({ type: 'negative', message: errorMessage });
        return { success: false };
    }
};