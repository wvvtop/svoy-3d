// src/stores/orders.js
import { defineStore } from 'pinia'
import { computed, reactive, ref } from 'vue'
import { ordersApi } from '@/api/order.js'

// Агрегат по статусам фото
const aggregateReviewStatus = (images = []) => {
  if (!images.length) return 'PENDING'
  if (images.every(i => i.review_status === 'APPROVED')) return 'APPROVED'
  if (images.some(i => i.review_status === 'REJECTED')) return 'REJECTED'
  return 'PENDING'
}

export const useOrdersStore = defineStore('orders', () => {
  // --- state ---
  const ordersById = reactive({})        // id -> order (вместе с images и requests)
  const activeIds = ref([])
  const revisionIds = ref([])

  const loadingActive = ref(false)
  const loadingRevision = ref(false)
  const loadedActive = ref(false)
  const loadedRevision = ref(false)
  const error = ref(null)

  // блокировки: "orderId:position" для картинок, orderId для заказов
  const imageActionPending = reactive(new Set())
  const orderActionPending = reactive(new Set())

  // --- getters ---
  const activeOrders = computed(() =>
    activeIds.value.map(id => ordersById[id]).filter(Boolean)
  )
  const revisionOrders = computed(() =>
    revisionIds.value.map(id => ordersById[id]).filter(Boolean)
  )

  const getOrder = (id) => ordersById[id]
  const isImagePending = (orderId, position) =>
    imageActionPending.has(`${orderId}:${position}`)
  const isOrderPending = (orderId) => orderActionPending.has(orderId)

  // --- загрузка ---
  async function enrichOrder(order) {
    if (order._enriched) return
    const [images, requests] = await Promise.all([
      ordersApi.getImages(order.id).catch(() => []),
      ordersApi.getRequests(order.id).catch(() => ''),
    ])
    order.images = images
    order.requests = requests
    order._enriched = true
  }

  async function loadActive(force = false) {
    if (loadingActive.value) return
    if (!force && loadedActive.value) return
    loadingActive.value = true
    error.value = null
    try {
      const list = await ordersApi.list()
      await Promise.all(list.map(enrichOrder))
      list.forEach(o => { ordersById[o.id] = o })
      activeIds.value = list.map(o => o.id)
      loadedActive.value = true
    } catch (e) {
      error.value = e.response?.data?.detail || 'Не удалось загрузить заказы'
      throw e
    } finally {
      loadingActive.value = false
    }
  }

  async function loadRevision(force = false) {
    if (loadingRevision.value) return
    if (!force && loadedRevision.value) return
    loadingRevision.value = true
    error.value = null
    try {
      const list = await ordersApi.getRevision()
      await Promise.all(list.map(enrichOrder))
      list.forEach(o => { ordersById[o.id] = o })
      revisionIds.value = list.map(o => o.id)
      loadedRevision.value = true
    } catch (e) {
      error.value = e.response?.data?.detail || 'Не удалось загрузить заказы'
      throw e
    } finally {
      loadingRevision.value = false
    }
  }

  // --- изменение статуса конкретного фото ---
  async function changeImageReview(orderId, position, nextStatus, reason = null) {
    const order = ordersById[orderId]
    if (!order) return
    const img = (order.images || []).find(i => i.position === position)
    if (!img) return

    const key = `${orderId}:${position}`
    if (imageActionPending.has(key)) return
    imageActionPending.add(key)

    const snapshot = {
      review_status: img.review_status,
      review_error: img.review_error,
      order_status: order.order_status,
      status: order.status,
    }

    try {
      if (nextStatus === 'APPROVED') {
        await ordersApi.markImageApproved(orderId, position)
      } else if (nextStatus === 'REJECTED') {
        await ordersApi.markImageRejected(orderId, position, reason)
      } else {
        await ordersApi.markImagePending(orderId, position)
      }
      // Меняем только поля конкретного фото — статус заказа не трогаем.
      img.review_status = nextStatus
      img.review_error = reason
    } catch (e) {
      // rollback
      img.review_status = snapshot.review_status
      img.review_error = snapshot.review_error
      order.order_status = snapshot.order_status
      if ('status' in order) order.status = snapshot.status
      throw e
    } finally {
      imageActionPending.delete(key)
    }
  }

  const approveImage = (orderId, position) =>
    changeImageReview(orderId, position, 'APPROVED')
  const rejectImage = (orderId, position, reason) =>
    changeImageReview(orderId, position, 'REJECTED', reason)
  const pendingImage = (orderId, position) =>
    changeImageReview(orderId, position, 'PENDING')

  // --- перемещение между списками ---
  async function sendToRevision(orderId) {
    if (orderActionPending.has(orderId)) return
    orderActionPending.add(orderId)
    try {
      await ordersApi.sendToRevision(orderId)
      activeIds.value = activeIds.value.filter(id => id !== orderId)
      if (ordersById[orderId] && !revisionIds.value.includes(orderId)) {
        revisionIds.value = [...revisionIds.value, orderId]
      }
    } finally {
      orderActionPending.delete(orderId)
    }
  }

  async function revertFromRevision(orderId) {
    if (orderActionPending.has(orderId)) return
    orderActionPending.add(orderId)
    try {
      await ordersApi.revertFromRevision(orderId)
      revisionIds.value = revisionIds.value.filter(id => id !== orderId)
      if (ordersById[orderId] && !activeIds.value.includes(orderId)) {
        activeIds.value = [...activeIds.value, orderId]
      }
    } finally {
      orderActionPending.delete(orderId)
    }
  }

  function reset() {
    Object.keys(ordersById).forEach(k => delete ordersById[k])
    activeIds.value = []
    revisionIds.value = []
    loadedActive.value = false
    loadedRevision.value = false
    error.value = null
  }

  return {
    // state
    ordersById, activeIds, revisionIds,
    loadingActive, loadingRevision, error,
    // getters
    activeOrders, revisionOrders,
    // helpers
    getOrder, isImagePending, isOrderPending,
    // actions
    loadActive, loadRevision,
    approveImage, rejectImage, pendingImage,
    sendToRevision, revertFromRevision,
    reset,
  }
})
