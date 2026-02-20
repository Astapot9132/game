<script setup lang="ts">
import { useUserStore } from '@/stores/user'

const userStore = useUserStore();
</script>

<template>
  <header class="topnav">
    <div class="topnav__inner">
      <div class="topnav__left">
        <span class="topnav__brand">Game</span>
        <nav class="topnav__links">
          <RouterLink class="topnav__link" to="/profile">Аккаунт</RouterLink>
        </nav>
      </div>

      <div class="topnav__right">
        <span v-if="userStore.isAuthenticated" class="topnav__nickname">
          {{ userStore.profile?.login }}
        </span>
        <RouterLink v-else class="topnav__link" to="/auth">Войти</RouterLink>
        <button
          v-if="userStore.isAuthenticated"
          type="button"
          class="topnav__logout"
          @click="userStore.logout"
        >
          Выйти
        </button>
      </div>
    </div>
  </header>
</template>

<style scoped>
.topnav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 8%;
  z-index: 10;
  background: #0b1220;
  color: #f8fafc;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 4px 12px rgb(0, 6, 15);
}

.topnav__inner {
  height: 100%;
  max-width: 100%;
  margin: 0 auto;
  padding: 0 10%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.topnav__left {
  display: flex;
  align-items: center;
  gap: 15%;
}

.topnav__brand {
  font-weight: 700;
  letter-spacing: 0.4px;
}

.topnav__links {
  display: flex;
  gap: 20%;
}

.topnav__link {
  color: #e2e8f0;
}

.topnav__link.router-link-active {
  color: #ffffff;
  text-decoration: underline;
  text-underline-offset: 6%;
}

.topnav__right {
  display: flex;
  align-items: center;
  gap: 18%;
}

.topnav__nickname {
  background: rgba(255, 255, 255, 0.12);
  padding: 10% 15%;
  border-radius: 999px;
  font-weight: 600;
  cursor: pointer;
}

.topnav__logout {
  border: none;
  border-radius: 15%;
  background: #f8fafc;
  color: #0b1220;
  padding: 12% 18%;
  cursor: pointer;
}
</style>