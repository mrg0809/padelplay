<template>
  <div class="login-page">
    <h1>Login</h1>
    <form @submit.prevent="login">
      <div>
        <label for="email">Email:</label>
        <input type="email" v-model="email" required />
      </div>
      <div>
        <label for="password">Password:</label>
        <input type="password" v-model="password" required />
      </div>
      <button type="submit">Login</button>
      <p v-if="error" class="error">{{ error }}</p>
    </form>
  </div>
</template>

<script>
import api from "../api";

export default {
  name: "LoginPage",
  data() {
    return {
      email: "",
      password: "",
      error: null,
    };
  },
  methods: {
    async login() {
      this.error = null;
      try {
        const response = await api.post("/auth/login", {
          email: this.email,
          password: this.password,
        });
        const { access_token } = response.data;
        localStorage.setItem("token", access_token); // Guardar el token en localStorage
        this.$router.push("/dashboard"); // Redirigir al dashboard
      } catch (err) {
        this.error = "Invalid credentials. Please try again.";
      }
    },
  },
};
</script>

<style scoped>
.error {
  color: red;
}
</style>

  