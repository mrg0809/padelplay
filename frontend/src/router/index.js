import { route } from "quasar/wrappers";
import { createRouter, createWebHistory } from "vue-router";
import routes from "./routes"; // Correctamente importado

export default route(function () {
  const Router = createRouter({
    history: createWebHistory(),
    routes, // Aquí se utiliza el arreglo importado
  });

  // Middleware para proteger rutas
  
  Router.beforeEach((to, from, next) => {
    const requiresAuth = to.meta?.requiresAuth;
    const token = localStorage.getItem("token");

    if (requiresAuth && !token) {
      next("/"); // Redirigir al login si no está autenticado
    } else {
      next(); // Continuar si no requiere autenticación o si hay un token
    }
  });

  return Router;
});


