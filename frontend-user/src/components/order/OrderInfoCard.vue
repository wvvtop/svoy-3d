<template>
  <article class="order-card">
    <div class="order-info">
      <header class="order-info__header">
        <span class="order-info__id">Заказ №{{ order.id }}</span>
        <span
          class="order-info__status"
          :class="`order-info__status--${status.variant}`"
        >
          {{ status.label }}
        </span>
      </header>

      <p class="order-info__date">
        Создан: {{ formatDate(order.created_at) }}
      </p>
    </div>
    <div class="order-info__actions">
      <ButtonComponent
        :text="actionConfig.text"
        :variant="actionConfig.variant"
        :disabled="isProcessing"
        @action="handleAction"
      />
    </div>
  </article>
</template>

<script setup>
import { computed, ref } from 'vue'
import { formatDate } from '@/utils/formatDate'
import { getStatus } from '@/utils/formatStatus'
import ButtonComponent from '../ButtonComponent.vue';
import { ordersApi } from '@/api/orders';

const emit = defineEmits(['deleted', 'restored']);
const status = computed(() => getStatus(props.order.status));
const isProcessing = ref(false);

const actionConfig = computed(() =>
  props.action === 'delete'
    ? {
        text: '✖',
        variant: 'circle-delete',
        confirmMsg: `Удалить заказ №${props.order.id}?`,
        request: () => ordersApi.delete(props.order.id),
        emitName: 'deleted',
      }
    : {
        text: '←',
        variant: 'circle-restore',
        confirmMsg: `Вернуть заказ №${props.order.id} из корзины?`,
        request: () => ordersApi.restore(props.order.id),
        emitName: 'restored',
      }
);

const handleAction = async () => {
  if (isProcessing.value) return;
  if (!confirm(actionConfig.value.confirmMsg)) return;

  isProcessing.value = true;
  try {
    await actionConfig.value.request();
    emit(actionConfig.value.emitName, props.order.id);
  } catch (err) {
    console.error(`Не удалось выполнить ${props.action}:`, err);
  } finally {
    isProcessing.value = false;
  }
};

const props = defineProps({
  order: { type: Object, required: true },
  // 'delete' — обычный список, 'restore' — корзина
  action: {
    type: String,
    default: 'delete',
    validator: (v) => ['delete', 'restore'].includes(v),
  },
});
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
}

.order-info__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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
}

/* Статусы — по семантике */
.order-info__status--success {
  background: var(--color-success-subtle);
  color: var(--color-success);
}
.order-info__status--warning {
  background: var(--color-warning-subtle);
  color: var(--color-warning);
}
.order-info__status--danger {
  background: var(--color-danger-subtle);
  color: var(--color-danger);
}
.order-info__status--primary {
  background: var(--color-primary-subtle);
  color: var(--color-primary);
}
.order-info__status--muted {
  background: var(--color-surface-hover);
  color: var(--color-text-muted);
}

.order-info__date {
  font-size: 14px;
  color: var(--color-text-muted);
  margin: 0;
}
</style>
