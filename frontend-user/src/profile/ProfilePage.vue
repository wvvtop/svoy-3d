<script setup lang="ts">
import ButtonComponent from '@/components/ButtonComponent.vue';
import PageLayout from '@/layouts/PageLayout.vue';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore()

const handleLogout = () => {
  authStore.logout()
}
</script>

<template>
  <PageLayout>
    <template #page__content_item>
      <div>
        <p>Разлогинеться</p>
        <ButtonComponent text="Выйти!" @action="handleLogout" variant="delete"></ButtonComponent>
      </div>
    </template>
  </PageLayout>
</template>
