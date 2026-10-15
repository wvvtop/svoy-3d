<script setup>
import { ref, onMounted } from 'vue'
import { ordersApi } from '@/api/orders'
import OrderCard from '@/components/order/OrderCard.vue'

const orders = ref([])
const isLoading = ref(false)
const error = ref(null)

function onDeleted(id) {
  orders.value = orders.value.filter((o) => o.id !== id);
}

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
  <div>
    <p v-if="isLoading">Загрузка…</p>
    <p v-else-if="error" class="orders__error">{{ error }}</p>
    <p v-else-if="!orders.length" class="orders__empty">Заказов пока нет</p>

    <div v-else class="orders__list">
      <OrderCard
        v-for="order in orders"
        :key="order.id"
        :order="order"
        @deleted="onDeleted"
      />
    </div>
  </div>
</template>


<style scoped>
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
