<script setup>
import { computed, onMounted, ref } from 'vue'
import OrdersPagination from '../components/OrdersPagination.vue'
import OrderCard from '../components/OrderCard.vue'
import OrderStatusAction from '../components/OrderStatusAction.vue'
import { ORDER_STATUS, useOrdersStore } from '../stores/orders.js'

const store = useOrdersStore()

const orders = computed(() => store.items)
const isLoading = computed(() => store.listLoading)

const actionError = ref(null)
const error = computed(() => store.listError)

onMounted(() => {
  store.loadRevision().catch(() => {})
})
</script>

<template>
  <div>
    <p v-if="isLoading">Загрузка…</p>
    <p v-if="actionError" class="orders__error">{{ actionError }}</p>
    <p v-if="error" class="orders__error">{{ error }}</p>
    <p v-else-if="!isLoading && !orders.length" class="orders__empty">Заказов пока нет</p>

    <div v-if="!isLoading && orders.length" class="orders__list">
      <OrderCard
        v-for="order in orders"
        :key="order.id"
        :order="order"
        :class="{ 'orders__item--shifted': order.status !== ORDER_STATUS.REVISION }"
        clickable
      >
        <template #actions>
          <OrderStatusAction :order="order" @error="actionError = $event" />
        </template>
      </OrderCard>
    </div>
    <OrdersPagination />
  </div>
</template>

<style scoped>
.orders__list {
  display: grid;
  gap: 12px;
}

.orders__item--shifted {
  opacity: 0.7;
}

.orders__error {
  color: var(--color-danger);
}

.orders__empty {
  color: var(--color-text-muted);
}
</style>
