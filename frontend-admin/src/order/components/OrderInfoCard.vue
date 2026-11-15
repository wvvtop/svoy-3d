<template>
  <article class="order-card">
    <component
      :is="clickable ? 'RouterLink' : 'div'"
      :to="clickable ? { name: 'Order', params: { id: order.id } } : undefined"
      class="order-info"
      :class="{ 'order-info--clickable': clickable }"
    >
      <div class="order-info__content">
        <!-- Левая колонка: номер + статус в одной строке, под ними дата -->
        <div class="order-info__main">
          <div class="order-info__header">
            <span class="order-info__id">Заказ №{{ order.id }}</span>
            <span
              class="order-info__status"
              :class="`order-info__status--${status.variant}`"
            >
              {{ status.label }}
            </span>
          </div>

          <p class="order-info__date">
            Создан: {{ formatDate(order.created_at) }}
          </p>
        </div>

        <!-- Правая колонка: пожелания клиента -->
        <p v-if="order.requests" class="order-info__requests">
          {{ order.requests.requests }}
        </p>
      </div>
    </component>

    <div v-if="$slots.actions" class="order-info__actions" @click.stop>
      <slot name="actions" :order="order"></slot>
    </div>
  </article>
</template>

<script setup>
import { formatDate } from '@/utils/formatDate';
import { getStatus } from '@/utils/formatStatus';
import { computed } from 'vue';

const props = defineProps({
  order: { type: Object, required: true },
  clickable: { type: Boolean, default: false },
});

const status = computed(() => getStatus(props.order.status));
</script>

<style scoped>
.order-card {
  display: flex;
}

.order-info {
  background: var(--color-surface);
  width: 100%;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;

  /* Сброс стилей ссылки */
  text-decoration: none;
  color: inherit;
}

.order-info--clickable {
  cursor: pointer;
}

/* Две колонки: слева — номер/статус/дата, справа — текст requests */
.order-info__content {
  display: flex;
  justify-content: flex-start;
  align-items: flex-start;
  gap: 16px;
}

.order-info__main {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex-shrink: 0;
}

/* Номер заказа и статус в одной строке, рядом */
.order-info__header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.order-info__id {
  font-weight: 600;
  color: var(--color-text);
}

.order-info__status {
  font-size: 12px;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 999px;
  flex-shrink: 0;
}

.order-info__date {
  font-size: 14px;
  color: var(--color-text-muted);
  margin: 0;
}

/* Пожелания клиента справа */
.order-info__requests {
  margin: 0;
  flex: 1;                        /* занимает оставшееся место */
  min-width: 0;
  color: var(--color-text);
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  font-size: 14px;
  text-align: left;
}

.order-info__status--success { background: var(--color-success-subtle); color: var(--color-success); }
.order-info__status--warning { background: var(--color-warning-subtle); color: var(--color-warning); }
.order-info__status--danger  { background: var(--color-danger-subtle);  color: var(--color-danger); }
.order-info__status--primary { background: var(--color-primary-subtle); color: var(--color-primary); }
.order-info__status--muted   { background: var(--color-surface-hover);  color: var(--color-text-muted); }
</style>
