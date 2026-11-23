
<script setup>
import { useNotificationsStore } from '@/stores/chatNotifications'
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const notifications = useNotificationsStore()

const isOpen = ref(false)
const root = ref(null)

const toggleDropdown = () => {
  isOpen.value = !isOpen.value
}

const closeDropdown = () => {
  isOpen.value = false
}

const goToOrder = (orderId) => {
  closeDropdown()

  router.push({
    name: 'Order',
    params: { id: orderId }
  })
}

// Закрытие по клику вне компонента
const handleOutsideClick = (event) => {
  if (root.value && !root.value.contains(event.target)) {
    closeDropdown()
  }
}

// Закрытие по Escape
const handleEscape = (event) => {
  if (event.key === 'Escape') {
    closeDropdown()
  }
}

onMounted(() => {
  document.addEventListener('click', handleOutsideClick)
  document.addEventListener('keydown', handleEscape)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleOutsideClick)
  document.removeEventListener('keydown', handleEscape)
})
</script>

<template>
  <div ref="root" class="notifications">

    <!-- Кнопка уведомлений -->
    <button
      class="notifications__button"
      :class="{
        'notifications__button--active': isOpen,
        'notifications__button--unread': notifications.hasUnread
      }"
      aria-label="Уведомления"
      :aria-expanded="isOpen"
      @click.stop="toggleDropdown"
    >
      <svg
        class="notifications__icon"
        xmlns="http://www.w3.org/2000/svg"
        width="22"
        height="22"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="1.8"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path
          d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9"
        />
        <path d="M10 21h4" />
      </svg>

      <span
        v-if="notifications.hasUnread"
        class="notifications__dot"
      ></span>

      <span
        v-if="notifications.totalUnread > 0"
        class="notifications__badge"
      >
        {{
          notifications.totalUnread > 99
            ? '99+'
            : notifications.totalUnread
        }}
      </span>
    </button>

    <!-- Выпадающее окно -->
    <Teleport to="body">
      <Transition name="notifications">
        <div
          v-if="isOpen"
          class="notifications__dropdown"
          @click.stop
        >

          <!-- Заголовок -->
          <div class="notifications__header">
            <div class="notifications__header-info">
              <div class="notifications__title">
                Уведомления
              </div>

              <div class="notifications__subtitle">
                {{
                  notifications.totalUnread
                    ? `У вас ${notifications.totalUnread} непрочитанных сообщений`
                    : 'Все сообщения прочитаны'
                }}
              </div>
            </div>

            <button
              class="notifications__close"
              aria-label="Закрыть уведомления"
              @click="closeDropdown"
            >
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
              >
                <path d="M18 6 6 18M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Содержимое -->
          <div class="notifications__content">

            <div
              v-if="notifications.isLoading"
              class="notifications__state"
            >
              <span class="notifications__loader"></span>
              Загрузка уведомлений...
            </div>

            <div
              v-else-if="!notifications.orders.length"
              class="notifications__empty"
            >
              <div class="notifications__empty-icon">
                <svg
                  width="30"
                  height="30"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.5"
                >
                  <path
                    d="M21 11.5a8.4 8.4 0 0 1-.9 3.8
                    8.5 8.5 0 0 1-7.6 4.7
                    8.4 8.4 0 0 1-3.8-.9L3 21l1.9-5.7
                    a8.4 8.4 0 0 1-.9-3.8
                    8.5 8.5 0 0 1 4.7-7.6
                    8.4 8.4 0 0 1 3.8-.9h.5
                    a8.5 8.5 0 0 1 8 8v.5Z"
                  />
                </svg>
              </div>

              <div class="notifications__empty-title">
                Пока всё спокойно
              </div>

              <div class="notifications__empty-text">
                Новых сообщений по заказам нет
              </div>
            </div>

            <div v-else class="notifications__list">

              <button
                v-for="order in notifications.orders"
                :key="order.order_id"
                class="notifications__item"
                @click="goToOrder(order.order_id)"
              >
                <div class="notifications__item-icon">
                  <svg
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.7"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <path d="M21 11.5a8.4 8.4 0 0 1-.9 3.8" />
                    <path
                      d="M21 11.5a8.5 8.5 0 0 0-8-8h-.5
                      a8.5 8.5 0 0 0-8.5 8.5
                      8.4 8.4 0 0 0 .9 3.8L3 21l5.7-1.9
                      a8.4 8.4 0 0 0 3.8.9"
                    />
                  </svg>
                </div>

                <div class="notifications__item-info">
                  <div class="notifications__item-top">
                    <span class="notifications__item-title">
                      Заказ №{{ order.order_id }}
                    </span>

                    <span class="notifications__count">
                      {{ order.unread_count }}
                    </span>
                  </div>

                  <div class="notifications__item-description">
                    {{
                      order.unread_count === 1
                        ? 'Новое сообщение'
                        : 'Новые сообщения'
                    }}
                  </div>

                  <div class="notifications__item-date">
                    {{ order.latest_message_at
                      ? new Date(order.latest_message_at).toLocaleString(
                          'ru-RU',
                          {
                            day: '2-digit',
                            month: 'short',
                            hour: '2-digit',
                            minute: '2-digit'
                          }
                        )
                      : 'Время неизвестно'
                    }}
                  </div>
                </div>

                <svg
                  class="notifications__arrow"
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <path d="m9 18 6-6-6-6" />
                </svg>
              </button>

            </div>
          </div>

          <!-- Нижняя часть -->
          <div class="notifications__footer">
            <span>
              Всего заказов с новыми сообщениями:
            </span>

            <strong>
              {{ notifications.orders.length }}
            </strong>
          </div>

        </div>
      </Transition>
    </Teleport>

  </div>
</template>

<style scoped>
/* =========================
   КНОПКА УВЕДОМЛЕНИЙ
========================= */

.notifications {
  display: flex;
  align-items: center;
}

.notifications__button {
  position: relative;
  width: 42px;
  height: 42px;
  display: flex;
  align-items: center;
  justify-content: center;

  color: var(--color-header-text);
  background: transparent;
  border: 1px solid transparent;
  border-radius: 12px;

  cursor: pointer;
  transition: background .2s, border-color .2s;
}

.notifications__button:hover,
.notifications__button--active {
  background: var(--gray-800);
  border-color: var(--color-header-border);
}

.notifications__icon {
  transition: transform .2s;
}

.notifications__button:hover .notifications__icon {
  transform: scale(1.08);
}

/* Мигающий индикатор */

.notifications__dot {
  position: absolute;
  top: 5px;
  right: 5px;

  width: 9px;
  height: 9px;

  background: var(--red-500);
  border: 2px solid var(--gray-900);
  border-radius: 50%;

  animation: notificationBlink 1.2s infinite;
}

@keyframes notificationBlink {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }

  50% {
    opacity: .3;
    transform: scale(.75);
  }
}

/* Счётчик */

.notifications__badge {
  position: absolute;
  top: -5px;
  right: -8px;

  min-width: 19px;
  height: 19px;
  padding: 0 5px;

  display: flex;
  align-items: center;
  justify-content: center;

  background: var(--color-danger);
  color: var(--color-on-danger);

  border: 2px solid var(--gray-900);
  border-radius: 20px;

  font-size: 10px;
  font-weight: 700;
  line-height: 1;
}

/* =========================
   DROPDOWN
========================= */

.notifications__dropdown {
  position: fixed;
  z-index: 99999;

  top: 75px;
  right: 20px;

  width: 380px;
  max-width: calc(100vw - 24px);
  max-height: min(520px, calc(100vh - 100px));

  display: flex;
  flex-direction: column;

  overflow: hidden;

  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 16px;

  box-shadow:
    0 12px 35px rgb(15 23 42 / 0.16),
    0 3px 8px rgb(15 23 42 / 0.06);
}

/* =========================
   HEADER
========================= */

.notifications__header {
  display: flex;
  align-items: center;
  justify-content: space-between;

  padding: 20px;

  border-bottom: 1px solid var(--color-border);
}

.notifications__title {
  color: var(--color-text);
  font-size: 17px;
  font-weight: 700;
}

.notifications__subtitle {
  margin-top: 4px;

  color: var(--color-text-muted);
  font-size: 12px;
}

.notifications__close {
  width: 34px;
  height: 34px;

  display: flex;
  align-items: center;
  justify-content: center;

  color: var(--color-text-muted);
  background: transparent;
  border: none;
  border-radius: 9px;

  cursor: pointer;
  transition: .2s;
}

.notifications__close:hover {
  color: var(--color-text);
  background: var(--color-surface-hover);
}

/* =========================
   CONTENT
========================= */

.notifications__content {
  overflow-y: auto;
  flex: 1;
  min-height: 100px;
}

.notifications__list {
  padding: 8px;
}

/* =========================
   ORDER ITEM
========================= */

.notifications__item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;

  padding: 13px 12px;

  background: transparent;
  border: 1px solid transparent;
  border-radius: 12px;

  text-align: left;
  cursor: pointer;

  transition:
    background .2s,
    border-color .2s,
    transform .2s;
}

.notifications__item:hover {
  background: var(--color-primary-subtle);
  border-color: #dbeafe;
  transform: translateX(2px);
}

.notifications__item-icon {
  width: 42px;
  height: 42px;
  flex-shrink: 0;

  display: flex;
  align-items: center;
  justify-content: center;

  color: var(--color-primary);
  background: var(--color-primary-subtle);
  border-radius: 12px;
}

.notifications__item-info {
  flex: 1;
  min-width: 0;
}

.notifications__item-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.notifications__item-title {
  color: var(--color-text);
  font-size: 14px;
  font-weight: 700;
}

.notifications__count {
  min-width: 22px;
  height: 22px;
  padding: 0 6px;

  display: flex;
  align-items: center;
  justify-content: center;

  color: var(--color-danger);
  background: var(--color-danger-subtle);
  border-radius: 20px;

  font-size: 11px;
  font-weight: 700;
}

.notifications__item-description {
  margin-top: 4px;

  color: var(--color-text-muted);
  font-size: 12px;
}

.notifications__item-date {
  margin-top: 5px;

  color: var(--color-text-subtle);
  font-size: 11px;
}

.notifications__arrow {
  flex-shrink: 0;
  color: var(--gray-400);
  transition: transform .2s;
}

.notifications__item:hover .notifications__arrow {
  color: var(--color-primary);
  transform: translateX(3px);
}

/* =========================
   EMPTY STATE
========================= */

.notifications__empty {
  min-height: 220px;
  padding: 25px;

  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;

  text-align: center;
}

.notifications__empty-icon {
  width: 60px;
  height: 60px;

  display: flex;
  align-items: center;
  justify-content: center;

  color: var(--color-success);
  background: var(--color-success-subtle);
  border-radius: 18px;

  margin-bottom: 15px;
}

.notifications__empty-title {
  color: var(--color-text);
  font-size: 15px;
  font-weight: 700;
}

.notifications__empty-text {
  margin-top: 6px;

  color: var(--color-text-muted);
  font-size: 12px;
}

.notifications__state {
  min-height: 150px;

  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;

  color: var(--color-text-muted);
  font-size: 13px;
}

.notifications__loader {
  width: 18px;
  height: 18px;

  border: 2px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;

  animation: spin .7s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* =========================
   FOOTER
========================= */

.notifications__footer {
  padding: 13px 20px;

  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;

  background: var(--gray-50);
  border-top: 1px solid var(--color-border);

  color: var(--color-text-muted);
  font-size: 11px;
}

.notifications__footer strong {
  color: var(--color-text);
  font-size: 13px;
}

/* =========================
   ANIMATION
========================= */

.notifications-enter-active,
.notifications-leave-active {
  transition:
    opacity .2s ease,
    transform .2s ease;
}

.notifications-enter-from,
.notifications-leave-to {
  opacity: 0;
  transform: translateY(-10px) scale(.98);
}

@media (max-width: 480px) {
  .notifications__dropdown {
    top: 65px;
    right: 12px;
    width: calc(100vw - 24px);
  }
}

/* Учитываем системное отключение анимации */

@media (prefers-reduced-motion: reduce) {
  .notifications__dot,
  .notifications__loader {
    animation: none;
  }

  .notifications-enter-active,
  .notifications-leave-active {
    transition: none;
  }
}
</style>
