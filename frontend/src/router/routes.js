const routes = [
  {
    path: '/',
    component: () => import('pages/LoginPage.vue'),
  },
  {
    path: '/register',
    component: () => import('pages/RegisterPage.vue'),
  },
  {
    path: '/dashboard',
    component: () => import('pages/DashboardPage.vue'),
    meta: { requiresAuth: true }, // Requiere autenticación
  },
];

export default routes;


