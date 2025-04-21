import { supabase } from "../supabase";

export const getTournamentsByClub = async (clubId) => {
  if (!clubId) {
    console.error("getTournamentsByClub llamado sin clubId.");
    return []; 
  }

  const today = new Date();
  const todayDateString = today.toISOString().split('T')[0];
  console.log(`Buscando torneos futuros para club ${clubId} desde fecha: ${todayDateString}`);

  try {
    const { data, error } = await supabase
      .from("tournaments")
      .select("id, name, start_date, category, gender") 
      .eq("club_id", clubId) 
      .gte('start_date', todayDateString)         
      .order('start_date', { ascending: true }); 

    // 4. Manejar errores
    if (error) {
        console.error(`Error fetching future tournaments for club ${clubId}:`, error);
        return []; 
    }

    console.log(`Encontrados ${data?.length || 0} torneos futuros para club ${clubId}.`);
    // 5. Devolver los datos (o array vacío si no hay resultados)
    return data || [];

  } catch (err) {
      console.error(`Excepción en getTournamentsByClub para club ${clubId}:`, err);
      return []; // Devolver array vacío en caso de excepción
  }
};


export const fetchTournaments = async (filters) => {
  console.log("Buscando torneos con filtros:", filters); 
  try {

      const today = new Date();
      const todayDateString = today.toISOString().split('T')[0]; 

      let query = supabase
          .from('tournaments')
          .select(`
              id,
              name,
              start_date,
              category,
              gender,
              price_per_pair,
              prize,
              club_id,
              clubs ( city, name )
          `)
          .gte('start_date', todayDateString);

      if (filters?.city && filters.city !== '') { 
          console.log(`Aplicando filtro ciudad: ${filters.city}`);
          query = query.eq('clubs.city', filters.city);
      }
      if (filters?.category && filters.category !== '') {
           console.log(`Aplicando filtro categoría: ${filters.category}`);
          query = query.eq('category', filters.category);
      }
      if (filters?.gender && filters.gender !== '') {
           console.log(`Aplicando filtro género: ${filters.gender}`);
          query = query.eq('gender', filters.gender);
      }

      query = query.order('start_date', { ascending: true });

      const { data, error } = await query;

      if (error) {
          console.error("Error de Supabase al buscar torneos:", error);
           if (error.message.includes("relation") || error.message.includes("schema")) {
               console.warn("Posible problema con el filtro de relación (ciudad).");
           }
          return []; 
      }

      console.log(`Se encontraron ${data?.length || 0} torneos.`);
      return data || [];

  } catch (err) {
      console.error('Excepción en fetchTournaments:', err);
      return [];
  }
};

export const fetchTournamentDetails = async (tournamentId) => {
  const { data, error } = await supabase
    .from("tournaments")
    .select("id, name, start_date, end_date, start_time, end_time, category, gender, price_per_pair, prize, clubs(name, city)")
    .eq("id", tournamentId);

  if (error) throw Error(error.message);
  return data || [];
}

