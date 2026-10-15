<template>
  <PageLayout>
    <template #page__content_item>
      <div class="orders">
        <header class="orders__header">
          <div class="orders__header-main">
            <!-- На активных заказах — заголовок + кнопка «Создать!» -->
              <template v-if="isOrdersRoot">
                <h1 class="orders__title">Ваши заказы</h1>
                <ButtonLink
                  :to="{ name: 'create-order' }"
                  text="Создать!"
                />
              </template>

              <!-- На дочерних страницах — «Вернуться назад» -->
              <ButtonLink
                v-else
                :to="{ name: 'orders' }"
                class="orders__back"
                text="← Вернуться к заказам"
              />
          </div>

          <!-- ПРАВАЯ ЧАСТЬ: всегда ссылки, активная подсвечена -->
          <nav class="orders__header-side">
            <ButtonLink
              :to="{ name: 'completed-orders' }"
              class="orders__nav-link"
              text="Завершённые заказы"
              />
            <ButtonLink
              :to="{ name: 'orders-bin' }"
              class="orders__nav-link"
              text="Корзина"
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

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import PageLayout from './PageLayout.vue';
import ButtonLink from '@/components/ButtonLink.vue';

const route = useRoute();

const isOrdersRoot = computed(() => route.name === 'orders');
</script>

<style scoped>
.orders__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-left: 25px;
  padding-top: 10px;
  padding-bottom: 20px;
}
.orders__header-main {
  display: flex;
  gap: 20px;
  align-items: center;
}

.orders__header-side {
  display: flex;
  gap: 20px;
  align-items: center;
}
</style>
