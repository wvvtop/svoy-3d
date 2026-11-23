<template>
  <div class="order_image">
    <img
      :src="image.preview_url"
      :alt="`Фото ${image.position}`"
      loading="lazy"
      class="order-gallery__img"
      :class="{ 'order-gallery__img--clickable': hasFullImage }"
      @click="openViewer"
    />
    <div class="order-gallery__caption">
      {{ image.position }}
    </div>
    <OrderImageHoverActions
      :loading="loading"
      :status="image.review_status"
      @approve="onApprove"
      @pending="onPending"
      @reject="onReject"
    />
    <span
      v-if="reviewBadge"
      class="image__badge"
      :class="`image__badge--${image.review_status}`"
    >
      {{ reviewBadge }}
    </span>
    <ImageViewer
      v-model="viewerOpen"
      :src="viewerSrc"
      :alt="`Фото ${image.position}`"
      :loading="loading"
      :status="image.review_status"
      @approve="onApprove"
      @reject="onReject"
      @pending="onPending"
    />
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import ImageViewer from './ImageViewer.vue';
import OrderImageHoverActions from './OrderImageHoverActions.vue';

const props = defineProps({
  image: { type: Object, required: true },
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['approve', 'reject', 'pending'])

const viewerOpen = ref(false)
const viewerSrc = ref('')

const hasFullImage = computed(() =>
  !!(props.image.compressed_url || props.image.preview_url)
)

const openViewer = () => {
  if (!hasFullImage.value) return
  viewerSrc.value = props.image.compressed_url || props.image.preview_url
  viewerOpen.value = true
}

const onApprove = () => emit('approve')
const onReject = (reason) => emit('reject', reason)
const onPending = () => emit('pending')

// Закрываем viewer, когда действие реально изменило статус
// (т.е. store успешно обновил review_status после ответа API).
watch(
  () => props.image.review_status,
  () => {
    if (viewerOpen.value) viewerOpen.value = false
  }
)

const REVIEW_LABELS = {
  PENDING: 'На проверке',
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

.order-gallery__img--clickable {
  cursor: zoom-in;
}

.order_image {
  position: relative;
  display: block;

  /* Управление видимостью hover-панели. Переменные каскадом уходят
     в дочерний OrderImageHoverActions.vue. */
  --hover-actions-opacity: 0;
  --hover-actions-pointer-events: none;
}

.order_image:hover,
.order_image:focus-within {
  --hover-actions-opacity: 1;
  --hover-actions-pointer-events: auto;
}

.image__badge--PENDING  { background: var(--color-warning); color: var(--color-on-warning); }
.image__badge--APPROVED { background: var(--color-success); }
.image__badge--REJECTED { background: var(--color-danger); }
</style>
