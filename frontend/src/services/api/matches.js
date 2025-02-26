import api from "../api";

export const fetchUpcomingPlayerMatches = async () => {
    try {
      const response = await api.get("/matches/upcoming");
      return response.data.matches;
    } catch (error) {
      console.error("Error al cargar partidos:", error);
      throw error;
    }
};