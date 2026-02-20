
import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import './assets/base.css';
import { createPinia } from 'pinia';
import { setupApi } from '@/lib/api-setup';

const app = createApp(App);
const pinia = createPinia();
app.use(pinia);
setupApi(pinia);
app.use(router);
app.mount('#app');
