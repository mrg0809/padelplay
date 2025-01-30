<template>
  <q-btn-dropdown
    flat
    round
    dense
    no-arrow
    icon="o_menu"
    size="lg"
    menu-self="top right"
    class="my-dropdown"
  >
    <q-list class="q-list-menu">
      <q-item clickable v-ripple @click="goToPage('/terms')">
        <q-item-section avatar>
          <q-icon name="description" />
        </q-item-section>
        <q-item-section>
          Términos y Condiciones
        </q-item-section>
      </q-item>

      <q-item clickable v-ripple @click="goToPage('/privacy')">
        <q-item-section avatar>
          <q-icon name="shield" />
        </q-item-section>
        <q-item-section>
          Aviso de Privacidad
        </q-item-section>
      </q-item>

      <q-item clickable v-ripple @click="goToPage('/faq')">
        <q-item-section avatar>
          <q-icon name="help_outline" />
        </q-item-section>
        <q-item-section>
          FAQ
        </q-item-section>
      </q-item>

      <q-separator />

      <q-item clickable v-ripple @click="logout">
        <q-item-section avatar>
          <q-icon name="logout" />
        </q-item-section>
        <q-item-section>
          Cerrar Sesión
        </q-item-section>
      </q-item>
    </q-list>
  </q-btn-dropdown>
</template>

<script>
export default {
  name: "PlayerTopMenu",
  methods: {
    goToPage(route) {
      this.$router.push(route);
    },
    logout() {
      // Cerrar sesion
      console.log("Cerrando sesión...");
      this.$router.push("/login");
    },
  },
};
</script>

<style scoped>
.my-dropdown >>> .q-btn-dropdown__arrow {
  display: none;
}

.q-list-menu {
  min-width: 150px;
  background-image: url("../assets/texturafondo.png");
  background-size: cover;

}

</style>