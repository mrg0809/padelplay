import { name } from "dayjs/locale/es-mx";

const routes = [
  { path: "/", component: () => import("pages/LoginPage.vue") },
  {
    path: "/datosclase",
    name: "LessonSummary",
    component: () => import("src/pages/player/LessonSummary.vue"),
  },
  {
    path: "/datosreserva",
    name: "ReservationSummary",
    component: () => import("src/pages/player/ReservationSummary.vue"),
  },
  {
    path: "/resumenorden",
    name: "OrderSummary",
    component: () => import("src/pages/player/OrderSummary.vue"),
  },
  {
    path: "/stripe-payment",
    name: "StripePayment",
    component: () => import("src/pages/StripePayment.vue"),
  },
  { path: "/forgot-password", component: () => import("pages/RecoveryPassword.vue")},
  { path: "/reset-password", component: () => import("pages/ResetPassword.vue")},
  { path: "/signup", component: () => import("pages/RegisterPage.vue")},
  
  { 
    path: "/admin/usuarios", 
    component: () => import("pages/admin/ManageUsers.vue"),
    meta: { requiresAuth: true },
  },
  { 
    path: "/admin/padelite", 
    component: () => import("pages/admin/CaptureScores.vue"),
    meta: { requiresAuth: true },
  },
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
    name: "DashboardPlayer",
    meta: { requiresAuth: true },
  },
  { 
    path: "/club/canchas", 
    component: () => import("src/pages/club/ManageCourts.vue"),
    meta: { requiresAuth: true },
  },
  { 
    path: "/club/clientes", 
    component: () => import("src/pages/club/ClubClients.vue"),
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
    path: "/club/bloqueos", 
    component: () => import("src/pages/club/ManageScheduleBlocks.vue"),
    meta: { requiresAuth: true },
  },
  { 
    path: "/club/clases", 
    component: () => import("src/pages/club/ManageLessons.vue"),
    meta: { requiresAuth: true },
  },
  { 
    path: "/club/configuracion", 
    component: () => import("src/pages/club/ClubSettings.vue"),
    meta: { requiresAuth: true },
  },
  { 
    path: "/club/cuentas", 
    component: () => import("src/pages/club/ManageAccounts.vue"),
    meta: { requiresAuth: true },
  },
  { 
    path: "/club/facturas", 
    component: () => import("src/pages/club/ClubInvoices.vue"),
    meta: { requiresAuth: true },
  },
  { 
    path: "/club/horarios", 
    component: () => import("src/pages/club/ManageSchedules.vue"),
    meta: { requiresAuth: true },
  },
  { 
    path: "/club/inicio", 
    component: () => import("src/pages/DashboardClub.vue"),
    meta: { requiresAuth: true },
  },
  { 
    path: "/club/instructores", 
    component: () => import("src/pages/club/ManageCoaches.vue"),
    meta: { requiresAuth: true },
  },
  { 
    path: "/club/pagos", 
    component: () => import("src/pages/club/ClubPayments.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: '/club/coach-profile/:id',
    name: 'CoachProfile',
    component: () => import("src/pages/club/CoachProfile.vue"),
    meta: { requiresAuth: true },
  },
  { 
    path: "/club/productos", 
    component: () => import("src/pages/club/ManageProducts.vue"),
    meta: { requiresAuth: true },
  },
  { 
    path: "/club/promociones", 
    component: () => import("src/pages/club/ManageDiscounts.vue"),
    meta: { requiresAuth: true },
  },
  { 
    path: "/club/agenda", 
    component: () => import("src/pages/club/ViewSchedule.vue"),
    meta: { requiresAuth: true },
  },
  { 
    path: "/club/comunidad", 
    component: () => import("src/pages/club/ClubCommunity.vue"),
    meta: { requiresAuth: true },
  },
  { 
    path: "/club/creartorneos", 
    component: () => import("src/pages/club/CreateTournament.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/club/preview-tournament",
    name: "PreviewTournament",
    component: () => import("src/pages/club/PreviewTournament.vue"),
  },
  { 
    path: "/club/reportes", 
    component: () => import("src/pages/club/ClubReporting.vue"),
    meta: { requiresAuth: true },
  },
  { 
    path: "/club/soporte", 
    component: () => import("src/pages/club/SupportOptions.vue"),
    meta: { requiresAuth: true },
  },
  { 
    path: "/club/torneos", 
    component: () => import("src/pages/club/ListTournaments.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/club/editartorneo/:tournamentId",
    component: () => import("src/pages/club/EditTournament.vue"),
    meta: { requiresAuth: true },
    name: "EditTournament"
  },
  {
    path: "/club/:clubId",
    name: "ClubDetails",
    component: () => import("src/pages/club/ClubDetails.vue"),
  },
  { 
    path: "/matches/:matchId/chat", 
    component: () => import("pages/player/MatchChat.vue"),
    meta: { requiresAuth: true },
    name: "MatchChat"
  },
  { 
    path: "/notifications", 
    component: () => import("src/pages/ShowNotifications.vue"),
    meta: { requiresAuth: true },
  },
  { 
    path: "/player/clases", 
    component: () => import("src/pages/player/ListLessonsClubs.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/player/coach/:coachId",
    name: "CoachDetails",
    component: () => import("src/pages/player/CoachDetails.vue"),
  },
  { 
    path: "/player/community", 
    component: () => import("src/pages/player/PlayerCommunity.vue"),
    meta: { requiresAuth: true },
  },
  { 
    path: "/player/editarinfo", 
    component: () => import("src/pages/player/EditPlayerInfo.vue"),
    meta: { requiresAuth: true },
  },
  { 
    path: "/player/inicio", 
    component: () => import("src/pages/DashboardPlayer.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/player/detallessesion/:lessonId",
    name: "LessonDetails",
    component: () => import("src/pages/player/LessonDetails.vue"),
  },
  {
    path: "/player/privatelesson/:lessonId",
    name: "PrivateLessonDetails",
    component: () => import("src/pages/player/ClassDetails.vue"),
  },
  { 
    path: "/player/match/:matchId", 
    component: () => import("src/pages/player/MatchDetails.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/player/formasdepago",
    name: "PaymentMethods",
    component: () => import("src/pages/player/PaymentMethods.vue"),
  },
  { 
    path: "/player/perfil", 
    component: () => import("pages/player/PlayerProfile.vue"),
    meta: { requiresAuth: true },
  },
  { 
    path: "/player/reservas", 
    component: () => import("src/pages/player/ListClubs.vue"),
    meta: { requiresAuth: true },
  },
  { 
    path: "/player/unete", 
    component: () => import("src/pages/player/ListOpenGames.vue"),
    meta: { requiresAuth: true },
  },
  { 
    path: "/player/torneos", 
    component: () => import("src/pages/player/ListTournaments.vue"),
    meta: { requiresAuth: true },
  },
  { 
    path: "/privacy", 
    component: () => import("src/pages/support/PrivacyNotice.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/tournamet/checkout",
    name: "TournamentCheckout",
    component: () => import("src/pages/tournament/TournamentCheckout.vue"),
  },
  {
    path: "/padelite",
    component: () => import("src/pages/tournament/PadeliteTournament.vue"),
  },
  {
    path: "/padelite/cuadro-final",
    component: () => import("src/pages/tournament/PadeliteFinalStage.vue"),
  },
  {
    path: "/tournament/:tournamentId",
    component: () => import("src/pages/tournament/TournamentDetails.vue"),
    meta: { requiresAuth: true },
    name: "TournamentDetails"
  },
  { path: "/inicio", component: () => import("pages/Home.vue") },
  { path: "/torneos", component: () => import("pages/Torneos.vue") },
  { path: "/asociaciones", component: () => import("pages/Asociaciones.vue") },
  { path: "/perfil", component: () => import("pages/Perfil.vue") },
  // Otras rutas...
  { path: "/:catchAll(.*)", name: "NotFound", component: () => import("pages/ErrorNotFound.vue") },
];

export default routes;




