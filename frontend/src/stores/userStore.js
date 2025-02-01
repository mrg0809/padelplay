import { defineStore } from 'pinia';

export const useUserStore = defineStore('user', {
  state: () => ({
    userId: null,
    email: null,
    userType: null,
    clubId: null,
    fullName: null,
  }),
  actions: {
    setUserDataFromToken(token) {
      try {
        const base64Url = token.split(".")[1]; // Extraer el payload
        const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
        const payload = JSON.parse(atob(base64));

        this.userId = payload.sub; // user_id
        this.email = payload.email;
        this.userType = payload.user_type;
        this.clubId = payload.club_id;
        this.fullName = payload.full_name;
      } catch (error) {
        console.error("Error decoding token:", error);
      }
    },
    clearUserData() {
      this.userId = null;
      this.email = null;
      this.userType = null;
      this.clubId = null;
      this.fullName = null;
    },
  },
  persist: true, // Habilita la persistencia del store
});