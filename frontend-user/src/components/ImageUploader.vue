<template>
  <div class="uploader-wrapper">
    <div class="uploader" :class="rootClasses">
      <template v-if="hasPreview">
        <img :src="previewSrc" :alt="alt" class="uploader__img" />

        <span
          v-if="reviewBadge"
          class="uploader__badge"
          :class="`uploader__badge--${reviewStatus}`"
        >
          {{ reviewBadge }}
        </span>

        <button
          v-if="!disabled"
          type="button"
          class="uploader__remove"
          aria-label="Удалить изображение"
          @click.stop="removeImage"
        >
          ✕
        </button>
      </template>

      <template v-else>
        <input
          ref="fileInput"
          type="file"
          class="uploader__input"
          :accept="accept"
          :disabled="disabled"
          @change="onFileInput"
        />
        <button
          type="button"
          class="uploader__drop"
          :disabled="disabled"
          @click="openFileDialog"
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          @drop.prevent="onDrop"
        >
          <svg class="uploader__icon" viewBox="0 0 24 24" fill="none"
               stroke="currentColor" stroke-width="2">
            <path d="M12 5v14M5 12h14" />
          </svg>
          <span class="uploader__text">Перетащите фото</span>
          <span class="uploader__hint">или нажмите для выбора</span>
        </button>
      </template>
    </div>

    <p v-if="problemText" class="uploader__error">{{ problemText }}</p>
  </div>
</template>

<script setup>
import { ref, computed, onBeforeUnmount, watch } from 'vue'

const props = defineProps({
  modelValue:     { type: [File, null], default: null },
  previewUrl:     { type: String, default: '' },   // новое
  initialPreview: { type: String, default: '' },   // backward-compat
  reviewStatus:   { type: String, default: '' },   // 'pending'|'approved'|'rejected'|''
  reviewError:    { type: String, default: '' },
  uploadError:    { type: String, default: '' },
  disabled:       { type: Boolean, default: false },
  accept:         { type: String, default: 'image/*' },
  maxSizeMb:      { type: Number, default: 15 },
  alt:            { type: String, default: 'Изображение' },
})

const emit = defineEmits(['update:modelValue', 'change', 'remove'])

const fileInput = ref(null)
const isDragging = ref(false)
const error = ref('')
const localPreview = ref('')

const externalPreview = computed(() => props.previewUrl || props.initialPreview)
const previewSrc = computed(() => localPreview.value || externalPreview.value)
const hasPreview = computed(() => Boolean(previewSrc.value))

const REVIEW_LABELS = {
  pending:  'На проверке',
  approved: 'Одобрено',
  rejected: 'Отклонено',
}
const reviewBadge = computed(() => {
  if (!props.reviewStatus || !hasPreview.value) return ''
  return REVIEW_LABELS[props.reviewStatus] || ''
})

const problemText = computed(() =>
  props.uploadError || props.reviewError || error.value || ''
)

const hasError = computed(
  () =>
    Boolean(problemText.value) ||
    props.reviewStatus === 'rejected'
)

const rootClasses = computed(() => ({
  'uploader--dragging':  isDragging.value,
  'uploader--has-image': hasPreview.value,
  'uploader--disabled':  props.disabled,
  'uploader--error':     hasError.value,
}))

watch(
  () => props.modelValue,
  (file) => {
    if (localPreview.value) {
      URL.revokeObjectURL(localPreview.value)
      localPreview.value = ''
    }
    if (file instanceof File) {
      localPreview.value = URL.createObjectURL(file)
    }
  },
  { immediate: true }
)

onBeforeUnmount(() => {
  if (localPreview.value) URL.revokeObjectURL(localPreview.value)
})

function openFileDialog() {
  if (props.disabled) return
  fileInput.value?.click()
}

function onFileInput(event) {
  const file = event.target.files?.[0]
  if (file) handleFile(file)
  event.target.value = ''
}

function onDrop(event) {
  isDragging.value = false
  if (props.disabled) return
  const file = event.dataTransfer?.files?.[0]
  if (file) handleFile(file)
}

function handleFile(file) {
  error.value = ''
  if (!file.type.startsWith('image/')) {
    error.value = 'Можно загрузить только изображение'
    return
  }
  const maxBytes = props.maxSizeMb * 1024 * 1024
  if (file.size > maxBytes) {
    error.value = `Файл больше ${props.maxSizeMb} МБ`
    return
  }
  emit('update:modelValue', file)
  emit('change', file)
}

function removeImage() {
  if (!confirm('Удалить фотографию?')) return
  error.value = ''
  emit('update:modelValue', null)
  emit('change', null)
  emit('remove')
}
</script>

<style scoped>
.uploader-wrapper {
  display: flex;
  flex-direction: column;
  gap: 6px;
  width: 100%;
}

.uploader {
  position: relative;
  width: 100%;
  aspect-ratio: 1 / 1;
  border-radius: 10px;
  overflow: hidden;
  background: var(--color-surface);
  border: 1px dashed var(--color-border-strong);
  transition: border-color 0.2s, background 0.2s;
}

.uploader--dragging {
  border-color: var(--color-primary);
  background: var(--color-primary-subtle);
}

.uploader--has-image {
  border-style: solid;
  border-color: var(--color-border);
}

.uploader--error {
  border-color: var(--color-danger);
  border-style: solid;
  box-shadow: 0 0 0 1px var(--color-danger) inset;
}

.uploader--disabled {
  opacity: 0.6;
  pointer-events: none;
}

.uploader__img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.uploader__remove {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 50%;
  background: rgb(15 23 42 / 0.7);
  color: var(--color-on-primary);
  font-size: 14px;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s, transform 0.15s;
}
.uploader__remove:hover {
  background: var(--color-danger);
  transform: scale(1.08);
}

.uploader__badge {
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
.uploader__badge--pending  { background: var(--color-warning); color: var(--color-on-warning); }
.uploader__badge--approved { background: var(--color-success); }
.uploader__badge--rejected { background: var(--color-danger); }

.uploader__input { display: none; }

.uploader__drop {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  border: none;
  background: transparent;
  cursor: pointer;
  color: var(--color-text-muted);
  padding: 12px;
  font-family: inherit;
}
.uploader__drop:hover { color: var(--color-text); }

.uploader__icon { width: 32px; height: 32px; opacity: 0.7; }
.uploader__text { font-size: 14px; font-weight: 500; color: var(--color-text); }
.uploader__hint { font-size: 12px; color: var(--color-text-muted); }

.uploader__error {
  margin: 0;
  font-size: 13px;
  color: var(--color-danger);
}
</style>
