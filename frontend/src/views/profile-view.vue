<script setup lang="ts">
import {useUserStore} from '@/stores/user'
import {ref} from 'vue'


const activeTab = ref('profile')
const userStore = useUserStore();

const tabs = [
  {id: "profile", label: "Профиль", icon: "👤"},
  {id: "history", label: "История игр", icon:  '⚔️' },
  {id: "settings", label: "Настройки", icon: "⚙️"},
  {id: 'achievements', label: 'Достижения', icon: '🏆' }
]

function switchTab(tabId: string) {
  activeTab.value = tabId
}
</script>

<template>
  <section class="profile">
    
    <div class="profile-card">
      <div class="tabs-navigation">
          <nav class="tabs">
            <button
              v-for="tab in tabs"
              :key="tab.id"
              :class="['tab-button', { active: activeTab === tab.id }]"
              @click="switchTab(tab.id)"
            >
              <span class="tab-icon">{{ tab.icon }}</span>
              <span class="tab-label">{{ tab.label }}</span>
            </button>
          </nav>
        </div>
        
      <div class="tab-content">
        <div v-if="activeTab === 'profile'" class="tab-pane">
          <h2>👤 Профиль игрока</h2>
          <div class="profile-info">
            <div class="info-card">
              <p><strong>Логин:</strong> {{ userStore.profile?.login }}</p>
              <p><strong>E-mail:</strong> {{ userStore.profile?.email || 'Не указан'}}</p>
            </div>
            
          </div>
        </div> 
      </div>    
    </div>
  </section>
</template>


<style scoped>
.profile {
  height: 90vh;
  min-height: 90vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.profile-card {
  background: white;
  width: 90%;
  height: 90%;
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 20px 70px rgb(15 23 42 / 0.2);
  display: flex;
  flex-direction: column;
}

/* .page-header {
  margin-bottom: 24px;
} */

/* .page-header h1 {
  margin: 0;
  color: #0f172a;
} */

/* .subtitle {
  color: #64748b;
  margin-top: 4px;
} */

/* Навигация по вкладкам */
.tabs-navigation {
  border-bottom: 2px solid #e2e8f0;
  margin-bottom: 24px;
  overflow-x: unset;
  white-space: nowrap;
}

.tabs {
  display: flex;
  /* gap: 4px; */
  /* min-width: max-content; */
  /* width: 100; */
}

.tab-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border: none;
  background: transparent;
  color: #64748b;
  cursor: pointer;
  border-radius: 8px 8px 0 0;
  transition: all 0.2s ease;
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  flex: 1 1 0;
  border: 2px solid #e2e8f0;
  border-bottom: unset;
}

.tab-button:hover {
  background: #f1f5f9;
  color: #475569;
}

.tab-button.active {
  background: #0f172a;
  color: white;
  position: relative;
}

.tab-button.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  right: 0;
  height: 2px;
  background: #0f172a;
}

.tab-icon {
  font-size: 18px;
}

.tab-label {
  margin-top: 2px;
}

/* Контент вкладок */
.tab-content {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.tab-pane {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Стили для контента */
.profile-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.info-card {
  background: #f8fafc;
  padding: 20px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.info-card h3 {
  margin-top: 0;
  color: #0f172a;
  border-bottom: 2px solid #0f172a;
  padding-bottom: 8px;
}

.xp-bar {
  height: 10px;
  background: #e2e8f0;
  border-radius: 5px;
  margin-top: 8px;
  overflow: hidden;
}

.xp-progress {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6);
  transition: width 0.5s ease;
}

/* Стили для истории боев */
.battles-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 20px;
}

.battle-card {
  background: #f8fafc;
  padding: 16px;
  border-radius: 12px;
  border-left: 4px solid #0f172a;
}

.battle-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.battle-result.win {
  color: #10b981;
  font-weight: bold;
}

.battle-result.lose {
  color: #ef4444;
  font-weight: bold;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #64748b;
}

/* Стили для настроек */
.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
  margin-top: 20px;
}

.setting-group {
  background: #f8fafc;
  padding: 20px;
  border-radius: 12px;
}

.setting-item {
  margin: 16px 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.setting-item label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.setting-item select {
  padding: 8px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  background: white;
}

.settings-actions {
  display: flex;
  gap: 12px;
  margin-top: 30px;
}

/* Стили для достижений и инвентаря */
.achievements-grid,
.inventory-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  margin-top: 20px;
}

.achievement-card,
.item-card {
  background: #f8fafc;
  padding: 16px;
  border-radius: 12px;
  text-align: center;
  border: 2px solid #e2e8f0;
  transition: transform 0.2s ease;
}

.achievement-card.unlocked {
  border-color: #10b981;
  background: #f0fdf4;
}

.achievement-card:hover,
.item-card:hover {
  transform: translateY(-2px);
}

.achievement-icon,
.item-icon {
  font-size: 40px;
  margin-bottom: 12px;
}

.achievement-progress {
  background: #e2e8f0;
  height: 6px;
  border-radius: 3px;
  margin-top: 12px;
  position: relative;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: #3b82f6;
}

.progress-text {
  position: absolute;
  top: -20px;
  left: 0;
  right: 0;
  font-size: 12px;
  color: #64748b;
}

.item-count {
  display: inline-block;
  background: #0f172a;
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  margin-top: 8px;
}

.item-actions {
  margin-top: 12px;
}

/* Кнопки */
button {
  border: none;
  border-radius: 10px;
  background: #0f172a;
  color: white;
  padding: 12px 20px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}

button:hover {
  background: #1e293b;
  transform: translateY(-1px);
}

button:disabled {
  background: #cbd5e1;
  cursor: not-allowed;
  transform: none;
}

.start-battle-btn {
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  margin-top: 16px;
}

.save-btn {
  background: #10b981;
}

.reset-btn {
  background: #ef4444;
}

.use-btn {
  background: #3b82f6;
  padding: 8px 16px;
  font-size: 12px;
}

/* Адаптивность */
@media (max-width: 768px) {
  .tabs {
    flex-wrap: wrap;
  }
  
  .profile__card {
    width: 95%;
    height: 95%;
    padding: 16px;
  }
  
  .tab-button {
    padding: 10px 16px;
    font-size: 13px;
  }
  
  .tab-icon {
    font-size: 16px;
  }
  
  .settings-actions {
    flex-direction: column;
  }
  
  .achievements-grid,
  .inventory-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  }
}
</style>