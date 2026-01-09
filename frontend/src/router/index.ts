import { createRouter, createWebHistory } from 'vue-router';
import AuthView from '@/views/auth-view.vue';
import DashboardView from '@/views/dashboard-view.vue';


function isAuthenticated(): boolean {
  return Boolean(localStorage.getItem('access_token'));
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: '/auth' },
    { path: '/auth', name: 'auth', component: AuthView },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: DashboardView,
      meta: { requiresAuth: true },
    },
  ],
});

router.beforeEach((to) => {
  if (to.meta.requiresAuth && !isAuthenticated()) {
    return { name: 'auth' };
  }
  if (to.name === 'auth' && isAuthenticated()) {
    return { name: 'dashboard' };
  }
  return true;
});

export default router;