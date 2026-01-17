import { defineStore } from 'pinia';
import { api, logout_user } from '@/lib/api';
import router from '@/router';


export const useUserStore = defineStore('user', {
  state: () => ({
    profile: null as null | { id: string; login: string; email: string },
    loading: false,
    hasCheckedAuth: false,
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.profile),
  },
  actions: {
    async loadCurrentUser() {
      this.loading = true;
      this.hasCheckedAuth = true;
      try {
        const { data } = await api.get('/auth/me');
        this.profile = data;
      } catch {
        this.profile = null
      }
      finally {
        this.loading = false;
      }
    },
    clear() {
      this.profile = null;
      this.hasCheckedAuth = false;
    },
    async logout() {
      await logout_user();
      this.clear();
      router.push({ name: 'auth' });
    },
  },
});