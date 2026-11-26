<script setup>
import ButtonComponent from '@/components/ButtonComponent.vue'

import { useOrdersStore } from '../stores/orders.js'

const store = useOrdersStore()
</script>

<template>
  <nav
    class="orders-pagination"
    aria-label="Пагинация заказов"
  >
    <ButtonComponent
      text="Назад"
      variant="secondary"
      size="sm"
      :disabled="store.listLoading || store.page === 1"
      @action="store.previousPage()"
    />

    <span
      class="orders-pagination__page"
      aria-live="polite"
    >
      Страница {{ store.page }}
    </span>

    <ButtonComponent
      text="Далее"
      variant="secondary"
      size="sm"
      :disabled="store.listLoading || !store.hasMore"
      @action="store.nextPage()"
    />

    <ButtonComponent
      text="Обновить"
      variant="secondary"
      size="sm"
      :disabled="store.listLoading"
      @action="store.refreshPage()"
    />
  </nav>
</template>

<style scoped>
.orders-pagination {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 20px 0;
  color: var(--color-text);
}

.orders-pagination__page {
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
}
</style>
