<script setup>
import OrderImageCard from './OrderImageCard.vue';
import OrderInfoCard from './OrderInfoCard.vue';

defineProps({
  order: { type: Object, required: true },
  action: {
    type: String,
    default: 'delete',
    validator: (v) => ['delete', 'restore'].includes(v),
  },
});

const emit = defineEmits(['deleted', 'restored']);
</script>

<template>
  <article class="order-card">
    <OrderInfoCard :order="order"
      :action="action"
      @deleted="emit('deleted', $event)"
      @restored="emit('restored', $event)" />
    <OrderImageCard :images="order.images" compact />
  </article>
</template>

<style scoped>
.order-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  padding: 16px;
  gap: 16px;
  transition: border-color 0.2s, background 0.2s;
}

.order-card:hover {
  border-color: var(--color-border-strong);
}
</style>
