<script setup>
import ButtonLink from '@/components/ButtonLink.vue';
import PageLayout from '@/layouts/PageLayout.vue';
import { useRoute } from 'vue-router';

const route = useRoute();
</script>

<template>
  <PageLayout>
    <template #page__content_item>
      <div class="orders">
        <header class="orders__header">
          <nav class="orders__header-nav">
            <ButtonLink
              :to="{ name: 'active-orders' }"
              class="orders__nav-link"
              :class="{ 'orders__nav-link--active': route.name === 'active-orders' }"
              text="Активные заказы"
              />
            <ButtonLink
              :to="{ name: 'revision-orders' }"
              class="orders__nav-link"
              :class="{ 'orders__nav-link--active': route.name === 'revision-orders' }"
              text="На доработку"
            />
          </nav>
        </header>
      </div>

      <main class="orders__content">
        <RouterView />
      </main>
    </template>
  </PageLayout>
</template>


<style scoped>
.orders__header {
  display: flex;
  justify-content: center;
  align-items: center;
  padding-top: 10px;
  padding-bottom: 20px;
}
.orders__header-nav {
  display: flex;
  gap: 20px;
  align-items: center;
}
</style>
