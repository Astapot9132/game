import api from '@/lib/api'

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