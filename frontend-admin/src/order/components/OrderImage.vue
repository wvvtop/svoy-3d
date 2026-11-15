<template>
  <div class="order_image">
    <img
      :src="image.preview_url"
      :alt="`Фото ${image.position}`"
      loading="lazy"
      class="order-gallery__img"
    />
    <figcaption class="order-gallery__caption">
      {{ image.position }}
    </figcaption>
    <span
      v-if="reviewBadge"
      class="image__badge"
      :class="`image__badge--${image.review_status}`"
    >
      {{ reviewBadge }}
    </span>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  image: {
    type: Object,
    required: true,
  }
})

const REVIEW_LABELS = {
  PENDING:  'На проверке',
  APPROVED: 'Одобрено',
  REJECTED: 'Отклонено',
}

const reviewBadge = computed(() => {
  if (!props.image.review_status || !props.image.preview_url) return ''
  return REVIEW_LABELS[props.image.review_status] || ''
})
</script>

<style scoped>
.order_image {
  position: relative;
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

.image__badge {
  position: absolute;
  left: 6px;
  top: 6px;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
  color: var(--color-on-primary);
  background: var(--color-secondary);
}


.image__badge--PENDING  { background: var(--color-warning); color: var(--color-on-warning); }
.image__badge--APPROVED { background: var(--color-success); }
.image__badge--REJECTED { background: var(--color-danger); }
</style>
