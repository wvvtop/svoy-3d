<script setup>
import { ref, onMounted } from 'vue'
import { ordersApi } from '@/api/orders'
import OrderCard from '@/components/order/OrderCard.vue'
import ButtonComponent from '@/components/ButtonComponent.vue'

const deleted_orders = ref([])
const isLoading = ref(false)
const error = ref(null)
const actionError = ref(null)
const processingIds = ref(new Set())

async function handleRestore(id) {
  if (!confirm(`Вернуть заказ №${id} из корзины?`)) return
  if (processingIds.value.has(id)) return

  processingIds.value.add(id)
  actionError.value = null
  try {
    await ordersApi.restore(id)                              // ждём ответ
    deleted_orders.value = deleted_orders.value.filter((o) => o.id !== id)
  } catch (err) {
    actionError.value = err.response?.data?.detail || 'Не удалось восстановить заказ'
  } finally {
    processingIds.value.delete(id)
  }
}

onMounted(async () => {
  isLoading.value = true
  error.value = null
  try {
    deleted_orders.value = await ordersApi.getDeleted()

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
</script>

<template>
  <div>
    <p v-if="isLoading">Загрузка…</p>
    <p v-else-if="error" class="orders__error">{{ error }}</p>
    <p v-else-if="!deleted_orders.length" class="orders__empty">
      Удалённых заказов пока нет
    </p>

    <div v-else class="orders__list">
      <p v-if="actionError" class="orders__error">{{ actionError }}</p>

      <OrderCard
        v-for="order in deleted_orders"
        :key="order.id"
        :order="order">
        <template #actions>
          <ButtonComponent text="←" variant="circle-restore"
            @action="handleRestore(order.id)" />
        </template>
      </OrderCard>
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
