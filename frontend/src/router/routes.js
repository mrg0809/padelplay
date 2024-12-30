const routes = [
  { path: "/", component: () => import("pages/LoginPage.vue") },
  {
    path: "/checkout",
    name: "CheckoutPage",
    component: () => import("src/pages/CheckoutPage.vue"),
  },
  { path: "/signup", component: () => import("pages/RegisterPage.vue")},
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
  { 
    path: "/club/perfil", 
    component: () => import("src/pages/club/EditClubInfo.vue"),
    meta: { requiresAuth: true },
  },
  { 
    path: "/club/admin", 
    component: () => import("src/pages/club/ManageClub.vue"),
    meta: { requiresAuth: true },
  },
  { 
    path: "/club/horarios", 
    component: () => import("src/pages/club/ManageSchedules.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/club/:clubId",
    name: "ClubDetails",
    component: () => import("src/pages/club/ClubDetails.vue"),
  },
  { 
    path: "/player/editarinfo", 
    component: () => import("src/pages/player/EditPlayerInfo.vue"),
    meta: { requiresAuth: true },
  },
  { 
    path: "/player/perfil", 
    component: () => import("src/pages/player/PlayerProfile.vue"),
    meta: { requiresAuth: true },
  },
  { 
    path: "/player/reservas", 
    component: () => import("src/pages/player/ListClubs.vue"),
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




