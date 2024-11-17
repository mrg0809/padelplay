import { route } from 'quasar/wrappers';
import { createRouter, createWebHistory } from 'vue-router';
import routes from './routes';

export default route(function () {
  const Router = createRouter({
    history: createWebHistory(),
    routes,
  });

// Middleware para proteger rutas
Router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth) {
    const token = localStorage.getItem('token');
    if (!token) {
      // Si no hay token, redirigir al login
      next('/');
    } else {
      // Si hay token, permitir acceso
      next();
    }
  } else {
    // Si no requiere autenticación, continuar
    next();
  }
});


  return Router;
});

