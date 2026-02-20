<script setup lang="ts">
import {useUserStore} from '@/stores/user'
const userStore = useUserStore();

</script>

<template>
  <section class="profile">
    
    <div class="dashboard__card">
      <h1>Главная страница игры</h1>
      <p>Здесь позже появится список действий/боёв. Пока что это заглушка.</p>
      <button type="button" @click="userStore.logout">Выйти</button>
    </div>
  </section>
</template>


<style scoped>


.profile {
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