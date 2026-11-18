<script setup>
import ButtonComponent from '@/components/ButtonComponent.vue';
import { computed, onMounted, ref } from 'vue';
import OrderCard from '../components/OrderCard.vue';
import { useOrdersStore } from '../stores/orders.js';


const store = useOrdersStore()

const orders = computed(() => store.revisionOrders)
const isLoading = computed(() => store.loadingRevision)

const actionError = ref(null)
const error = computed(() => store.error || actionError.value)

onMounted(() => {
  store.loadRevision().catch(() => {})
})

async function handleMoveToActive(id) {
  if (!confirm(`Отправить заказ №${id} из доработки?`)) return
  actionError.value = null
  try {
    await store.revertFromRevision(id)
  } catch (err) {
    console.error('Не удалось отправить заказ из доработки:', err)
    actionError.value = err.response?.data?.detail || 'Не удалось отправить заказ из доработки'
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
            text="↩️"
            variant="circle-restore"
            @action="handleMoveToActive(order.id)"
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

