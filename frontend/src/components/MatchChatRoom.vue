<template>
  <q-layout view="hHh lpR fFf" class="bg-dark text-white">
    <q-page-container>
      <q-page class="q-pa-md">
        <q-card class="bg-dark text-white">
          <div class="chat-messages">
            <q-chat-message
              v-for="message in messages"
              :key="message.id"
              :name="userMap[message.sender_id]?.first_name || 'Usuario desconocido'"
              :avatar="userMap[message.sender_id]?.photo_url"
              :text="[message.message]"
              :stamp="formatTimestamp(message.timestamp)"
              :sent="message.sender_id === currentUserId"
              :bg-color="message.sender_id === currentUserId ? 'amber-7' : 'primary'"
              :text-color="message.sender_id === currentUserId ? 'black' : 'white'"
            />
          </div>
        </q-card>
        <div class="chat-message-input">
          <q-input
            v-model="newMessage"
            placeholder="Escribe un mensaje..."
            outlined
            dense
            @keyup.enter="sendMessage"
          />
          <q-btn
            color="black"
            @click="sendMessage"
            :disable="!newMessage.trim()"
            icon="o_send"
          />
        </div>
      </q-page>
    </q-page-container>
  </q-layout>
</template>
  
  <script>
  import { ref, onMounted, onUnmounted } from "vue";
  import { supabase } from "../services/supabase";
  import { QChatMessage } from "quasar";
  
  export default {
    props: {
      matchId: {
        type: String,
        required: true,
      },
    },
    components: {
      QChatMessage
    },
    setup(props) {
      const messages = ref([]);
      const newMessage = ref("");
      const currentUserId = ref(null); // ID del usuario actual
      const user = ref({full_name: "Usuario desconocido"})
      const userMap = ref({})
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
  
  
      const fetchUserDetails = async (userIds) => {
        try {
          const { data, error } = await supabase
            .from("players")
            .select("user_id, first_name, photo_url")
            .in("user_id", userIds);
  
          if (error) {
            console.error("Error al obtener detalles de usuarios:", error);
          } else {
            data.forEach((user) => {
              userMap.value[user.user_id] = user;
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
        const userIds = messages.value.map(message => message.sender_id); // Obtener los IDs de los remitentes
        await fetchUserDetails(userIds);
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
        userMap,
      };
    },
  };
  </script>
  
  <style scoped>
  .chat-messages {
    height: 80%;
    overflow-y: auto;
    margin-bottom: 16px;
    padding: 8px;
    background-color: #1e1e1e;
    border-radius: 8px;
  }

  .chat-message-input {
    width: 100%;
    display: flex;
    justify-content: center;  
  }
  
 
  </style>
  