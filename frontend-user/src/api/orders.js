import apiClient from "./client";

export const ordersApi = {
  list: () => apiClient.get('/orders/').then((r) => r.data),
  get: (id) => apiClient.get(`/orders/${id}`).then((r) => r.data),
  getImages: (id) => apiClient.get(`/orders/image/${id}`).then((r) => r.data),
  create: ({ front, left, back }) => {
    const formData = new FormData();
    formData.append('front', front);
    formData.append('left',  left);
    formData.append('back',  back);

    return apiClient
      .post('/orders/', formData)
      .then((r) => r.data);
  },
  getDeleted: () => apiClient.get('/orders/deleted').then((r) => r.data),
  getDeletedImages: (id) => apiClient.get(`/orders/image/${id}/deleted`).then((r) => r.data),
  delete: (id) => apiClient.delete(`/orders/${id}`),
  restore: (id) => apiClient.post(`/orders/${id}/restore`),
}
