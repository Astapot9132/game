# Snippet Dropzone

## Пошаговый план запуска фронтенда (Vue 3 + Vite)
1. Установи Node.js ≥ 18 (если ещё не установлен) и перейди в корень репозитория `game`.
2. Создай новый проект: `npm create vite@latest frontend -- --template vue-ts` — утилита сама подготовит структуру `frontend/`.
3. Перейди в каталог `frontend` и подтяни зависимости: `npm install`. Дополнительно поставь полезные пакеты: `npm install axios pinia vue-router@4` и дев-зависимости `npm install -D @types/node` (если шаблон их не добавил).
4. Скопируй сниппеты ниже в соответствующие файлы (создай папки `src/lib`, `src/router`, `src/views`, `src/components`, `src/assets` если их нет). Каждый блок уже учитывает рекомендации из `AGENTS.md`.
5. Проверь переменные окружения: создай `.env` на основе `.env.example`, пропиши `VITE_API_BASE_URL=http://127.0.0.1:8000` (или свой URL FastAPI). Vite автоматически подставит значение в рантайме.
6. Запусти локально: `npm run dev` (во фронтенд-каталоге). Авторизуйся через форму — после успешного ответа токены сохранятся в `localStorage`, а роутер перенаправит на заглушку `/dashboard`.
7. Для будущих страниц оставь `RouterView` в `App.vue` и добавляй новые маршруты в `router/index.ts`. Не забудь про lint/format (`npm run build` проверит типы перед релизом).

## Сниппеты для копирования

frontend/.env.example
```
VITE_API_BASE_URL=http://127.0.0.1:8000
```

frontend/src/lib/api.ts
```
import axios from 'axios';

// Конфигурируем общий HTTP-клиент, чтобы в одном месте менять базовый URL или заголовки.
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000',
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true, // пригодится, если бекенд выставит куки (refresh токены и т.п.)
});

export interface AuthResponse {
  access_token: string;
  refresh_token?: string;
  token_type: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload extends LoginPayload {
  username: string;
}

export async function login(payload: LoginPayload): Promise<AuthResponse> {
  const { data } = await api.post<AuthResponse>('/auth/login', payload);
  return data;
}

export async function register(payload: RegisterPayload): Promise<AuthResponse> {
  const { data } = await api.post<AuthResponse>('/auth/register', payload);
  return data;
}

export default api;
```

frontend/src/router/index.ts
```
import { createRouter, createWebHistory } from 'vue-router';
import AuthView from '@/views/AuthView.vue';
import DashboardView from '@/views/DashboardView.vue';

// Небольшой хелпер, чтобы не тянуть внешние стейт-менеджеры на старте.
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
```

frontend/src/main.ts
```
import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import './assets/base.css';

const app = createApp(App);
app.use(router);
app.mount('#app');
```

```
ОСТАНОВИЛСЯ ТУТ -----------------------------------------------------------
```
frontend/src/App.vue
```
<template>
  <!-- RouterView подставляет нужную страницу в зависимости от URL -->
  <RouterView />
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router';
</script>
```

frontend/src/assets/base.css
```
:root {
  font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  line-height: 1.5;
  color: #0f172a;
  background-color: #f8fafc;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  min-height: 100vh;
  background: linear-gradient(120deg, #0f172a, #1d4ed8);
}

#app {
  min-height: 100vh;
}
```

frontend/src/views/AuthView.vue
```
<template>
  <section class="auth">
    <div class="auth__card">
      <h1 class="auth__title">{{ mode === 'login' ? 'Вход' : 'Регистрация' }}</h1>
      <form class="auth__form" @submit.prevent="handleSubmit">
        <label class="auth__label">
          <span>E-mail</span>
          <input
            v-model.trim="form.email"
            type="email"
            required
            autocomplete="email"
            placeholder="you@example.com"
          />
        </label>

        <label v-if="mode === 'register'" class="auth__label">
          <span>Никнейм</span>
          <input
            v-model.trim="form.username"
            type="text"
            required
            minlength="3"
            placeholder="player_one"
          />
        </label>

        <label class="auth__label">
          <span>Пароль</span>
          <input
            v-model.trim="form.password"
            type="password"
            required
            minlength="6"
            autocomplete="current-password"
          />
        </label>

        <p v-if="error" class="auth__error">{{ error }}</p>

        <button class="auth__submit" :disabled="isLoading">
          {{ isLoading ? 'Отправка...' : submitLabel }}
        </button>
      </form>

      <button class="auth__switch" type="button" @click="toggleMode" :disabled="isLoading">
        {{ mode === 'login' ? 'Нет аккаунта? Зарегистрируйся' : 'Уже есть аккаунт? Войти' }}
      </button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { reactive, ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { login, register } from '@/lib/api';

interface AuthFormState {
  email: string;
  username: string;
  password: string;
}

const router = useRouter();
const mode = ref<'login' | 'register'>('login');
const isLoading = ref(false);
const error = ref('');
const form = reactive<AuthFormState>({
  email: '',
  username: '',
  password: '',
});

const submitLabel = computed(() => (mode.value === 'login' ? 'Войти' : 'Создать аккаунт'));

function toggleMode() {
  error.value = '';
  mode.value = mode.value === 'login' ? 'register' : 'login';
}

async function handleSubmit() {
  try {
    isLoading.value = true;
    error.value = '';

    const payload = {
      email: form.email,
      password: form.password,
      username: form.username,
    };

    const response =
      mode.value === 'login' ? await login(payload) : await register(payload);

    localStorage.setItem('access_token', response.access_token);
    if (response.refresh_token) {
      localStorage.setItem('refresh_token', response.refresh_token);
    }

    await router.push({ name: 'dashboard' });
  } catch (err) {
    error.value = 'Не удалось отправить данные. Проверь ввод или сервер.';
    console.error(err);
  } finally {
    isLoading.value = false;
  }
}
</script>

<style scoped>
.auth {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 16px;
}

.auth__card {
  width: min(420px, 100%);
  padding: 32px;
  border-radius: 16px;
  background: #fff;
  box-shadow: 0 20px 70px rgb(15 23 42 / 0.2);
}

.auth__title {
  margin: 0 0 24px;
  text-align: center;
}

.auth__form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.auth__label {
  display: flex;
  flex-direction: column;
  font-size: 14px;
  color: #0f172a;
  gap: 6px;
}

.auth__label input {
  border: 1px solid #cbd5f5;
  border-radius: 10px;
  padding: 12px;
  font-size: 16px;
}

.auth__submit {
  border: none;
  border-radius: 12px;
  padding: 14px;
  font-size: 16px;
  font-weight: 600;
  color: white;
  background: linear-gradient(120deg, #2563eb, #7c3aed);
  cursor: pointer;
}

.auth__submit:disabled {
  opacity: 0.6;
  cursor: progress;
}

.auth__switch {
  margin-top: 12px;
  width: 100%;
  border: none;
  background: transparent;
  color: #2563eb;
  cursor: pointer;
}

.auth__error {
  margin: 0;
  color: #dc2626;
  font-size: 14px;
}
</style>
```

frontend/src/views/DashboardView.vue
```
<template>
  <section class="dashboard">
    <div class="dashboard__card">
      <h1>Главная страница игры</h1>
      <p>Здесь позже появится список действий/боёв. Пока что это заглушка.</p>
      <button type="button" @click="logout">Выйти</button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';

const router = useRouter();

function logout() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  router.push({ name: 'auth' });
}
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.dashboard__card {
  background: white;
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 20px 70px rgb(15 23 42 / 0.2);
  text-align: center;
}

button {
  margin-top: 16px;
  border: none;
  border-radius: 10px;
  background: #0f172a;
  color: white;
  padding: 12px 20px;
  cursor: pointer;
}
</style>
```

## Что проверить после копирования
- `npm run dev` запускается без ошибок, страница по адресу `http://localhost:5173` открывается.
- При неправильных данных форма показывает сообщение об ошибке (см. `error.value`).
- После успешной авторизации токены появляются в `Application → Local Storage` (вкладка браузерных девтулов) и происходит редирект.
- В `router.beforeEach` можно подключить реальную проверку токена (например, запрос `/auth/me`) — оставь TODO после того, как появится соответствующая ручка на бэке.

