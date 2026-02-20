import { createRouter, createWebHistory } from 'vue-router';
import AuthView from '@/views/auth-view.vue';
import ProfileView from '@/views/profile-view.vue';
import { useUserStore } from '@/stores/user';


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: '/auth' },
    { path: '/auth', name: 'auth', component: AuthView },
    {
      path: '/profile',
      name: 'profile',
      component: ProfileView,
      meta: { requiresAuth: true },
    },
  ],
});

router.beforeEach(async (to) => {
  const userStore = useUserStore()
  if (!userStore.hasCheckedAuth && !userStore.loading) {
    await userStore.loadCurrentUser().catch(() => userStore.clear());
  }
  if (to.meta.requiresAuth && !userStore.isAuthenticated) {
    return { name: 'auth' };
  }
  if (to.name === 'auth' && userStore.isAuthenticated) {
    return { name: 'profile' };
  }
  return true;
});

export default router;