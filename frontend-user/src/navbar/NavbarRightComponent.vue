<template>
  <div class="navbar_right">
    <template v-if="authStore.isAuthenticated()">
      <div class="navbar_right__profile">
        <ButtonLink to="/profile" text="Профиль" variant="nav"/>
      </div>
    </template>
    <template v-else>
      <ButtonLink to="/login" text="Войти" variant="nav"/>
    </template>
  </div>
</template>

<script setup>
import ButtonLink from '@/components/ButtonLink.vue';
import { useAuthStore } from '@/stores/auth';


const authStore = useAuthStore()
</script>
