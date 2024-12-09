const routes = [
  { path: "/", component: () => import("pages/LoginPage.vue") },
  { 
    path: "/dashboard/superuser", 
    component: () => import("pages/DashboardSuperuser.vue"),
    meta: { requiresAuth: true },
  },
  { 
    path: "/dashboard/admin", 
    component: () => import("pages/DashboardAdmin.vue"),
    meta: { requiresAuth: true },
  },
  { 
    path: "/dashboard/club", 
    component: () => import("pages/DashboardClub.vue"),
    meta: { requiresAuth: true },
  },
  { 
    path: "/dashboard/player", 
    component: () => import("pages/DashboardPlayer.vue"),
    meta: { requiresAuth: true },
  },
  { 
    path: "/club/canchas", 
    component: () => import("src/pages/club/ManageCourts.vue"),
    meta: { requiresAuth: true },
  },
  { path: "/inicio", component: () => import("pages/Home.vue") },
  { path: "/torneos", component: () => import("pages/Torneos.vue") },
  { path: "/asociaciones", component: () => import("pages/Asociaciones.vue") },
  { path: "/perfil", component: () => import("pages/Perfil.vue") },
  // Otras rutas...
  { path: "/:catchAll(.*)", redirect: "/" },
];

export default routes;




