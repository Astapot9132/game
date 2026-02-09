import { defineStore } from 'pinia';
import { api, logout_user, csrf_token } from '@/lib/api';
import router from '@/router';


export const useUserStore = defineStore('user', {
  state: () => ({
    profile: null as null | { id: string; login: string; email: string },
    loading: false,
    csrfToken: string | null = null;
    hasCheckedAuth: false,
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.profile),
  },
  actions: {
    async loadCurrentUser() {
      this.loading = true;
      try {
        const { data } = await api.get('/auth/me');
        this.profile = data;
      } catch {
        this.profile = null
      }
      finally {
        this.hasCheckedAuth = true;
        this.loading = false;
      }
    },
    clear() {
      this.profile = null;
      this.csrfToken = null;
      this.hasCheckedAuth = false;
    },
    async csrf() {
        const { data } = await api.get<{ csrf_token: string }>('/auth/csrf');
        this.csrfToken = data.csrf_token;
    }
    async logout() {
      await logout_user();
      this.clear();
      router.push({ name: 'auth' });
    },
  },
});