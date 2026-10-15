<script setup>
import { ref, onMounted } from 'vue'
import { ordersApi } from '@/api/orders'
import OrderCard from '@/components/order/OrderCard.vue'

const deleted_orders = ref([])
const isLoading = ref(false)
const error = ref(null)

onMounted(async () => {
  isLoading.value = true
  error.value = null
  try {
    // 1. Получаем список заказов
    deleted_orders.value = await ordersApi.getDeleted()

    // 2. Для каждого заказа догружаем фото
    await Promise.all(
      deleted_orders.value.map(async (order) => {
        try {
          order.images = await ordersApi.getDeletedImages(order.id)
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

function onRestored(id) {
  deleted_orders.value = deleted_orders.value.filter((o) => o.id !== id);
}
</script>

<template>
  <div>
    <p v-if="isLoading">Загрузка…</p>
    <p v-else-if="error" class="orders__error">{{ error }}</p>
    <p v-else-if="!deleted_orders.length" class="orders__empty">Удаленных заказов пока нет</p>

    <div v-else class="orders__list">
      <OrderCard
        v-for="order in deleted_orders"
        :key="order.id"
        :order="order"
        action="restore"
        @restored="onRestored"
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

