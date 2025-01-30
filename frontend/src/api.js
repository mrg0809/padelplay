import axios from "axios";

const api = axios.create({
  baseURL: "http://192.168.1.133:8000/", // URL de tu backend
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token"); // Suponiendo que el token está en localStorage
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export function getUserFromToken() {
  const token = localStorage.getItem("token");
  if (!token) return null;

  try {
    const base64Url = token.split(".")[1];
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
    const decodedPayload = JSON.parse(atob(base64));
    return decodedPayload; // Contiene información como club_id
  } catch (error) {
    console.error("Error decoding token:", error);
    return null;
  }
}

export default api;
