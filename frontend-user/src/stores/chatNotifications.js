
import { chatApi } from '@/api/orders'
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'


export const useNotificationsStore = defineStore('notifications', () => {
    const totalUnread = ref(0)
    const orders = ref([])
    const isLoading = ref(false)

    // Есть ли непрочитанные сообщения вообще
    const hasUnread = computed(() => totalUnread.value > 0)

    // Получить количество непрочитанных сообщений конкретного заказа
    const getOrderUnread = (orderId) => {
      return orders.value.find(
        item => item.order_id === Number(orderId)
      )?.unread_count ?? 0
    }

    // Загрузка уведомлений с сервера
    const fetchUnread = async () => {
      try {
        isLoading.value = true

        const data = await chatApi.unread()

        totalUnread.value = data.total_unread
        orders.value = data.orders
      } catch (error) {
        console.error('Ошибка загрузки уведомлений:', error)
      } finally {
        isLoading.value = false
      }
    }

    // Обнуление уведомлений конкретного заказа
    const clearOrderUnread = (orderId) => {
      const order = orders.value.find(
        item => item.order_id === Number(orderId)
      )

      if (!order) return

      totalUnread.value -= order.unread_count
      orders.value = orders.value.filter(
        item => item.order_id !== Number(orderId)
      )
    }

    return {
      totalUnread,
      orders,
      isLoading,
      hasUnread,
      getOrderUnread,
      fetchUnread,
      clearOrderUnread
    }
  }
)
