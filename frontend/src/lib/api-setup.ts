import type { Pinia } from 'pinia';
import { useUserStore } from '@/stores/user';
import { api, refresh_user } from '@/lib/api';

let isRefreshing = false;
let pendingRequests: ((tokenUpdated: boolean) => void)[] = [];
let isConfigured = false;

export function setupApi(pinia: Pinia) {
  if (isConfigured) return;
  isConfigured = true;

  const userStore = useUserStore(pinia);

  api.interceptors.request.use(async (config) => {
    const method = config.method?.toLowerCase();
    const needsCsrf = method && !['get', 'head', 'options'].includes(method);

    if (needsCsrf) {
      if (!userStore.csrfToken) {
        await userStore.csrf();
      }
      config.headers = config.headers ?? {};
      config.headers['X-CSRF-Token'] = userStore.csrfToken;
    }
    return config;
   });

  api.interceptors.response.use(
    (res) => res,
    async (error) => {
      const { config, response } = error;
      if (response?.status === 403) {
        await userStore.logout();
        return Promise.reject(error);
      }
      if (response?.status !== 401 || config._retry) {
        return Promise.reject(error);
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          pendingRequests.push((tokenUpdated) => {
            if (tokenUpdated) {
              resolve(api(config));
            } else {
              reject(error);
            }
          });
        });
      }

      config._retry = true;
      isRefreshing = true;
      try {
        await refresh_user();
        pendingRequests.forEach((cb) => cb(true));
        return api(config);
      } catch (refreshErr) {
        pendingRequests.forEach((cb) => cb(false));
        throw refreshErr;
      } finally {
        pendingRequests = [];
        isRefreshing = false;
      }
    }
  );
}