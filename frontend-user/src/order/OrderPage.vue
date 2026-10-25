<template>
  <PageLayout>
    <template #page__content_item>
      <div class="order-page">
        <aside class="order-page__chat">
          <ChatComponent :order-id="orderId" :current-user-id="currentUserId"/>
        </aside>
        <div class="order-page__form">
          <OrderForm :order-id="orderId" />
        </div>
      </div>
    </template>
  </PageLayout>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import PageLayout from '@/layouts/PageLayout.vue'
import OrderForm from '@/components/order/OrderForm.vue'
import ChatComponent from '@/components/order/ChatComponent.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const route = useRoute()
const orderId = computed(() => route.params.id)
const currentUserId = computed(() => auth.userId ?? null)
</script>

<style scoped>
.order-page {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 380px;
  gap: 24px;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  align-items: start;
}
.order-page__form {
  display: flex;
  justify-content: center;
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
