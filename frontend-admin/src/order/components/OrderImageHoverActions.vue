<template>
  <div
    class="hover-actions"
    :class="{ 'hover-actions--active': isActive }"
    @click.stop
  >
    <template v-if="!rejectMode">
      <ButtonComponent
        class="hover-actions__btn"
        variant="primary"
        type="button"
        :disabled="loading"
        @action="$emit('approve')"
        text="✓"
        title="Принять"
        aria-label="Принять"
      />
      <ButtonComponent
        v-if="status !== 'PENDING'"
        class="hover-actions__btn"
        variant="secondary"
        type="button"
        :disabled="loading"
        @action="$emit('pending')"
        text="↺"
        title="На проверку"
        aria-label="На проверку"
      />
      <ButtonComponent
        class="hover-actions__btn"
        variant="delete"
        type="button"
        :disabled="loading"
        @action="rejectMode = true"
        text="✕"
        title="Отклонить"
        aria-label="Отклонить"
      />
    </template>

    <template v-else>
      <InputComponent
        v-model="rejectReason"
        class="hover-actions__input"
        placeholder="Причина отклонения"
        :disabled="loading"
      />
      <ButtonComponent
        class="hover-actions__btn"
        variant="secondary"
        type="button"
        :disabled="loading"
        @action="cancelReject"
        text="↩"
        title="Отмена"
        aria-label="Отмена"
      />
      <ButtonComponent
        class="hover-actions__btn"
        variant="delete"
        type="button"
        :disabled="loading || !rejectReason.trim()"
        @action="submitReject"
        text="✓"
        title="Отклонить"
        aria-label="Отклонить"
      />
    </template>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import ButtonComponent from '@/components/ButtonComponent.vue'
import InputComponent from '@/components/InputComponent.vue'

const props = defineProps({
  loading: { type: Boolean, default: false },
  status: { type: String, default: '' },
})

const emit = defineEmits(['approve', 'reject', 'pending'])

const rejectMode = ref(false)
const rejectReason = ref('')

// Держим панель видимой, пока идёт запрос или открыт режим отклонения,
// даже если курсор ушёл с картинки.
const isActive = computed(() => rejectMode.value || props.loading)

function submitReject() {
  const reason = rejectReason.value.trim()
  if (!reason || props.loading) return
  emit('reject', reason)
}

function cancelReject() {
  rejectMode.value = false
  rejectReason.value = ''
}

// Когда статус фото реально изменился (успешный ответ сервера) —
// сбрасываем режим отклонения, чтобы следующее наведение было чистым.
watch(
  () => props.status,
  () => {
    rejectMode.value = false
    rejectReason.value = ''
  }
)
</script>

<style scoped>
.hover-actions {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-wrap: wrap;          /* ← разрешаем перенос на вторую строку */
  align-items: center;
  gap: 4px;
  padding: 6px;
  background: rgba(0, 0, 0, 0.65);
  border-radius: 0 0 8px 8px;

  opacity: var(--hover-actions-opacity, 0);
  pointer-events: var(--hover-actions-pointer-events, none);
  transition: opacity 0.15s ease;
}

/* Принудительно показываем, пока идёт запрос или открыт reject-режим */
.hover-actions--active {
  opacity: 1;
  pointer-events: auto;
}

/* Поле причины занимает всю ширину первой строки */
.hover-actions__input {
  flex: 1 1 100%;
  min-width: 0;
}

/* Первая кнопка после input уезжает вправо (кнопки под полем) */
.hover-actions__input + .hover-actions__btn {
  margin-left: auto;
}

/* Компактные кнопки для маленького тумбнейла */
.hover-actions__btn {
  min-width: 28px;
  min-height: 28px;
  padding: 2px 6px;
  font-size: 14px;
  line-height: 1;
  flex-shrink: 0;
}
</style>
