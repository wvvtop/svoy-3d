<script setup>
import ButtonComponent from '@/components/ButtonComponent.vue';
import { computed, onMounted, ref } from 'vue';
import OrderCard from '../components/OrderCard.vue';
import { useOrdersStore } from '../stores/orders.js';


const store = useOrdersStore()

const orders = computed(() => store.activeOrders)
const isLoading = computed(() => store.loadingActive)

const actionError = ref(null)
const error = computed(() => store.error || actionError.value)

onMounted(() => {
  store.loadActive().catch(() => {})
})

async function handleMoveToRevision(id) {
  if (!confirm(`Отправить заказ на доработку №${id}?`)) return
  actionError.value = null
  try {
    await store.sendToRevision(id)
  } catch (err) {
    console.error('Не удалось отправить заказ на доработку:', err)
    actionError.value = err.response?.data?.detail || 'Не удалось отправить заказ на доработку'
  }
}
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
        clickable
      >
        <template #actions>
          <ButtonComponent
            text="🛠️"
            variant="circle-delete"
            @action="handleMoveToRevision(order.id)"
          />
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
