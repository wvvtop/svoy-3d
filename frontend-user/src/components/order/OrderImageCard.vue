<script setup>
defineProps({
  images: {
    type: Array,
    default: () => [],
  },
})
</script>

<template>
  <section class="order-gallery">
    <p v-if="!images.length" class="order-gallery__empty">
      Фотографий нет
    </p>

    <div v-else class="order-gallery__grid">
      <figure
        v-for="img in images"
        :key="img.id"
        class="order-gallery__item"
      >
        <a
          :href="img.compressed_url"
          target="_blank"
          rel="noopener"
          class="order-gallery__link"
        >
          <img
            :src="img.preview_url"
            :alt="`Фото ${img.position}`"
            loading="lazy"
            class="order-gallery__img"
          />
        </a>
        <figcaption class="order-gallery__caption">
          {{ img.position }}
        </figcaption>
      </figure>
    </div>
  </section>
</template>

<style scoped>
.order-gallery {
  margin-top: 16px;
}

.order-gallery__empty {
  color: var(--color-text-muted);
}

.order-gallery__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 12px;
}

.order-gallery__link {
  display: block;
}

.order-gallery__img {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  border-radius: 8px;
  display: block;
}

.order-gallery__caption {
  font-size: 12px;
  color: var(--color-text-muted);
  margin-top: 4px;
  text-align: center;
}
</style>
