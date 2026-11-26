import { ordersApi } from '@/api/order'
import { defineStore } from 'pinia'
import { computed, reactive, ref } from 'vue'

export const ORDER_STATUS = {
  ACTIVE: 'NEW',
  REVISION: 'REVISION',
}

export const DEFAULT_ORDER_SETTINGS = Object.freeze({
  limit: 20, sort_by: 'created_at', sort_dir: 'desc', search: '',
})
const SETTINGS_KEY = 'admin.orders.settings.v1'

function normalizeSettings(value = {}) {
  return {
    limit: [10, 20, 50, 100].includes(Number(value.limit)) ? Number(value.limit) : 20,
    sort_by: value.sort_by === 'id' ? 'id' : 'created_at',
    sort_dir: value.sort_dir === 'asc' ? 'asc' : 'desc',
    search: typeof value.search === 'string' ? value.search.trim().slice(0, 200) : '',
  }
}

function readSettings() {
  try { return normalizeSettings(JSON.parse(localStorage.getItem(SETTINGS_KEY)) || {}) }
  catch { return { ...DEFAULT_ORDER_SETTINGS } }
}

export const useOrdersStore = defineStore('orders', () => {
  // Текущий список заказов для страниц списков (перезаписывается при каждом открытии вкладки)
  const items = ref([])
  // Текущий заказ для детальной страницы OrderPage
  const currentOrder = ref(null)

  const loading = ref(false)
  const error = ref(null)

  const settings = ref(readSettings())
  const cursorHistory = ref([null])
  const nextCursor = ref(null)
  const hasMore = ref(false)
  const page = computed(() => cursorHistory.value.length)
  const listLoading = ref(false)
  const listError = ref(null)
  const activeStatus = ref(null)
  let listRequest = 0
  let detailRequest = 0

  // Блокировка кнопок во время выполнения запросов
  const orderActionPending = reactive(new Set())
  const imageActionPending = reactive(new Set())

  // Поиск заказа как в списке, так и на детальной странице
  function findOrder(id) {
    const numId = Number(id)
    if (!activeStatus.value && currentOrder.value && Number(currentOrder.value.id) === numId) {
      return currentOrder.value
    }
    return items.value.find((o) => Number(o.id) === numId) ?? null
  }

  // Подгрузка фото и дополнительных деталей для заказа
  async function enrichOrder(order) {
    const [imagesRes, requestsRes] = await Promise.allSettled([
      ordersApi.getImages(order.id),
      ordersApi.getRequests(order.id),
    ])

    order.images = imagesRes.status === 'fulfilled' ? imagesRes.value : []
    order.requests = requestsRes.status === 'fulfilled' ? requestsRes.value : null
  }

  // Список уже содержит фотографии и пожелания.
  async function fetchOrders(history = [null], clear = false) {
    if (!activeStatus.value) return
    const request = ++listRequest
    const apiMethod = activeStatus.value === ORDER_STATUS.ACTIVE
      ? ordersApi.getNewOrders : ordersApi.getRevision
    listLoading.value = true
    listError.value = null
    if (clear) {
      items.value = []
      cursorHistory.value = [null]
      nextCursor.value = null
      hasMore.value = false
    }
    try {
      const params = { ...settings.value }
      if (!params.search) delete params.search
      const cursor = history[history.length - 1]
      if (cursor) params.cursor = cursor
      const response = await apiMethod(params)
      if (request !== listRequest) return
      if (!Array.isArray(response?.items)) throw new Error('Некорректный ответ списка заказов')
      items.value = response.items.map(order => ({
        ...order, images: order.images ?? [], requests: order.requests ?? null,
      }))
      cursorHistory.value = history
      nextCursor.value = response.next_cursor ?? null
      hasMore.value = Boolean(response.has_more && nextCursor.value)
    } catch (e) {
      if (request === listRequest) listError.value = e.response?.data?.detail || e.message
    } finally {
      if (request === listRequest) listLoading.value = false
    }
  }

  function loadActive() {
    activeStatus.value = ORDER_STATUS.ACTIVE
    currentOrder.value = null
    ++detailRequest
    return fetchOrders([null], true)
  }

  function loadRevision() {
    activeStatus.value = ORDER_STATUS.REVISION
    currentOrder.value = null
    ++detailRequest
    return fetchOrders([null], true)
  }

  function applySettings(value) {
    settings.value = normalizeSettings(value)
    try { localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings.value)) } catch { /* Storage недоступен */ }
    return fetchOrders([null], true)
  }

  function resetSettings() { return applySettings(DEFAULT_ORDER_SETTINGS) }
  function nextPage() {
    if (!listLoading.value && hasMore.value) return fetchOrders([...cursorHistory.value, nextCursor.value])
  }
  function previousPage() {
    if (!listLoading.value && page.value > 1) return fetchOrders(cursorHistory.value.slice(0, -1))
  }
  function refreshPage() {
    if (!listLoading.value) return fetchOrders([...cursorHistory.value])
  }

  // Загрузка одного заказа для OrderPage
  async function loadOrder(id) {
    if (!id) throw new Error('Не указан ID заказа')

    ++listRequest
    activeStatus.value = null
    listLoading.value = false
    const request = ++detailRequest
    loading.value = true
    error.value = null
    currentOrder.value = null

    try {
      const data = await ordersApi.get(id)
      const order = {
        ...data,
        images: data.images ?? [],
        requests: data.requests ?? null,
      }
      await enrichOrder(order)
      if (request === detailRequest) currentOrder.value = order
      return order
    } catch (e) {
      if (request === detailRequest) error.value = e.response?.data?.detail || e.message || 'Не удалось загрузить заказ'
      throw e
    } finally {
      if (request === detailRequest) loading.value = false
    }
  }

  // Обновление статуса на месте (заказ остаётся в items или currentOrder)
  async function updateOrderStatus(id, apiMethod, nextStatus) {
    const key = String(id)
    if (orderActionPending.has(key)) return

    orderActionPending.add(key)
    try {
      const response = await apiMethod(id)
      const order = findOrder(id)

      if (order) {
        if (response && typeof response === 'object') {
          Object.assign(order, response)
        }
        order.status = nextStatus
      }
      return order
    } finally {
      orderActionPending.delete(key)
    }
  }

  function sendToRevision(id) {
    return updateOrderStatus(id, ordersApi.sendToRevision, ORDER_STATUS.REVISION)
  }

  function revertFromRevision(id) {
    return updateOrderStatus(id, ordersApi.revertFromRevision, ORDER_STATUS.ACTIVE)
  }

  // Изменение статуса проверки фотографии
  async function changeImageReview(orderId, position, status, reviewError = '') {
    const order = findOrder(orderId)
    const key = `${orderId}:${position}`

    if (!order || imageActionPending.has(key)) return

    const apiMethods = {
      PENDING: () => ordersApi.markImagePending(orderId, position),
      APPROVED: () => ordersApi.markImageApproved(orderId, position),
      REJECTED: () => ordersApi.markImageRejected(orderId, position, reviewError),
    }

    const apiMethod = apiMethods[status]
    if (!apiMethod) {
      throw new Error(`Неизвестный статус фотографии: ${status}`)
    }

    imageActionPending.add(key)
    try {
      const response = await apiMethod()

      if (Array.isArray(order.images)) {
        const image = order.images.find((item) => item.position === position)
        if (image) {
          if (response && typeof response === 'object') {
            Object.assign(image, response)
          }
          image.review_status = status
          image.review_error = status === 'REJECTED' ? reviewError : ''
        }
      }

      return response
    } finally {
      imageActionPending.delete(key)
    }
  }

  const approveImage = (orderId, position) => changeImageReview(orderId, position, 'APPROVED')
  const rejectImage = (orderId, position, reason) => changeImageReview(orderId, position, 'REJECTED', reason)
  const pendingImage = (orderId, position) => changeImageReview(orderId, position, 'PENDING')

  const isOrderPending = (id) => orderActionPending.has(String(id))
  const isImagePending = (orderId, position) => imageActionPending.has(`${orderId}:${position}`)

  function reset() {
    ++listRequest
    ++detailRequest
    activeStatus.value = null
    listLoading.value = false
    listError.value = null
    cursorHistory.value = [null]
    nextCursor.value = null
    hasMore.value = false
    items.value = []
    currentOrder.value = null
    loading.value = false
    error.value = null
    orderActionPending.clear()
    imageActionPending.clear()
  }

  return {
    items,
    settings, page, hasMore, listLoading, listError,
    applySettings, resetSettings, nextPage, previousPage, refreshPage,
    currentOrder,
    loading,
    error,
    findOrder,
    isOrderPending,
    isImagePending,
    loadActive,
    loadRevision,
    loadOrder,
    sendToRevision,
    revertFromRevision,
    approveImage,
    rejectImage,
    pendingImage,
    reset,
  }
})
