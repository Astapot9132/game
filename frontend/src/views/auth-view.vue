
<script setup lang="ts">
import { reactive, ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { login_user, register_user } from '@/lib/api';
import axios from 'axios';
import router from '@/router';
import {useUserStore} from '@/stores/user'

interface AuthFormState {
  login: string;
  password: string;
}

const userStore = useUserStore()
const mode = ref<'login' | 'register'>('login');
const isLoading = ref(false);
const error = ref('');
const form = reactive<AuthFormState>({
  login: '',
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
      password: form.password,
      login: form.login,
    };

    if (mode.value === 'login') {

      await login_user(payload);
      await userStore.loadCurrentUser();
      console.log(userStore.profile)
      await router.push({ name: 'dashboard' });
    } else {
      await register_user(payload);
      mode.value = 'login';
    }

  } catch (err) {
    if (axios.isAxiosError(err)) {
      const status = err.response?.status
      if (status === 403) {
        error.value = err.response?.data?.detail;
      } else if (status) {
        error.value = `Статус ошибки ${status}.`
    } else {
      error.value = 'Сервер не доступен'
    }} else {
      error.value = 'Внутренняя ошибка сервера'
    }
    console.log(err)
  } finally {
    isLoading.value = false;
  }
}
</script>

<template>
  <section class="auth">
    <div class="auth__card">
      <h1 class="auth__title">{{ mode === 'login' ? 'Вход' : 'Регистрация' }}</h1>
      <form class="auth__form" @submit.prevent="handleSubmit()">
        <label class="auth__label">
          <input
            v-model.trim="form.login"
            type="text"
            required
            placeholder="Введите никнейм"
          />
        </label>

        <label class="auth__label">
          <input
            v-model.trim="form.password"
            type="password"
            required
            autocomplete="current-password"
            placeholder="Введите пароль"
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