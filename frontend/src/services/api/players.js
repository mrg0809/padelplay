import api from "../api";

export const fetchUpcomingPlayerEvents = async (playerId) => {
    try {
      const response = await api.get(`/events/player/upcoming_events/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching upcoming player events from API:', error);
      return [];
    }
  };