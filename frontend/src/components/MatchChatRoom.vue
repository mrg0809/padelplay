<template>
    <q-layout view="hHh lpR fFf" class="bg-dark text-white">
      <q-page-container>
        <q-page class="q-pa-md">
          <q-card class="bg-dark text-white">
            <!-- Mensajes -->
            <div class="chat-messages">
              <div
                v-for="message in messages"
                :key="message.id"
                :class="['message', message.sender_id === currentUserId ? 'self' : 'other']"
              >
                <p><strong>{{ user.full_name }}</strong></p>
                <p>{{ message.message }}</p>
                <small>{{ formatTimestamp(message.timestamp) }}</small>
              </div>
            </div>
           
          </q-card>
          <!-- Campo para enviar mensaje -->
        <div>
          <q-input
                v-model="newMessage"
                placeholder="Escribe un mensaje..."
                outlined
                dense
                class="q-my-sm"
                @keyup.enter="sendMessage"
              />
              <q-btn
                label="Enviar"
                color="primary"
                @click="sendMessage"
                :disable="!newMessage.trim()"
              />
        </div>
        </q-page>
      </q-page-container>
    </q-layout>
  </template>
  
  <script>
  import { ref, onMounted, onUnmounted } from "vue";
  import { supabase } from "../services/supabase";
  
  export default {
    props: {
      matchId: {
        type: String,
        required: true,
      },
    },
    setup(props) {
      const messages = ref([]);
      const newMessage = ref("");
      const currentUserId = ref(null); // ID del usuario actual
      const user = ref({full_name: "Usuario desconocido"})
      let subscription = null;
  
      const fetchMessages = async () => {
        try {
          const { data, error } = await supabase
            .from("chat_messages")
            .select("*")
            .eq("match_id", props.matchId)
            .order("timestamp", { ascending: true });
  
          if (error) {
            console.error("Error al cargar mensajes:", error);
          } else {
            messages.value = data;
          }
        } catch (err) {
          console.error("Error inesperado al cargar mensajes:", err);
        }
      };
  
      const fetchChatUsers = async () => {
        try {
          const { data, error } = await supabase
            .from("chat_users")
            .select("user_id")
            .eq("match_id", props.matchId);
  
          if (error) {
            console.error("Error al cargar usuarios del chat:", error);
          } else {
            const userIds = data.map((u) => u.user_id);
            await fetchUserDetails(userIds);
          }
        } catch (err) {
          console.error("Error inesperado al cargar usuarios del chat:", err);
        }
      };
  
      const fetchUserDetails = async (userIds) => {
        try {
          const { data, error } = await supabase
            .from("players")
            .select("id, email")
            .in("id", userIds);
  
          if (error) {
            console.error("Error al obtener detalles de usuarios:", error);
          } else {
            data.forEach((user) => {
              userMap.value[user.id] = user.email;
            });
          }
        } catch (err) {
          console.error("Error inesperado al obtener detalles de usuarios:", err);
        }
      };
  
      const sendMessage = async () => {
        try {
          const { error } = await supabase.from("chat_messages").insert({
            match_id: props.matchId,
            sender: user.value.full_name,
            sender_id: currentUserId.value,
            message: newMessage.value.trim(),
          });
  
          if (error) {
            console.error("Error al enviar mensaje:", error);
          } else {
            newMessage.value = "";
          }
        } catch (err) {
          console.error("Error inesperado al enviar mensaje:", err);
        }
      };
  
      const setupRealtime = () => {
        subscription = supabase
          .channel("public:chat_messages")
          .on(
            "postgres_changes",
            {
              event: "INSERT",
              schema: "public",
              table: "chat_messages",
              filter: `match_id=eq.${props.matchId}`,
            },
            (payload) => {
              messages.value.push(payload.new);
            }
          )
          .subscribe((status) => {
            if (status === "SUBSCRIBED") {
              console.log("Realtime subscription active");
            }
          });
      };
  
      const formatTimestamp = (timestamp) => {
        return new Date(timestamp).toLocaleTimeString("es-MX", {
          hour: "2-digit",
          minute: "2-digit",
        });
      };
  
      onMounted(async () => {
        const token = localStorage.getItem("token");
        if (token) {
          const base64Url = token.split(".")[1];
          const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
          const payload = JSON.parse(atob(base64));
          currentUserId.value = payload.sub;
          user.value.full_name = payload.full_name || "Usuario desconocido"
        }
        await fetchMessages();
        await fetchChatUsers();
        setupRealtime();
      });
  
      onUnmounted(() => {
        if (subscription) {
          supabase.removeChannel(subscription);
        }
      });
  
      return {
        currentUserId,
        messages,
        newMessage,
        formatTimestamp,
        sendMessage,
        user,
      };
    },
  };
  </script>
  
  <style scoped>
  .chat-messages {
    max-height: 400px;
    overflow-y: auto;
    margin-bottom: 16px;
    padding: 8px;
    background-color: #1e1e1e;
    border-radius: 8px;
  }
  
  .message {
    margin-bottom: 8px;
    padding: 8px;
    border-radius: 4px;
  }
  
  .message.self {
    background-color: #007bff;
    color: white;
    align-self: flex-end;
  }
  
  .message.other {
    background-color: #444;
    color: white;
    align-self: flex-start;
  }
  </style>
  