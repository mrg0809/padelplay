import { supabase } from "src/services/supabase";


export const fetchTournamentPlayers = async (tournamentId) => {
    const { data: teamsData, error: teamsError } = await supabase
      .from("tournament_teams")
      .select("player1_id, player2_id")
      .eq("tournament_id", tournamentId);
  
    if (teamsError) throw new Error(teamsError.message);
  
    if (!teamsData || teamsData.length === 0) {
      return []; // No hay equipos inscritos, devolvemos un array vacío
    }
  
    // Obtener todos los player_ids únicos
    const playerIds = Array.from(new Set(teamsData.flatMap(team => [team.player1_id, team.player2_id])));
  
    const { data: playersData, error: playersError } = await supabase
      .from("players")
      .select("id, user_id, photo_url")
      .in("user_id", playerIds);
  
    if (playersError) throw new Error(playersError.message);
  
    // Mapear los datos de los jugadores para facilitar su uso
    const playersMap = new Map(playersData.map(player => [player.user_id, player]));
  
    // Combinar los datos de los equipos con los datos de los jugadores
    const tournamentPlayers = teamsData.map(team => ({
      player1: playersMap.get(team.player1_id),
      player2: playersMap.get(team.player2_id),
    }));
  
    return tournamentPlayers;
  };