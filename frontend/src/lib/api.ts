import { getCookie } from '@/lib/cookie'
import axios from 'axios';
import {useUserStore} from '@/stores/user'

let isRefreshing = false;
let pendingRequests: ((tokenUpdated: boolean) => void)[] = [];
const userStore = useUserStore()

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true,
});

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
      await userStore.logout()
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


export type AuthResponse = {
  access_token: string;
  refresh_token?: string;
  token_type: string;
}

export type LoginPayload = {
  login: string;
  password: string;
}

export type RegisterPayload = LoginPayload

export async function login_user(payload: LoginPayload): Promise<void> {
  const { data } = await api.post('/auth/login', payload);
  return data;
}

export async function logout_user(): Promise<void> {
  const { data } = await api.post('/auth/logout');
  return data
}

export async function register_user(payload: RegisterPayload): Promise<void> {
    const { data } = await api.post('/auth/registration', payload);
    return data
}

export async function refresh_user(): Promise<void> {
    const { data } = await api.post('/auth/refresh');
    return data
}

export default api;