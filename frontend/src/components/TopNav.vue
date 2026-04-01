<script setup lang="ts">
import { useUserStore } from '@/stores/user'

const userStore = useUserStore();
</script>

<template>
  <header class="topnav">
    <div class="topnav__inner">
      <div class="topnav__left">
        <span class="topnav__brand">Game</span>
      </div>

      <div class="topnav__right">
          <RouterLink v-if="userStore.isAuthenticated" class="topnav__button" to="/profile">Аккаунт</RouterLink>
          <RouterLink v-else class="topnav__button" to="/auth">Войти</RouterLink>
        <button
          v-if="userStore.isAuthenticated"
          type="button"
          class="topnav__button"
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
  padding: 0 5% 0% 6%;
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



.topnav__right {
  display: flex;
  align-items: center;
  gap: 12px;
  /* width: auto; */
}

.topnav__button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  /* box-sizing: border-box; */
  border: none;
  width: 120px;
  /* flex: 0 0 120px; */
  font-weight: 600;
  border-radius: 15%;
  background: #f8fafc;
  color: #0b1220;
  padding: 11px 15px;
  cursor: pointer;
  text-decoration: unset;
  line-height: 1;
  font: inherit;
  font-weight: 600;
}
</style>