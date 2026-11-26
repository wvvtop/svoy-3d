<script setup>
import PageLayout from '@/layouts/PageLayout.vue'
import { computed, onMounted, ref, watch } from 'vue'
import { useOrdersStore } from '../stores/orders'
import { useRoute } from 'vue-router'
import OrderInfoCard from '../components/OrderInfoCard.vue'
import OrderStatusAction from '../components/OrderStatusAction.vue'
import SpacerComponent from '@/components/SpacerComponent.vue'
import OrderPhotoGrid from '../components/OrderPhotoGrid.vue'
import ChatComponent from '../components/ChatComponent.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const currentUserId = computed(() => auth.userId ?? null)

const route = useRoute()
const store = useOrdersStore()

const orderId = computed(() => route.params.id)
const order = computed(() => store.currentOrder)

const loadError = ref(null)
const actionError = ref(null)
const error = computed(() => loadError.value || actionError.value)

async function load() {
  loadError.value = null
  actionError.value = null
  try {
    await store.loadOrder(orderId.value)
  } catch (e) {
    loadError.value = e.response?.data?.detail || e.message || 'Не удалось загрузить заказ'
  }
}

onMounted(load)
watch(orderId, load)
</script>

<template>
  <PageLayout>
    <template #page__content_item>
      <div>
        <p v-if="error" class="order__error">{{ error }}</p>
        <p v-if="store.loading && !order" class="order__loading">Загрузка…</p>

        <article v-else-if="order" class="order">
          <OrderInfoCard :order="order" :clickable="false">
            <template #actions>
              <OrderStatusAction :order="order" @error="actionError = $event" />
            </template>
          </OrderInfoCard>

          <SpacerComponent size="md" />

          <OrderPhotoGrid :orderId="order.id" />

          <SpacerComponent size="md" />
          <div class="order-page__chat">
            <ChatComponent :orderId="orderId" :currentUserId="currentUserId" />
          </div>
        </article>
      </div>
    </template>
  </PageLayout>
</template>

<style scoped>
.order__error {
  color: var(--color-danger);
}
.order__loading {
  color: var(--color-text-muted);
}

.order-page__chat {
  position: sticky;
  top: 24px;
  height: calc(100vh - 120px);
}
@media (max-width: 900px) {
  .order-page {
    grid-template-columns: 1fr;
  }
  .order-page__chat {
    position: static;
    height: 500px;
  }
}
</style>
