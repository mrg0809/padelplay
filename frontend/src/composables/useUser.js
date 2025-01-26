import { ref, onMounted, onUnmounted } from 'vue';
import { supabase } from '../services/supabase'; 

const user = ref(null);
const isLoading = ref(true);
let authListener = null;

export function useUser() {
  onMounted(async () => { // Marca onMounted como async
    try {
      const { data: { user: sessionUser }, error } = await supabase.auth.getUser(); // Usa await
      if (error) {
        console.error("Error getting user:", error);
      }
      if (sessionUser) {
        user.value = sessionUser;
      }
    } catch (error) {
      console.error("Unexpected error getting user:", error);
    } finally {
      isLoading.value = false;
    }

    authListener = supabase.auth.onAuthStateChange((event, session) => {
      console.log("AUTH EVENT", event);
      console.log("AUTH SESSION", session);
      if (event === 'SIGNED_IN' || event === 'USER_UPDATED') {
        user.value = session.user;
      } else if (event === 'SIGNED_OUT') {
        user.value = null;
      }
    });
  });

  onUnmounted(() => {
    if (authListener) {
      authListener.unsubscribe();
    }
  });

  return { user, isLoading };
}