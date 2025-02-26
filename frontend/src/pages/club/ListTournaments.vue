<template>
  <q-layout view="hHh lpR fFf" class="body text-white">
    <q-header elevated class="bg-primary text-white">
      <div class="header-content">
        <div class="greeting">
          <img src="/src/assets/padelplay.png" alt="Logo" class="logo-icon" />
          Mis Torneos
        </div>
        <div class="header-icons">
          <q-btn flat round icon="arrow_back" @click="goBack" />
        </div>
      </div>
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
            class="q-mb-md transparent-card"
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
                  size="sm"
                  @click="editTournament(tournament.id)"
                />
                <q-btn
                  icon="delete"
                  label="Eliminar"
                  color="negative"
                  size="sm"
                  :disable="tournament.registered_teams > 0"
                  @click="openDeleteDialog(tournament.id)"
                />
                <q-btn
                  icon="block"
                  label="Cerrar Torneo"
                  color="orange"
                  size="sm"
                  @click="openCloseDialog(tournament)"
                />
              </div>
            </q-card-section>
          </q-card>
        </div>
      </q-page>

      <!-- Botón flotante para agregar torneo -->
      <q-btn
        glossy
        round
        size="lg"
        color="black"
        icon="add"
        class="fixed-bottom-right q-mb-xl"
      >
        <q-menu anchor="top end" self="bottom end">
          <q-list style="min-width: 150px">
            <q-item clickable v-close-popup @click="openCreateTournament">
              <q-item-section><strong>Retas</strong></q-item-section>
            </q-item>
            <q-item clickable v-close-popup @click="openCreateTournament">
              <q-item-section><strong>Torneo</strong></q-item-section>
            </q-item>
          </q-list>
        </q-menu>
      </q-btn>

      <!-- Diálogo de Confirmación para Eliminar -->
      <q-dialog v-model="deleteDialogVisible">
        <q-card class="bg-black text-white">
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
        <q-card class="bg-black text-white">
          <q-card-section>
            <div class="text-h6">Confirmar cierre</div>
            <div>
              ¿Estás seguro de que deseas cerrar este torneo? Esto generará el fixture automáticamente.
            </div>
          </q-card-section>
          <q-card-actions align="right">
            <q-btn flat label="Cancelar" color="red" v-close-popup />
            <q-btn flat label="Cerrar Torneo" color="green" @click="closeTournament" />
          </q-card-actions>
        </q-card>
      </q-dialog>
    </q-page-container>
    <ClubNavigationMenu />
  </q-layout>
</template>

<script>
import { ref, onMounted } from "vue";
import { supabase } from "src/services/supabase";
import { useRouter } from "vue-router";
import { useQuasar } from 'quasar';
import api from "../../services/api";
import ClubNavigationMenu from "src/components/ClubNavigationMenu.vue";

export default {
  name: "ListTournaments",
  components: {
    ClubNavigationMenu,
  },
  setup() {
    const router = useRouter();
    const $q = useQuasar();
    const tournaments = ref([]);
    const clubId = ref(null);

    // Estado para los diálogos de confirmación
    const deleteDialogVisible = ref(false);
    const closeDialogVisible = ref(false);
    const selectedTournamentId = ref(null);
    const selectedTournament = ref(null);

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
        $q.notify({
            type: "positive",
            message: "Torneo eliminado exitosamente.",
          });
      } catch (error) {
        console.error("Error al eliminar el torneo:", error.message);
        $q.notify({
            type: "negative",
            message: "Error al eliminar torneo.",
          });
      }
    };

    const openCloseDialog = (tournament) => {
      selectedTournament.value = tournament;
      closeDialogVisible.value = true;
    };

    const closeTournament = async () => {
      try {
          console.log('torneo:', selectedTournament.value.id)
          // Generar el preview del rol de juegos
          const response = await api.get(`/tournaments/${selectedTournament.value.id}/preview`);
          const matches = response.data.matches;

          // Navegar a la página de preview
          console.log("Passing tournament:", selectedTournament.value);
          console.log("Passing matches:", matches);

          setTimeout(() => {
          router.push({
            route: "/preview-tournament",
            name: "PreviewTournament",
            state: { tournament: selectedTournament.value, matches: matches },
          });
        }, 1000);
        } catch (error) {
          console.error("Error generating preview:", error);
          $q.notify({
          type: 'negative',
          message: 'Error al generar la vista previa.'
        });
        }
      };

    const openCreateTournament = (type) => {
      router.push("/club/creartorneos");
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
      editTournament,
      openDeleteDialog,
      openCloseDialog,
      deleteDialogVisible,
      closeDialogVisible,
      deleteTournament,
      closeTournament,
      openCreateTournament,
    };
  },
};
</script>

<style scoped>
.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  background-color: #000000;
}

.greeting {
  font-size: 1rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-icons {
  display: flex;
  gap: 2px;
}

.logo-icon {
  width: 60px;
  height: 60px;
}

.body {
  background-image: url(../../assets/menu/padelcourtfloor.jpg);
  background-size: cover;
}

.fixed-bottom-right {
  position: fixed;
  bottom: 80px;
  right: 20px;
  z-index: 1000;
}

.transparent-card {
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 8px;
}

.tournaments-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.q-btn {
  font-size: 12px;
  padding: 4px 8px;
}
</style>