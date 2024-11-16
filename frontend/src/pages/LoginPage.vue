<template>
    <q-page class="q-pa-md">
      <q-card class="q-pa-md">
        <q-form @submit="loginUser">
          <q-input v-model="email" label="Correo" type="email" required />
          <q-input v-model="password" label="Contraseña" type="password" required />
          <q-btn label="Iniciar sesión" type="submit" color="primary" />
        </q-form>
      </q-card>
    </q-page>
  </template>
  
  <script setup>
  import { ref } from 'vue';
  import { supabase } from '../services/supabase';
  
  const email = ref('');
  const password = ref('');
  
  const loginUser = async () => {
    const { error } = await supabase.auth.signInWithPassword({
      email: email.value,
      password: password.value,
    });
  
    if (error) {
      console.error(error.message);
      alert('Error al iniciar sesión');
      return;
    }
  
    alert('Inicio de sesión exitoso');
  };
  </script>
  