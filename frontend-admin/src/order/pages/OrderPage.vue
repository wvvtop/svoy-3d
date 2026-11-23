<script setup>
import PageLayout from '@/layouts/PageLayout.vue';
import { computed, onMounted, ref, watch } from 'vue';
import { useOrdersStore } from '../stores/orders';
import { useRoute } from 'vue-router';
import OrderInfoCard from '../components/OrderInfoCard.vue';
import ButtonComponent from '@/components/ButtonComponent.vue';
import SpacerComponent from '@/components/SpacerComponent.vue';
import OrderPhotoGrid from '../components/OrderPhotoGrid.vue';
import ChatComponent from '../components/ChatComponent.vue';
import { useAuthStore } from '@/stores/auth';

const auth = useAuthStore()

const currentUserId = computed(() => auth.userId ?? null)

const REVISION_STATUS = 'REVISION'

const route = useRoute()
const store = useOrdersStore()

const orderId = computed(() => route.params.id)
const order = computed(() => store.getOrder(orderId.value))
const nativeId = computed(() => order.value?.id ?? null)

const isRevision = computed(() => order.value?.status === REVISION_STATUS)

const actionPending = computed(() =>
  nativeId.value != null && store.isOrderPending(nativeId.value)
)

const error = ref(null)

async function load() {
  error.value = null
  try {
    await store.loadOrder(orderId.value)
  } catch (e) {
    error.value = e.response?.data?.detail || e.message || 'Не удалось загрузить заказ'
  }
}

onMounted(load)
watch(orderId, load)

async function onMoveToRevision() {
  if (nativeId.value == null) return
  if (!confirm(`Отправить заказ №${nativeId.value} на доработку?`)) return
  error.value = null
  try {
    await store.sendToRevision(nativeId.value)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Не удалось отправить заказ на доработку'
  }
}

async function onRevert() {
  if (nativeId.value == null) return
  if (!confirm(`Вернуть заказ №${orderId.value} из доработки?`)) return
  error.value = null
  try {
    await store.revertFromRevision(nativeId.value)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Не удалось вернуть заказ из доработки'
  }
}
</script>

<template>
  <PageLayout>
    <template #page__content_item>
      <div>
        <p v-if="error" class="order__error">{{ error }}</p>
        <p v-else-if="!order" class="order__loading">Загрузка…</p>

        <article v-else class="order">
          <OrderInfoCard :order="order" :clickable="false">
            <template #actions>
              <ButtonComponent
                v-if="!isRevision"
                text="🛠️"
                variant="circle-delete"
                :disabled="actionPending"
                @action="onMoveToRevision"
              />
              <ButtonComponent
                v-else
                text="↩️"
                variant="circle-restore"
                :disabled="actionPending"
                @action="onRevert"
              />
            </template>
          </OrderInfoCard>

          <SpacerComponent size="md" />

          <OrderPhotoGrid :orderId="order.id" />

          <SpacerComponent size="md" />
          <div class="order-page__chat">
            <ChatComponent :orderId="orderId" :currentUserId="currentUserId"/>
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
