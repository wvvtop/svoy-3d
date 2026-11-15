<script setup>
import ButtonComponent from '@/components/ButtonComponent.vue';
import { onMounted, ref } from 'vue';
import OrderCard from '../components/OrderCard.vue';
import { ordersApi } from '@/api/order.js';

const orders = ref([])
const isLoading = ref(false)
const error = ref(null)

const processingIds = ref(new Set())

async function handleMoveToActive(id) {
  if (!confirm(`Отправить заказ №${id} из доработки?`)) return
  if (processingIds.value.has(id)) return

  processingIds.value.add(id)
  try {
    await ordersApi.revertFromRevision(id)                              // ждём ответ
    orders.value = orders.value.filter((o) => o.id !== id)  // убираем ТОЛЬКО после успеха
  } catch (err) {
    console.error('Не удалось отправить заказ из доработки:', err)
    error.value = err.response?.data?.detail || 'Не удалось отправить заказ из доработки:'
  } finally {
    processingIds.value.delete(id)
  }
}

onMounted(async () => {
  isLoading.value = true
  error.value = null
  try {
    // 1. Получаем список заказов
    orders.value = await ordersApi.getRevision()

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
    // 3. Для каждого заказа догружаем запросы от пользователя
    await Promise.all(
      orders.value.map(async (order) =>{
        try {
          order.requests = await ordersApi.getRequests(order.id)
        } catch {
          order.requests = ''
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
        clickable>
        <template #actions>
          <ButtonComponent text="↩️" variant="circle-restore"
            @action="handleMoveToActive(order.id)" />

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
