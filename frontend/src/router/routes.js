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
  // Otras rutas...
  { path: "/:catchAll(.*)", redirect: "/" },
];

export default routes;




