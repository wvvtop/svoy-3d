<template>
  <Teleport to="body">
    <Transition name="viewer-fade">
      <div
        v-if="modelValue"
        class="image-viewer"
        role="dialog"
        aria-modal="true"
        @click="close"
      >
        <div class="image-viewer__frame" @click.stop>
          <img
            v-if="src"
            :src="src"
            :alt="alt"
            class="image-viewer__img"
          />
          <ButtonComponent
            class="image-viewer__close"
            variant="circle-close"
            type="button"
            text="✕"
            aria-label="Закрыть"
            @action="close"
          />

          <div class="image-viewer__actions">
            <template v-if="!rejectMode">
              <ButtonComponent
                variant="primary"
                type="button"
                :disabled="loading"
                @action="onApprove"
                text="Принять"
              />
              <ButtonComponent
                v-if="status !== 'PENDING'"
                variant="secondary"
                type="button"
                :disabled="loading"
                @action="onPending"
                text="На проверку"
              />
              <ButtonComponent
                variant="delete"
                type="button"
                :disabled="loading"
                @action="rejectMode = true"
                text="Отклонить"
              />
            </template>

            <template v-else>
              <InputComponent
                v-model="rejectReason"
                class="image-viewer__input"
                placeholder="Причина отклонения"
                :disabled="loading"
              />
              <div class="image-viewer__reject-actions">
                <ButtonComponent
                  variant="secondary"
                  type="button"
                  :disabled="loading"
                  @action="cancelReject"
                  text="Отмена"
                />
                <ButtonComponent
                  variant="delete"
                  type="button"
                  :disabled="loading"
                  @action="onReject"
                  text="Отклонить"
                />
              </div>
            </template>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, watch, onBeforeUnmount } from 'vue'
import InputComponent from '@/components/InputComponent.vue'
import ButtonComponent from '@/components/ButtonComponent.vue';

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  src: { type: String, default: '' },
  alt: { type: String, default: 'Изображение' },
  loading: { type: Boolean, default: false },
  status: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue', 'approve', 'reject', 'pending'])

const rejectMode = ref(false)
const rejectReason = ref('')

const close = () => emit('update:modelValue', false)

const onApprove = () => emit('approve')
const onPending = () => emit('pending')

const onReject = () => {
  const reason = rejectReason.value.trim()
  if (props.loading) return
  emit('reject', reason)
}

const cancelReject = () => {
  rejectMode.value = false
  rejectReason.value = ''
}

const onKeydown = (e) => {
  if (e.key === 'Escape') close()
}

watch(
  () => props.modelValue,
  (isOpen) => {
    if (isOpen) {
      document.addEventListener('keydown', onKeydown)
      document.body.style.overflow = 'hidden'
    } else {
      document.removeEventListener('keydown', onKeydown)
      document.body.style.overflow = ''
      rejectMode.value = false
      rejectReason.value = ''
    }
  },
  { immediate: true }
)

onBeforeUnmount(() => {
  document.removeEventListener('keydown', onKeydown)
  document.body.style.overflow = ''
})
</script>

<style scoped>
.image-viewer {
  position: fixed;
  inset: 0;
  z-index: 1000;
  background: var(--color-overlay);
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-viewer__frame {
  position: relative;
  display: flex;
  flex-direction: column;
  max-width: 75vw;
  max-height: 75vh;
}

.image-viewer__img {
  display: block;
  max-width: 75vw;
  max-height: calc(75vh - 60px);
  object-fit: contain;
  border-radius: 8px;
}

.image-viewer__close {
  position: absolute;
  top: 10px;
  right: 10px;
}

.image-viewer__actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding-top: 12px;
}

.image-viewer__input {
  flex: 1;
  min-width: 0;
}

.image-viewer__reject-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.viewer-fade-enter-active,
.viewer-fade-leave-active {
  transition: opacity 0.2s ease;
}

.viewer-fade-enter-from,
.viewer-fade-leave-to {
  opacity: 0;
}
</style>
