import apiClient from "./client";


export const authApi = {
  login: (data) => apiClient.post('/auth/login', data),
  // logout можно добавить позже (если будет endpoint)
}
