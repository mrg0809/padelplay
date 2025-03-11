import { supabase } from "../supabase";

export const fetchCourtBlocks = async (date, clubId) => {
    try {
        const { data, error } = await supabase
            .from('court_blocks')
            .select('*')
            .eq('club_id', clubId)
            .lte('start_date', date)
            .gte('end_date', date);

        if (error) throw error;
        return data;
    } catch (error) {
        console.error('Error fetching court blocks:', error);
        throw error;
    }
};