<template>
  <div class="navbar_center">
    <template v-if="authStore.isAuthenticated()">
      <div class="navbar_center">
        <ButtonLink :to="{ name: 'orders' }" text="Заказы" variant="nav"/>
      </div>
    </template>
  </div>
</template>

<script setup>
import ButtonLink from '@/components/ButtonLink.vue';
import { useAuthStore } from '@/stores/auth';


const authStore = useAuthStore()
</script>
