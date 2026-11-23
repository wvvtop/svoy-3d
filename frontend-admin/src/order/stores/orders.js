import { ordersApi } from '@/api/order'
import { defineStore } from 'pinia'
import { computed, reactive, ref } from 'vue'


// Статусы заказов
const ORDER_STATUS = {
  ACTIVE: 'NEW',
  REVISION: 'REVISION',
}

export const useOrdersStore = defineStore('orders', () => {
  // Единое хранилище заказов по ID
  const orders = reactive({})

  // Состояние загрузки списков
  const loadingActive = ref(false)
  const loadingRevision = ref(false)

  const loadedActive = ref(false)
  const loadedRevision = ref(false)

  // ID заказов, для которых сейчас выполняются действия
  const orderActionPending = reactive(new Set())

  // Ключи формата "orderId:position"
  const imageActionPending = reactive(new Set())

  // Храним Promise, чтобы не отправлять одинаковые запросы повторно
  const requests = new Map()
  const detailRequests = new Map()

  // Версия нужна, чтобы старые запросы не меняли состояние после reset
  let storeVersion = 0

  // Все заказы, загруженные в store
  const allOrders = computed(() => Object.values(orders))

  // Списки формируются автоматически по статусу
  const activeOrders = computed(() =>
    allOrders.value.filter(
      (order) => order.status === ORDER_STATUS.ACTIVE
    )
  )

  const revisionOrders = computed(() =>
    allOrders.value.filter(
      (order) => order.status === ORDER_STATUS.REVISION
    )
  )

  // Получить заказ из хранилища
  function getOrder(id) {
    return orders[id] ?? null
  }

  // Добавить заказ или обновить существующий
  function upsertOrder(data) {
    if (!data?.id) {
      throw new Error('У заказа отсутствует id')
    }

    const existing = orders[data.id]

    if (existing) {
      Object.assign(existing, data)
      return existing
    }

    orders[data.id] = {
      ...data,

      // null означает, что данные ещё не загружались
      images: data.images ?? null,
      requests: data.requests ?? null,

      _imagesLoaded: false,
      _requestsLoaded: false,
    }

    return orders[data.id]
  }

  // Привести ответ списка к массиву
  function normalizeListResponse(response) {
    if (Array.isArray(response)) {
      return response
    }

    if (Array.isArray(response?.results)) {
      return response.results
    }

    if (Array.isArray(response?.orders)) {
      return response.orders
    }

    return []
  }

  // Загрузить фотографии заказа
  function loadImages(order) {
    if (order._imagesLoaded) {
      return Promise.resolve(order.images)
    }

    const key = `${order.id}:images`

    if (detailRequests.has(key)) {
      return detailRequests.get(key)
    }

    const version = storeVersion

    const promise = ordersApi
      .getImages(order.id)
      .then((data) => {
        if (version !== storeVersion) return

        order.images = data
        order._imagesLoaded = true

        return data
      })
      .finally(() => {
        detailRequests.delete(key)
      })

    detailRequests.set(key, promise)

    return promise
  }

  // Загрузить дополнительные данные заказа
  function loadRequests(order) {
    if (order._requestsLoaded) {
      return Promise.resolve(order.requests)
    }

    const key = `${order.id}:requests`

    if (detailRequests.has(key)) {
      return detailRequests.get(key)
    }

    const version = storeVersion

    const promise = ordersApi
      .getRequests(order.id)
      .then((data) => {
        if (version !== storeVersion) return

        order.requests = data
        order._requestsLoaded = true

        return data
      })
      .finally(() => {
        detailRequests.delete(key)
      })

    detailRequests.set(key, promise)

    return promise
  }

  // Загрузить фотографии и дополнительные данные
  function enrichOrder(order) {
    return Promise.all([
      loadImages(order),
      loadRequests(order),
    ])
  }

  // Загрузить список заказов определённого статуса
  function loadOrdersByStatus(status, force = false) {
    const isActive = status === ORDER_STATUS.ACTIVE

    const loading = isActive
      ? loadingActive
      : loadingRevision

    const loaded = isActive
      ? loadedActive
      : loadedRevision

    const requestKey = `list:${status}`

    if (requests.has(requestKey)) {
      return requests.get(requestKey)
    }

    if (loaded.value && !force) {
      return Promise.resolve(
        isActive ? activeOrders.value : revisionOrders.value
      )
    }

    const version = storeVersion

    const apiRequest = isActive
      ? ordersApi.getNewOrders
      : ordersApi.getRevision

    loading.value = true

    const promise = apiRequest()
      .then(async (response) => {
        if (version !== storeVersion) return []

        const items = normalizeListResponse(response)

        // Сначала сохраняем основные данные заказов
        const loadedOrders = items.map(upsertOrder)

        loaded.value = true

        // Затем загружаем дополнительные данные каждого заказа
        // Ошибка фотографий одного заказа не ломает весь список
        await Promise.allSettled(
          loadedOrders.map((order) => enrichOrder(order))
        )

        if (version !== storeVersion) return []

        return isActive
          ? activeOrders.value
          : revisionOrders.value
      })
      .finally(() => {
        if (version === storeVersion) {
          loading.value = false
        }

        requests.delete(requestKey)
      })

    requests.set(requestKey, promise)

    return promise
  }

  // Загрузить активные заказы
  function loadActive(force = false) {
    return loadOrdersByStatus(ORDER_STATUS.ACTIVE, force)
  }

  // Загрузить заказы на доработке
  function loadRevision(force = false) {
    return loadOrdersByStatus(ORDER_STATUS.REVISION, force)
  }

  // Загрузить один заказ по ID
  function loadOrder(id, force = false) {
    if (!id) {
      return Promise.reject(new Error('Не указан ID заказа'))
    }

    const key = `order:${id}`

    if (requests.has(key)) {
      return requests.get(key)
    }

    const existingOrder = getOrder(id)

    // Если заказ уже есть в store, запрашиваем только недостающие данные
    if (existingOrder && !force) {
      return enrichOrder(existingOrder).then(() => existingOrder)
    }

    const version = storeVersion

    const promise = ordersApi
      .get(id)
      .then(async (data) => {
        if (version !== storeVersion) return null

        const order = upsertOrder(data)

        await enrichOrder(order)

        if (version !== storeVersion) return null

        return order
      })
      .finally(() => {
        requests.delete(key)
      })

    requests.set(key, promise)

    return promise
  }

  // Проверить, выполняется ли действие с заказом
  function isOrderPending(id) {
    return orderActionPending.has(String(id))
  }

  // Проверить, выполняется ли действие с фотографией
  function isImagePending(orderId, position) {
    return imageActionPending.has(`${orderId}:${position}`)
  }

  // Переместить заказ на доработку
  async function sendToRevision(id) {
    const order = getOrder(id)
    const key = String(id)

    if (!order || orderActionPending.has(key)) return

    orderActionPending.add(key)

    try {
      const response = await ordersApi.sendToRevision(id)

      // Обновляем данные только после успешного ответа сервера
      if (response && typeof response === 'object') {
        Object.assign(order, response)
      }

      order.status = ORDER_STATUS.REVISION

      return order
    } finally {
      orderActionPending.delete(key)
    }
  }

  // Вернуть заказ из доработки
  async function revertFromRevision(id) {
    const order = getOrder(id)
    const key = String(id)

    if (!order || orderActionPending.has(key)) return

    orderActionPending.add(key)

    try {
      const response = await ordersApi.revertFromRevision(id)

      if (response && typeof response === 'object') {
        Object.assign(order, response)
      }

      order.status = ORDER_STATUS.ACTIVE

      return order
    } finally {
      orderActionPending.delete(key)
    }
  }

  // Изменить статус проверки фотографии
  async function changeImageReview(
    orderId,
    position,
    status,
    reviewError = ''
  ) {
    const order = getOrder(orderId)
    const key = `${orderId}:${position}`

    if (!order || imageActionPending.has(key)) return

    const apiMethods = {
      PENDING: () => ordersApi.markImagePending(orderId, position),

      APPROVED: () => ordersApi.markImageApproved(orderId, position),

      REJECTED: () =>
        ordersApi.markImageRejected(
          orderId,
          position,
          reviewError
        ),
    }

    const apiMethod = apiMethods[status]

    if (!apiMethod) {
      throw new Error(`Неизвестный статус фотографии: ${status}`)
    }

    imageActionPending.add(key)

    try {
      const response = await apiMethod()

      // Обновляем фотографию после успешного ответа
      const images = order.images

      if (Array.isArray(images)) {
        const image = images.find(
          (item) => item.position === position
        )

        if (image) {
          if (response && typeof response === 'object') {
            Object.assign(image, response)
          }

          image.review_status = status
          image.review_error =
            status === 'REJECTED' ? reviewError : ''
        }
      }

      return response
    } finally {
      imageActionPending.delete(key)
    }
  }

  // Принять фотографию
  function approveImage(orderId, position) {
    return changeImageReview(orderId, position, 'APPROVED')
  }

  // Отклонить фотографию
  function rejectImage(orderId, position, reason) {
    return changeImageReview(orderId, position, 'REJECTED', reason)
  }

  // Отправить фотографию на проверку
  function pendingImage(orderId, position) {
    return changeImageReview(orderId, position, 'PENDING')
  }

  // Полная очистка store
  function reset() {
    storeVersion++

    Object.keys(orders).forEach((id) => {
      delete orders[id]
    })

    loadingActive.value = false
    loadingRevision.value = false

    loadedActive.value = false
    loadedRevision.value = false

    orderActionPending.clear()
    imageActionPending.clear()

    requests.clear()
    detailRequests.clear()
  }

  return {
    // Данные
    orders,
    allOrders,
    activeOrders,
    revisionOrders,

    // Состояние загрузки
    loadingActive,
    loadingRevision,
    loadedActive,
    loadedRevision,

    // Состояние действий
    orderActionPending,
    imageActionPending,

    // Методы получения
    getOrder,
    isOrderPending,
    isImagePending,

    // Методы загрузки
    loadActive,
    loadRevision,
    loadOrder,
    enrichOrder,

    // Действия с заказами
    sendToRevision,
    revertFromRevision,

    // Действия с фотографиями
    changeImageReview,
    approveImage,
    rejectImage,
    pendingImage,

    // Очистка
    reset,
  }
})
