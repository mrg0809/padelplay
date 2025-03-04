javascript
Copy
import api from "../services/api"; // Importa tu servicio de API

/**
 * Crea un pago a través de tu backend.
 * @param {Object} paymentData - Datos del pago.
 * @returns {Promise<Object>} - Respuesta del backend (token y URL de pago).
 */
export const createEspiralPayment = async (paymentData) => {
  try {
    const response = await api.post("/payments/create-payment", paymentData); // Llama a tu endpoint de FastAPI
    return response.data; // Devuelve la respuesta del backend
  } catch (error) {
    console.error("Error en createEspiralPayment:", error);
    throw error;
  }
};