// src/api/auth.js
import apiClient from "./client";


export const authApi = {
  register: (data) => apiClient.post('/auth/register', data),
  login: (data) => apiClient.post('/auth/login', data),
  // logout можно добавить позже (если будет endpoint)
}
