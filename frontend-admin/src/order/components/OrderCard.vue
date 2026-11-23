<script setup>
import SpacerComponent from '@/components/SpacerComponent.vue';
import OrderInfoCard from './OrderInfoCard.vue';
import OrderPhotoGrid from './OrderPhotoGrid.vue';

defineProps({
  order: { type: Object, required: true },
  clickable: { type: Boolean, default: false },
});
</script>

<template>
  <article class="order-card">
    <OrderInfoCard :order="order" :clickable="clickable">
      <template v-if="$slots.actions" #actions>
        <slot name="actions"></slot>
      </template>
    </OrderInfoCard>

    <SpacerComponent size="md" />

    <OrderPhotoGrid :orderId="order.id" />
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
