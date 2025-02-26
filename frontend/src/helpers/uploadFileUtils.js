import api from "../services/api";
import { useQuasar } from "quasar";

export async function uploadPhoto(file, player) {
  const $q = useQuasar();

  if (file.size > 2 * 1024 * 1024) {
    $q.notify({ type: "negative", message: "El archivo es demasiado grande (máximo 2MB)." });
    return;
  }

  if (!file.type.startsWith("image/")) {
    $q.notify({ type: "negative", message: "El archivo debe ser una imagen." });
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await api.post("/players/upload-photo", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
    });

    player.photo_url = response.data.photo_url;
    $q.notify({ type: "positive", message: "Foto de perfil actualizada exitosamente" });
  } catch (error) {
    console.error("Error al subir foto de perfil:", error.message);
    $q.notify({ type: "negative", message: "Error al subir foto de perfil" });
  }
}
