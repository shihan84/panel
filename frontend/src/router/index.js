import { createRouter, createWebHistory } from 'vue-router';
import store from '../store';
import Login from '../views/Login.vue';
import ServerManagement from '../views/admin/ServerManagement.vue';
import ClientDashboard from '../views/client/ClientDashboard.vue';

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/admin/servers',
    name: 'ServerManagement',
    component: ServerManagement,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/dashboard',
    name: 'ClientDashboard',
    component: ClientDashboard,
    meta: { requiresAuth: true }
  },
  // Redirect root to login or appropriate dashboard
  {
    path: '/',
    redirect: () => {
      if (store.getters.isAuthenticated) {
        return store.getters.isAdmin ? '/admin/servers' : '/dashboard';
      }
      return '/login';
    }
  }
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
});

router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
  const requiresAdmin = to.matched.some(record => record.meta.requiresAdmin);
  const isAuthenticated = store.getters.isAuthenticated;
  const isAdmin = store.getters.isAdmin;

  if (requiresAuth && !isAuthenticated) {
    return next('/login');
  }

  if (requiresAdmin && !isAdmin) {
    // Redirect non-admins away from admin pages
    return next('/dashboard'); 
  }

  next();
});

export default router;
