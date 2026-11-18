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
        :loading="store.isImagePending(orderId, img.position)"
        @approve="handleApprove(img.position)"
        @reject="(reason) => handleReject(img.position, reason)"
        @pending="handlePending(img.position)"
      />
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import OrderImage from './OrderImage.vue';
import { useOrdersStore } from '../stores/orders.js';

const props = defineProps({
  orderId: { type: [String, Number], required: true },
})

const store = useOrdersStore()

const images = computed(() => store.getOrder(props.orderId)?.images || [])

async function handleApprove(position) {
  try {
    await store.approveImage(props.orderId, position)
  } catch (e) {
    console.error('Не удалось принять фото:', e)
  }
}

async function handleReject(position, reason) {
  try {
    await store.rejectImage(props.orderId, position, reason)
  } catch (e) {
    console.error('Не удалось отклонить фото:', e)
  }
}

async function handlePending(position) {
  try {
    await store.pendingImage(props.orderId, position)
  } catch (e) {
    console.error('Не удалось отправить фото на проверку:', e)
  }
}
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
