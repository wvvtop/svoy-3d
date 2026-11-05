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
