<template>
  <section class="order_gallery">
    <p v-if="!images.length" class="order_gallery__empty">
      Фотографий нет
    </p>

    <div v-else class="order-gallery__grid">
      <OrderImage
        v-for="img in images"
        :key="img.id"
        class="order-gallery__item"
        :image="img"
      />
    </div>
  </section>
</template>

<script setup>
import OrderImage from './OrderImage.vue';

defineProps({
  images: {
    type: Array,
    default: () => [],
  },
})
</script>

<style scoped>
.order_gallery__empty {
  color: var(--color-text-muted);
}

.order-gallery__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 12px;
}
</style>
