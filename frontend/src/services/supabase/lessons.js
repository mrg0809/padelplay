import { supabase } from "../supabase";

export const getLessonDetails = async (lessonId) => {
    const { data, error } = await supabase
      .from("lessons")
      .select("id, name, description, court_id, duration, coach, lesson_date, lesson_time, price, coaches(name)")
      .eq("id", lessonId);
  
    if (error) throw new Error(error.message);
    return data;
  };
