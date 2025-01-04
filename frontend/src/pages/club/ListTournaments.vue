<template>
  <q-layout view="hHh lpR fFf" class="bg-dark text-white">
    <q-header elevated class="bg-primary text-white">
      <q-toolbar>
        <q-toolbar-title>Mis Torneos</q-toolbar-title>
        <q-btn flat round icon="arrow_back" @click="goBack" label="REGRESAR" />
      </q-toolbar>
    </q-header>

    <q-page-container>
      <q-page class="q-pa-md">
        <!-- Listado de Torneos -->
        <div v-if="tournaments.length === 0" class="text-center q-mt-md">
          <q-icon name="event_busy" size="64px" />
          <p>No has creado torneos todavía.</p>
        </div>
        <div v-else class="tournaments-list">
          <q-card
            v-for="tournament in tournaments"
            :key="tournament.id"
            class="q-mb-md"
            bordered
          >
            <q-card-section>
              <h4>{{ tournament.name }}</h4>
              <p>
                <strong>Fecha:</strong> {{ tournament.start_date }} <br />
                <strong>Mínimo de Parejas:</strong> {{ tournament.min_pairs }} <br />
                <strong>Parejas Inscritas:</strong> {{ tournament.registered_teams }}
              </p>
              <div class="actions">
                <q-btn
                  icon="edit"
                  label="Editar"
                  color="primary"
                  @click="editTournament(tournament.id)"
                />
                <q-btn
                  icon="delete"
                  label="Eliminar"
                  color="negative"
                  :disable="tournament.registered_teams > 0"
                  @click="openDeleteDialog(tournament.id)"
                />
                <q-btn
                  icon="block"
                  label="Cerrar Torneo"
                  color="orange"
                  @click="openCloseDialog(tournament.id)"
                />
              </div>
            </q-card-section>
          </q-card>
        </div>
      </q-page>

      <!-- Diálogo de Confirmación para Eliminar -->
      <q-dialog v-model="deleteDialogVisible">
        <q-card>
          <q-card-section>
            <div class="text-h6">Confirmar eliminación</div>
            <div>¿Estás seguro de que deseas eliminar este torneo?</div>
          </q-card-section>
          <q-card-actions align="right">
            <q-btn flat label="Cancelar" color="primary" v-close-popup />
            <q-btn flat label="Eliminar" color="negative" @click="deleteTournament" />
          </q-card-actions>
        </q-card>
      </q-dialog>

      <!-- Diálogo de Confirmación para Cerrar -->
      <q-dialog v-model="closeDialogVisible">
        <q-card>
          <q-card-section>
            <div class="text-h6">Confirmar cierre</div>
            <div>
              ¿Estás seguro de que deseas cerrar este torneo? Esto generará el fixture automáticamente.
            </div>
          </q-card-section>
          <q-card-actions align="right">
            <q-btn flat label="Cancelar" color="primary" v-close-popup />
            <q-btn flat label="Cerrar Torneo" color="orange" @click="closeTournament" />
          </q-card-actions>
        </q-card>
      </q-dialog>
    </q-page-container>
    <!-- Menú de Navegación Inferior -->
    <q-footer class="bg-primary text-white">
      <q-tabs
        align="justify"
        class="q-pa-xs"
        active-color="white"
        @update:model-value="onTabChange"
      >
        <q-tab
          v-for="tab in tabs"
          :key="tab.name"
          :name="tab.name"
          :label="tab.label"
          :icon="tab.icon"
          class="text-white"
        />
      </q-tabs>
    </q-footer>
  </q-layout>
</template>

<script>
import { ref, onMounted } from "vue";
import { supabase } from "src/services/supabase";
import { useRouter } from "vue-router";

export default {
  name: "ListTournaments",
  setup() {
    const router = useRouter();
    const tournaments = ref([]);
    const clubId = ref(null);

    // Estado para los diálogos de confirmación
    const deleteDialogVisible = ref(false);
    const closeDialogVisible = ref(false);
    const selectedTournamentId = ref(null);

    const fetchTournaments = async () => {
      try {
        if (!clubId.value) {
          console.error("Club ID no encontrado.");
          return;
        }

        const { data, error } = await supabase.rpc("get_tournaments_by_club", {
          club_id: clubId.value,
        });

        if (error) {
          console.error("Error fetching tournaments:", error.message);
          return;
        }

        tournaments.value = data.map((tournament) => ({
          id: tournament.id,
          name: tournament.name,
          start_date: tournament.start_date,
          min_pairs: tournament.min_pairs,
          registered_teams: tournament.registered_teams || 0,
        }));
      } catch (error) {
        console.error("Unexpected error fetching tournaments:", error.message);
      }
    };

    const editTournament = (id) => {
      router.push({ name: "EditTournament", params: { tournamentId: id } });
    };

    const openDeleteDialog = (id) => {
      selectedTournamentId.value = id;
      deleteDialogVisible.value = true;
    };

    const deleteTournament = async () => {
      try {
        const { error } = await supabase.from("tournaments").delete().eq("id", selectedTournamentId.value);
        if (error) throw error;

        tournaments.value = tournaments.value.filter(
          (tournament) => tournament.id !== selectedTournamentId.value
        );
        deleteDialogVisible.value = false;
        alert("Torneo eliminado exitosamente.");
      } catch (error) {
        console.error("Error al eliminar el torneo:", error.message);
        alert("Error al eliminar el torneo.");
      }
    };

    const openCloseDialog = (id) => {
      selectedTournamentId.value = id;
      closeDialogVisible.value = true;
    };

    const closeTournament = async () => {
      try {
        const { error } = await supabase
          .from("tournaments")
          .update({ status: "closed" })
          .eq("id", selectedTournamentId.value);
        if (error) throw error;

        closeDialogVisible.value = false;
        alert("Torneo cerrado exitosamente.");
        fetchTournaments();
      } catch (error) {
        console.error("Error al cerrar el torneo:", error.message);
        alert("Error al cerrar el torneo.");
      }
    };

    const onTabChange = (tabName) => {
      router.push(`/club/${tabName}`);
    };

    const goBack = () => {
      router.back();
    };

    onMounted(() => {
      const token = localStorage.getItem("token");
      if (token) {
        const base64Url = token.split(".")[1];
        const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
        const payload = JSON.parse(atob(base64));
        clubId.value = payload.club_id || null;
      }

      fetchTournaments();
    });

    return {
      tournaments,
      goBack,
      onTabChange,
      editTournament,
      openDeleteDialog,
      openCloseDialog,
      deleteDialogVisible,
      closeDialogVisible,
      deleteTournament,
      closeTournament,
      tabs: [
        { name: "inicio", label: "Inicio", icon: "home" },
        { name: "torneos", label: "Torneos", icon: "sports_tennis" },
        { name: "perfil", label: "Perfil", icon: "account_circle" },
      ],
    };
  },
};
</script>

<style scoped>
.tournaments-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.q-card {
  background-color: #1e1e1e;
  color: white;
}

.q-card:hover {
  background-color: #292929;
}

.actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}
</style>
