<template>
  <form class="order-form" @submit.prevent="handleSubmit">
    <h1>{{ isEdit ? `Заказ #${orderId}` : 'Создать заказ' }}</h1>
    <SpacerComponent />
    <p class="order-form__description">
      Вам необходимо загрузить фотографии с разных ракурсов, которые указаны в форме.
      Постарайтесь сделать фотографии перпендикулярно объекту.
    </p>
    <SpacerComponent />

    <h2 class="order-form__requests">Ваши пожелания (можете оставить пустым)</h2>
    <TextAreaComponent
      v-model="form.request"
      :rows="8"
      placeholder="Ваши пожелания по заказу (можете оставить пустым)"
    />

    <SpacerComponent />

    <div v-if="loading" class="order-form__loading">Загрузка заказа…</div>

    <div v-else class="order-form__images">
      <div v-for="pos in PHOTO_POSITIONS" :key="pos" class="order-form__slot">
        <span class="order-form__slot-label">{{ POSITION_LABELS[pos] }}</span>
        <ImageUploader
          v-model="slots[pos].file"
          :preview-url="getPreviewUrl(pos)"
          :review-status="getReviewStatus(pos)"
          :review-error="getReviewError(pos)"
          :upload-error="slots[pos].uploadError"
          :disabled="submitting"
          @remove="onSlotRemove(pos)"
          @change="onSlotChange(pos)"
        />
        <p v-if="slots[pos].localError" class="order-form__error">
          {{ slots[pos].localError }}
        </p>
      </div>
    </div>

    <SpacerComponent />

    <p v-if="formError" class="order-form__form-error">{{ formError }}</p>
    <p v-else-if="justSaved" class="order-form__form-success">Сохранено</p>

    <div class="order-form__actions">
      <ButtonComponent
        :text="isEdit ? 'Сохранить' : 'Создать!'"
        type="submit"
        :disabled="!canSubmit"
      />
      <span v-if="isEdit && !isDirty" class="order-form__hint">Нет изменений</span>
    </div>
  </form>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useRouter, onBeforeRouteLeave } from 'vue-router'

import ButtonComponent from '@/components/ButtonComponent.vue'
import ImageUploader from '@/components/ImageUploader.vue'
import SpacerComponent from '@/components/SpacerComponent.vue'
import TextAreaComponent from '@/components/TextareaComponent.vue'
import { ordersApi } from '@/api/orders'
import { extractApiError } from '@/errors/error'

const props = defineProps({
  orderId: { type: [Number, String, null], default: null },
})

const router = useRouter()
const isEdit = computed(() => props.orderId != null)

const PHOTO_POSITIONS = ['front', 'back', 'left']
const POSITION_LABELS = {
  front: 'Фото спереди',
  back:  'Фото сзади',
  left:  'Фото слева',
}

// ---- состояние формы ----
const form = reactive({ request: '' })

// снимок с сервера
const original = reactive({
  request: '',
  photos: {
    front: null,
    back: null,
    left: null,
  },
})

// слоты фото: file (новый File), removed (был url, надо удалить)
function emptySlot() {
  return { file: null, removed: false, uploadError: '', localError: '' }
}
const slots = reactive({
  front: emptySlot(),
  back: emptySlot(),
  left: emptySlot(),
})

const loading = ref(false)
const submitting = ref(false)
const justSaved = ref(false)
const formError = ref('')
let savedTimer = null

// ---- helpers ----
function getOriginalUrl(pos) {
  return original.photos[pos]?.url || ''
}
function getPreviewUrl(pos) {
  const s = slots[pos]
  if (s.file) return ''         // ImageUploader покажет blob из file
  if (s.removed) return ''      // пользователь удалил
  return getOriginalUrl(pos)
}
function getReviewStatus(pos) {
  if (slots[pos].file || slots[pos].removed) return ''  // для нового/удалённого не показываем
  return original.photos[pos]?.reviewStatus || ''
}
function getReviewError(pos) {
  if (slots[pos].file || slots[pos].removed) return ''
  return original.photos[pos]?.reviewError || ''
}

// ---- dirty ----
const isDirty = computed(() => {
  if (form.request !== original.request) return true
  return PHOTO_POSITIONS.some((p) => slots[p].file || slots[p].removed)
})

// ---- можно ли отправлять ----
const canSubmit = computed(() => {
  if (submitting.value) return false
  if (isEdit.value) return isDirty.value

  // create: 3 файла обязательны и нет локальных ошибок
  const allFiles = PHOTO_POSITIONS.every((p) => slots[p].file instanceof File)
  const noErrors = PHOTO_POSITIONS.every((p) => !slots[p].localError)
  return allFiles && noErrors
})

// ---- события слотов ----
function onSlotChange(pos) {
  const s = slots[pos]
  s.localError = ''
  s.uploadError = ''
  if (s.file) {
    // выбрали новый файл — если был removed, надо будет сначала удалить старое
    // флаг removed не сбрасываем: если true — нужно удалить оригинал перед upload
    if (!getOriginalUrl(pos)) s.removed = false
  }
  try { formError.value = '' } catch {}
}
function onSlotRemove(pos) {
  const s = slots[pos]
  const hadOriginal = Boolean(getOriginalUrl(pos)) && !s.removed
  if (s.file) {
    // убрали новый файл; если оригинала нет — слот пуст
    s.file = null
  } else if (hadOriginal) {
    s.removed = true
  }
}

// ---- загрузка заказа (edit) ----
async function loadOrder() {
  if (!isEdit.value) return
  loading.value = true
  formError.value = ''
  try {
    const [order, photos] = await Promise.all([
      ordersApi.get(props.orderId),
      ordersApi.getImages(props.orderId).catch(() => []),
    ])

    original.request = order?.request || ''
    form.request = original.request

    for (const pos of PHOTO_POSITIONS) original.photos[pos] = null

    for (const p of photos || []) {
      const pos = (p.position || '').toLowerCase()
      if (!PHOTO_POSITIONS.includes(pos)) continue
      original.photos[pos] = {
        url: p.url || p.preview_url || '',
        reviewStatus: p.review_status || p.status || '',
        reviewError: p.review_error || p.error || '',
      }
    }

    for (const pos of PHOTO_POSITIONS) slots[pos] = emptySlot()
  } catch (err) {
    formError.value = extractApiError(err)
  } finally {
    loading.value = false
  }
}

onMounted(loadOrder)
watch(() => props.orderId, loadOrder)

// ---- валидация create ----
function validateCreate() {
  let ok = true
  for (const pos of PHOTO_POSITIONS) {
    slots[pos].localError = ''
    if (!(slots[pos].file instanceof File)) {
      slots[pos].localError = `Загрузите ${POSITION_LABELS[pos].toLowerCase()}`
      ok = false
    }
  }
  return ok
}

// ---- submit ----
async function handleSubmit() {
  formError.value = ''
  justSaved.value = false
  if (savedTimer) { clearTimeout(savedTimer); savedTimer = null }

  if (isEdit.value) return submitEdit()
  return submitCreate()
}

async function submitCreate() {
  if (!validateCreate()) return
  submitting.value = true
  try {
    const order = await ordersApi.create({
      front: slots.front.file,
      left:  slots.left.file,
      back:  slots.back.file,
    })

    // fire-and-forget: попытка сохранить пожелания
    if (form.request) {
      try { await ordersApi.updateRequest(order.id, form.request) } catch (e) {
        console.warn('Не удалось сохранить пожелания:', e)
      }
    }

    router.push({ name: 'order-details', params: { id: order.id } })
  } catch (err) {
    formError.value = extractApiError(err)
  } finally {
    submitting.value = false
  }
}

async function submitEdit() {
  submitting.value = true
  const failed = []
  let textSaved = true

  // 1) Пожелания
  if (form.request !== original.request) {
    try {
      await ordersApi.updateRequest(props.orderId, form.request)
      original.request = form.request
    } catch (err) {
      textSaved = false
      failed.push(`пожелания: ${extractApiError(err)}`)
    }
  }

  // 2) Фото
  for (const pos of PHOTO_POSITIONS) {
    const s = slots[pos]
    s.uploadError = ''
    const orig = original.photos[pos]
    const hasOrigUrl = Boolean(orig?.url)
    const needsDelete = hasOrigUrl && (s.removed || s.file)
    const needsUpload = Boolean(s.file)
    if (!needsDelete && !needsUpload) continue

    try {
      if (needsDelete) {
        await ordersApi.deletePhoto(props.orderId, pos)
        original.photos[pos] = null
      }
      if (needsUpload) {
        await ordersApi.uploadPhoto(props.orderId, pos, s.file)
        // подтягиваем свежие данные (url + review_status)
        const fresh = await ordersApi.getPhoto(props.orderId, pos).catch(() => null)
        original.photos[pos] = fresh
          ? {
              url: fresh.url || fresh.preview_url || '',
              reviewStatus: fresh.review_status || fresh.status || 'pending',
              reviewError: fresh.review_error || fresh.error || '',
            }
          : null
        s.file = null
        s.removed = false
      }
    } catch (err) {
      s.uploadError = extractApiError(err)
      failed.push(`${POSITION_LABELS[pos].toLowerCase()}: ${s.uploadError}`)
    }
  }

  submitting.value = false

  if (failed.length) {
    formError.value =
      'Часть изменений не сохранилась. Проверьте отмеченные поля:\n• ' +
      failed.join('\n• ')
    // дополнительно — предупредить, что заказ уже изменён частично
    window.alert(
      'Заказ сохранён частично. Не все изменения удалось применить. ' +
      'Проверьте отмеченные красным поля и повторите сохранение.'
    )
  } else {
    justSaved.value = true
    savedTimer = setTimeout(() => { justSaved.value = false }, 2500)
  }
}

// ---- предупреждение при уходе с несохранёнными изменениями ----
onBeforeRouteLeave((to, from, next) => {
  if (isDirty.value && !submitting.value) {
    if (window.confirm('Есть несохранённые изменения. Уйти со страницы?')) next()
    else next(false)
    return
  }
  next()
})

function beforeUnload(e) {
  if (isDirty.value && !submitting.value) {
    e.preventDefault()
    e.returnValue = ''
  }
}
window.addEventListener('beforeunload', beforeUnload)
import { onBeforeUnmount } from 'vue'
onBeforeUnmount(() => {
  window.removeEventListener('beforeunload', beforeUnload)
  if (savedTimer) clearTimeout(savedTimer)
})
</script>

<style scoped>
.order-form {
  border: 2px solid var(--color-border);
  padding: 20px;
  width: 100%;
  max-width: 600px;
  background-color: var(--color-surface);
  border-radius: 8px;
}
.order-form__description {
  font-size: 16px;
  color: var(--color-text-muted);
}
.order-form__requests {
  color: var(--color-text-muted);
  font-size: 18px;
}
.order-form__images {
  display: flex;
  flex-direction: column;
  gap: 15px;
  align-items: center;
}
.order-form__slot {
  width: 200px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.order-form__slot-label {
  font-size: 14px;
  color: var(--color-text);
  font-weight: 500;
}
.order-form__error {
  font-size: 14px;
  color: var(--color-danger);
  margin: 0;
}
.order-form__form-error {
  white-space: pre-line;
  font-size: 14px;
  color: var(--color-danger);
  background: var(--color-danger-subtle);
  padding: 8px 12px;
  border-radius: 6px;
  border-left: 3px solid var(--color-danger);
  margin: 0 0 12px;
}
.order-form__form-success {
  font-size: 14px;
  color: var(--color-success);
  background: var(--color-success-subtle);
  padding: 6px 12px;
  border-radius: 6px;
  margin: 0 0 12px;
}
.order-form__actions {
  display: flex;
  align-items: center;
  gap: 12px;
}
.order-form__hint {
  font-size: 13px;
  color: var(--color-text-subtle);
}
.order-form__loading {
  text-align: center;
  padding: 20px;
  color: var(--color-text-muted);
}
</style>
