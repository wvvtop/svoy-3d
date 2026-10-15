<script setup>
import PageLayout from '@/layouts/PageLayout.vue';
import { ref, onMounted } from 'vue'
import { ordersApi } from '@/api/orders'
import OrderCard from '@/components/order/OrderCard.vue'
import ButtonLink from '@/components/ButtonLink.vue';

const orders = ref([])
const isLoading = ref(false)
const error = ref(null)

onMounted(async () => {
  isLoading.value = true
  error.value = null
  try {
    // 1. Получаем список заказов
    orders.value = await ordersApi.list()

    // 2. Для каждого заказа догружаем фото
    await Promise.all(
      orders.value.map(async (order) => {
        try {
          order.images = await ordersApi.getImages(order.id)
        } catch {
          order.images = []
        }
      })
    )
  } catch (err) {
    error.value = err.response?.data?.detail || 'Не удалось загрузить заказы'
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <PageLayout>
    <template #page__content_item>
      <header class="orders__header">
        <div class="orders__header-main">
          <span>Ваши заказы</span>
          <ButtonLink :to="{ name: 'Create order' }" text="Создать!"/>
        </div>
        <div class="orders__header-side">
          <ButtonLink text="Завершенные заказы"/>
          <ButtonLink text="Корзина"/>
        </div>
      </header>


      <p v-if="isLoading">Загрузка…</p>
      <p v-else-if="error" class="orders__error">{{ error }}</p>
      <p v-else-if="!orders.length" class="orders__empty">Заказов пока нет</p>

      <div v-else class="orders__list">
        <OrderCard
          v-for="order in orders"
          :key="order.id"
          :order="order"
        />
      </div>
    </template>
  </PageLayout>
</template>


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

.orders__list {
  display: grid;
  gap: 12px;
}

.orders__error {
  color: var(--color-danger);
}

.orders__empty {
  color: var(--color-text-muted);
}
</style>
