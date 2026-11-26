<script setup>
import { computed } from 'vue'
import ButtonComponent from '@/components/ButtonComponent.vue'
import { ORDER_STATUS, useOrdersStore } from '../stores/orders.js'

const props = defineProps({
  order: { type: Object, required: true },
})

const emit = defineEmits(['error'])

const store = useOrdersStore()

const isRevision = computed(() => props.order.status === ORDER_STATUS.REVISION)
const pending = computed(() => store.isOrderPending(props.order.id))

async function handleToggle() {
  const id = props.order.id
  const confirmText = isRevision.value
    ? `Вернуть заказ №${id} из доработки?`
    : `Отправить заказ №${id} на доработку?`

  if (!confirm(confirmText)) return

  emit('error', null)
  try {
    if (isRevision.value) {
      await store.revertFromRevision(id)
    } else {
      await store.sendToRevision(id)
    }
  } catch (err) {
    const fallbackMsg = isRevision.value
      ? 'Не удалось вернуть заказ из доработки'
      : 'Не удалось отправить заказ на доработку'
    emit('error', err.response?.data?.detail || fallbackMsg)
  }
}
</script>

<template>
  <ButtonComponent
    v-if="!isRevision"
    text="🛠️"
    title="На доработку"
    variant="circle-delete"
    :disabled="pending"
    @action="handleToggle"
  />
  <ButtonComponent
    v-else
    text="↩️"
    title="Вернуть из доработки"
    variant="circle-restore"
    :disabled="pending"
    @action="handleToggle"
  />
</template>
