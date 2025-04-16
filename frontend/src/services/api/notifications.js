import api from "../api";

export const createNotification = async (notificationData) => {
    try {
        const response = await api.post('/notifications', notificationData);
        return response.data; 
    } catch (error) {
        console.error("Error al crear la notificación:", error);
        throw error; 
    }
  };