<template>
  <div class="register-page">
    <h1>Register</h1>
    <form @submit.prevent="register">
      <div>
        <label for="full_name">Full Name:</label>
        <input type="text" v-model="fullName" required />
      </div>
      <div>
        <label for="email">Email:</label>
        <input type="email" v-model="email" required />
      </div>
      <div>
        <label for="password">Password:</label>
        <input type="password" v-model="password" required />
      </div>
      <button type="submit">Register</button>
      <p v-if="error" class="error">{{ error }}</p>
      <p v-if="success" class="success">Registration successful! Please login.</p>
    </form>
  </div>
</template>

<script>
import api from "../api";

export default {
  name: "RegisterPage",
  data() {
    return {
      fullName: "",
      email: "",
      password: "",
      error: null,
      success: false,
    };
  },
  methods: {
    async register() {
      this.error = null;
      this.success = false;
      try {
        await api.post("/auth/register", {
          full_name: this.fullName,
          email: this.email,
          password: this.password,
        });
        this.success = true;
      } catch (err) {
        this.error = "Error registering. Please try again.";
      }
    },
  },
};
</script>

<style scoped>
.error {
  color: red;
}
.success {
  color: green;
}
</style>
