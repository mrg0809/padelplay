<template>
    <q-page class="q-pa-md">
      <q-card class="q-pa-md">
        <q-form @submit="registerUser">
          <q-input v-model="email" label="Correo" type="email" required />
          <q-input v-model="password" label="Contraseña" type="password" required />
          <q-select
            v-model="userType"
            label="Tipo de usuario"
            :options="userTypes"
            required
          />
          <q-btn label="Registrar" type="submit" color="primary" />
        </q-form>
      </q-card>
    </q-page>
  </template>
  
  <script setup>
  import { ref } from 'vue';
  import { supabase } from '../services/supabase';
  
  const email = ref('');
  const password = ref('');
  const userType = ref('');
  const userTypes = ['administrador', 'club', 'jugador'];
  
  const registerUser = async () => {
    const { data, error } = await supabase.auth.signUp({
      email: email.value,
      password: password.value,
    });
  
    if (error) {
      console.error(error.message);
      return;
    }
  
    // Crear perfil adicional
    await supabase.from('profiles').insert({
      id: data.user.id,
      full_name: email.value.split('@')[0],
      user_type: userType.value,
    });
  
    alert('Usuario registrado correctamente');
  };
  </script>
  