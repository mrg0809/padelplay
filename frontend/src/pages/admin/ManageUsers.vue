<template>
    <q-layout view="hHh lpR fFf" class="bg-dark text-white">
      <q-header elevated class="bg-primary text-white">
        <q-toolbar>
          <q-toolbar-title>Administrar Usuarios</q-toolbar-title>
        </q-toolbar>
      </q-header>
  
      <q-page-container>
        <q-page class="q-pa-md">
          <!-- Filtro -->
          <div class="q-mb-md">
            <q-select
              v-model="selectedFilter"
              :options="filters"
              label="Filtrar por tipo de usuario"
              outlined
              dense
              color="primary"
              @change="filterUsers"
            />
          </div>
  
          <!-- Tabla de Usuarios -->
          <q-table
            flat
            :rows="filteredUsers"
            :columns="columns"
            row-key="id"
            dense
            class="text-white bg-dark"
            hide-bottom
          />
  
          <!-- Resumen -->
          <div class="q-mt-md text-white">
            <p>Total Clubes: {{ totalClubs }}</p>
            <p>Total Asociaciones: {{ totalAssociations }}</p>
          </div>
          <!-- Botones para agregar usuarios -->
          <div class="q-mb-md text-right">
            <q-btn
              label="Agregar Club"
              color="primary"
              icon="add"
              class="q-mr-md"
              @click="addUser('club')"
            />
            <q-btn
              label="Agregar Asociación"
              color="primary"
              icon="add"
              @click="addUser('association')"
            />
          </div>
        </q-page>
      </q-page-container>
    </q-layout>
  </template>
  
  <script>
  import { supabase } from "src/services/supabase";

export default {
  name: "ManageUsers",
  data() {
    return {
      users: [], // Lista completa de usuarios
      filteredUsers: [], // Usuarios filtrados dinámicamente
      selectedFilter: "all", // Filtro seleccionado
      filters: [
        { label: "Todos", value: "all" },
        { label: "Clubes", value: "club" },
        { label: "Asociaciones", value: "association" },
      ],
      columns: [
        { name: "email", label: "Correo", align: "left", field: "email" },
        { name: "name", label: "Nombre", align: "left", field: "name" },
      ],
    };
  },
  computed: {
    totalClubs() {
      return this.users.filter((user) => user.user_type === "club").length;
    },
    totalAssociations() {
      return this.users.filter((user) => user.user_type === "association").length;
    },
  },
  methods: {
    async fetchUsers() {
    try {
      const { data, error } = await supabase.rpc("get_users_with_profiles");

      if (error) {
        console.error("Error al obtener usuarios:", error.message);
        return;
      }

      this.users = data.map((user) => ({
        id: user.id,
        email: user.email,
        name: user.full_name,
        user_type: user.user_type, // Verifica que esto esté presente
      }));

      console.log("Usuarios cargados:", this.users);

      // Inicializar usuarios filtrados
      this.filterUsers();
    } catch (error) {
      console.error("Error inesperado:", error.message);
    }
  },
  filterUsers() {
    console.log("Filtro seleccionado:", this.selectedFilter);
    console.log("Usuarios antes de filtrar:", this.users);

    if (this.selectedFilter.value === "all") {
        this.filteredUsers = [...this.users];
    } else {
        this.filteredUsers = this.users.filter((user) => {
        console.log("Comparando:", user.user_type, "con", this.selectedFilter.value);
        return user.user_type === this.selectedFilter.value;
        });
    }

    console.log("Usuarios filtrados:", this.filteredUsers);
    },
    addUser(userType) {
      this.$router.push(`/admin/add-user?type=${userType}`);
    },
  },
  watch: {
    selectedFilter: "filterUsers", // Reactividad para actualizar al cambiar el filtro
  },
  mounted() {
    this.fetchUsers();
  },
};
  </script>
  
  <style scoped>
  .q-layout {
    min-height: 100vh;
  }
  
  /* Tabla */
  .q-table {
  width: 100%;
}

.q-table .q-virtual-scroll__padding {
  display: none; /* Eliminar el espacio del input de paginación */
}

.text-white {
  color: white !important;
}

.bg-dark {
  background-color: #121212 !important;
}
  </style>
  