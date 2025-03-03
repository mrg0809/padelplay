import api from "../api";

export const fetchClubLessons = async (clubId) => {
    try {
      const response = await api.get("/lessons", {
        params: { club_id: clubId },
      });
      return response.data;
    } catch (error) {
      console.error("Error al cargar clases:", error);
      throw error;
    }
};