import { supabase } from "../supabase";

export const getProductsByClub = async (clubId) => {
  const { data, error } = await supabase
    .from("club_products")
    .select("id, name, brand, category, price, modality")
    .eq("club_id", clubId);

  if (error) throw Error(error.message);
  return data || [];
}