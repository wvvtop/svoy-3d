<template>
  <div class="uploader" :class="{ 'uploader--dragging': isDragging,
  'uploader--has-image': hasImage }">
    <!-- Есть изображение — показываем превью + крестик -->
    <template v-if="hasImage">
      <img :src="previewSrc" :alt="alt" class="uploader__img" />

      <button
        type="button"
        class="uploader__remove"
        aria-label="Удалить изображение"
        @click.stop="removeImage"
      >
        ✕
      </button>
    </template>

    <!-- Нет изображения — зона загрузки -->
    <template v-else>
      <input
        ref="fileInput"
        type="file"
        class="uploader__input"
        :accept="accept"
        @change="onFileInput"
      />

      <button
        type="button"
        class="uploader__drop"
        @click="openFileDialog"
        @dragover.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
        @drop.prevent="onDrop"
      >
        <svg class="uploader__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 5v14M5 12h14" />
        </svg>
        <span class="uploader__text">Перетащите фото</span>
        <span class="uploader__hint">или нажмите для выбора</span>
      </button>
    </template>

    <p v-if="error" class="uploader__error">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref, computed, onBeforeUnmount, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: [File, null],
    default: null,
  },
  // URL уже загруженного изображения (например, из БД)
  initialPreview: {
    type: String,
    default: '',
  },
  accept: {
    type: String,
    default: 'image/*',
  },
  maxSizeMb: {
    type: Number,
    default: 15,
  },
  alt: {
    type: String,
    default: 'Изображение',
  },
})

const emit = defineEmits(['update:modelValue', 'change'])

const fileInput = ref(null)
const isDragging = ref(false)
const error = ref('')
const localPreview = ref('')

// Если задан modelValue или initialPreview — показываем изображение
const previewSrc = computed(() => localPreview.value || props.initialPreview)
const hasImage = computed(() => Boolean(previewSrc.value))

// Создаём/освобождаем blob URL при изменении файла
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
  if (localPreview.value) {
    URL.revokeObjectURL(localPreview.value)
  }
})

function openFileDialog() {
  fileInput.value?.click()
}

function onFileInput(event) {
  const file = event.target.files?.[0]
  if (file) handleFile(file)
  // сбрасываем input, чтобы можно было выбрать тот же файл повторно
  event.target.value = ''
}

function onDrop(event) {
  isDragging.value = false
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
  error.value = ''
  emit('update:modelValue', null)
  emit('change', null)
}
</script>

<style scoped>
.uploader {
  position: relative;
  width: 100%;
  aspect-ratio: 1 / 1;         /* по умолчанию — квадрат */
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

/* ---- превью ---- */
.uploader__img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

/* ---- крестик удаления ---- */
.uploader__remove {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 50%;
  background: rgb(15 23 42 / 0.7);
  color: white;
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

/* ---- зона загрузки ---- */
.uploader__input {
  display: none;
}

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

.uploader__drop:hover {
  color: var(--color-text);
}

.uploader__icon {
  width: 32px;
  height: 32px;
  opacity: 0.7;
}

.uploader__text {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text);
}

.uploader__hint {
  font-size: 12px;
  color: var(--color-text-muted);
}

/* ---- ошибка ---- */
.uploader__error {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  margin: 0;
  padding: 4px 8px;
  font-size: 12px;
  background: var(--color-danger);
  color: var(--color-on-danger);
  text-align: center;
}
</style>
