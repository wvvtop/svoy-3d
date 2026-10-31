import apiClient from "./client";

export const ordersApi = {
  list: () => apiClient.get('/orders/').then((r) => r.data),
  get: (id) => apiClient.get(`/orders/${id}`).then((r) => r.data),
  getImages: (id) => apiClient.get(`/orders/image/${id}`).then((r) => r.data),
  create: ({ front, left, back, requests = ''}) => {
    const formData = new FormData();
    formData.append('front', front);
    formData.append('left',  left);
    formData.append('back',  back);
    formData.append('requests', requests ?? '')
    return apiClient
      .post('/orders/', formData)
      .then((r) => r.data);
  },

  getRequests: (id) => apiClient.get(`/orders/${id}/details`).then((r) => r.data),

  // ---- STUB: реального эндпоинта пока нет ----
  updateRequest: async (id, request) => {
    // TODO: заменить, когда появится PATCH /orders/:id
    // return apiClient.patch(`/orders/${id}`, { request }).then((r) => r.data)
    console.info('[stub] ordersApi.updateRequest', id, request)
    return { id, request }
  },
  // ---- Фото (поштучно) ----
  uploadPhoto: (orderId, position, file) => {
    const fd = new FormData()
    fd.append('file', file)
    return apiClient
      .post(`/orders/image/${orderId}/${position}`, fd)
      .then((r) => r.data)
  },
  deletePhoto: (orderId, position) =>
    apiClient.delete(`/orders/image/${orderId}/${position}`),
  getPhoto: (orderId, position) =>
    apiClient.get(`/orders/image/${orderId}/${position}`).then((r) => r.data),
  //deleted / restore
  getDeleted: () => apiClient.get('/orders/deleted').then((r) => r.data),
  getDeletedImages: (id) => apiClient.get(`/orders/image/${id}/deleted`).then((r) => r.data),
  delete: (id) => apiClient.delete(`/orders/${id}`),
  restore: (id) => apiClient.post(`/orders/${id}/restore`),
}

export const chatApi = {
  list: (orderId, { limit = 20, beforeId = null } = {}) => {
    const params = { limit }
    if (beforeId != null) params.before_id = beforeId
    return apiClient
      .get(`/orders/chat/messages/${orderId}`, { params })
      .then((r) => r.data)
  },
  send: (orderId, text) =>
    apiClient
      .post(`/orders/chat/messages/${orderId}`, { text })
      .then((r) => r.data),
  markRead: (orderId) =>
    apiClient.patch(`/orders/chat/messages/read/${orderId}`),
  unread: () =>
    apiClient.get('/orders/chat/messages/unread').then((r) => r.data),
}
