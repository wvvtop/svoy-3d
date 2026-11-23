<template>
  <div class="navbar_right">
    <template v-if="authStore.isAuthenticated">
      <NavbarNotificationsComponent />

      <div class="navbar_right__profile">
        <ButtonLink to="/profile" text="Профиль" variant="nav"/>
      </div>
    </template>
    <template v-else>
      <ButtonLink :to="{ name: 'Login' }" text="Войти" variant="nav"/>
    </template>
  </div>
</template>

<script setup>
import ButtonLink from '@/components/ButtonLink.vue';
import { useAuthStore } from '@/stores/auth';
import NavbarNotificationsComponent from './NavbarNotificationsComponent.vue';
import { useNotificationsStore } from '@/stores/chatNotifications.js';
import { onMounted } from 'vue';


const authStore = useAuthStore()

const notifications = useNotificationsStore()

onMounted(() => {
  notifications.fetchUnread()
})
</script>


<style scoped>
.navbar_right {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 15px;
}
</style>
