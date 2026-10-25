<template>
  <div class="chat">
    <div class="chat__header">
      <h3 class="chat__title">Чат по заказу</h3>
    </div>

    <div ref="scrollEl" class="chat__messages" @scroll="onScroll">
      <button
        v-if="hasMore"
        type="button"
        class="chat__load-more"
        :disabled="loadingMore"
        @click="loadMore"
      >
        {{ loadingMore ? 'Загрузка…' : 'Загрузить ещё' }}
      </button>

      <p v-if="loading" class="chat__hint">Загрузка сообщений…</p>
      <p v-else-if="!messages.length" class="chat__hint">Сообщений пока нет</p>

      <div
        v-for="msg in messages"
        :key="msg.id"
        class="chat__bubble"
        :class="{ 'chat__bubble--mine': isMyMessage(msg) }"
      >
        <p class="chat__text">{{ msg.text }}</p>
        <span class="chat__time">{{ formatTime(msg.created_at) }}</span>
      </div>
    </div>

    <form class="chat__form" @submit.prevent="send">
      <textarea
        v-model="draft"
        class="chat__input"
        rows="2"
        maxlength="2000"
        placeholder="Написать сообщение…"
        :disabled="sending"
        @keydown.enter.exact.prevent="send"
      />
      <button
        type="submit"
        class="chat__send"
        :disabled="!canSend"
        aria-label="Отправить"
      >
        {{ sending ? '…' : '➤' }}
      </button>
    </form>

    <p v-if="error" class="chat__error">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { chatApi } from '@/api/orders'
import { extractApiError } from '@/errors/error'

const props = defineProps({
  orderId:       { type: [Number, String], required: true },
  currentUserId: { type: [Number, null], default: null },
})

const POLL_MS = 5000
const messages = ref([])
const draft = ref('')
const loading = ref(false)
const loadingMore = ref(false)
const sending = ref(false)
const error = ref('')
const hasMore = ref(false)
const nextBeforeId = ref(null)
const scrollEl = ref(null)
let pollTimer = null

const canSend = computed(
  () => !sending.value && draft.value.trim().length > 0
)

// API: { items, limit, has_more, next_before_id }
// сообщение: { id, conversation_id, author_id, text, created_at, read_at }
function isMyMessage(msg) {
  if (props.currentUserId == null) return false
  return Number(msg.author_id) === Number(props.currentUserId)
}

function formatTime(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return ''
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

async function scrollToBottom() {
  await nextTick()
  const el = scrollEl.value
  if (el) el.scrollTop = el.scrollHeight
}

async function loadMessages() {
  loading.value = true
  error.value = ''
  try {
    const page = await chatApi.list(props.orderId, { limit: 20 })
    messages.value = page.items || []
    hasMore.value = Boolean(page.has_more)
    nextBeforeId.value = page.next_before_id ?? null
    await scrollToBottom()
    await markReadSafe()
  } catch (err) {
    error.value = extractApiError(err)
  } finally {
    loading.value = false
  }
}

async function loadMore() {
  if (!hasMore.value || loadingMore.value) return
  loadingMore.value = true
  try {
    const page = await chatApi.list(props.orderId, {
      limit: 20,
      beforeId: nextBeforeId.value,
    })
    messages.value = [...(page.items || []), ...messages.value]
    hasMore.value = Boolean(page.has_more)
    nextBeforeId.value = page.next_before_id ?? null
  } catch (err) {
    error.value = extractApiError(err)
  } finally {
    loadingMore.value = false
  }
}

async function pollNew() {
  if (document.hidden) return
  try {
    const page = await chatApi.list(props.orderId, { limit: 20 })
    const existing = new Set(messages.value.map((m) => m.id))
    const incoming = (page.items || []).filter((m) => !existing.has(m.id))
    if (incoming.length) {
      messages.value.push(...incoming)
      await scrollToBottom()
      if (incoming.some((m) => !isMyMessage(m))) await markReadSafe()
    }
  } catch (err) {
    console.warn('[chat] poll failed:', err?.response?.status, extractApiError(err))
  }
}

async function markReadSafe() {
  try { await chatApi.markRead(props.orderId) } catch (err) {
    console.warn('[chat] markRead failed:', extractApiError(err))
  }
}

async function send() {
  if (!canSend.value) return
  const text = draft.value.trim()
  sending.value = true
  error.value = ''
  try {
    const created = await chatApi.send(props.orderId, text)
    if (created && created.id) {
      messages.value.push(created)
    } else {
      const page = await chatApi.list(props.orderId, { limit: 20 })
      messages.value = page.items || []
    }
    draft.value = ''
    await scrollToBottom()
  } catch (err) {
    error.value = extractApiError(err)
  } finally {
    sending.value = false
  }
}

function startPolling() {
  stopPolling()
  pollTimer = setInterval(pollNew, POLL_MS)
}
function stopPolling() {
  if (pollTimer) { clearInterval(pollTimer); pollTimer = null }
}

onMounted(async () => {
  await loadMessages()
  startPolling()
})
onBeforeUnmount(stopPolling)

watch(() => props.orderId, async () => {
  messages.value = []
  hasMore.value = false
  nextBeforeId.value = null
  await loadMessages()
})
</script>

<style scoped>
.chat {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 400px;
  background: var(--color-surface);
  border: 2px solid var(--color-border);
  border-radius: 8px;
  overflow: hidden;
}
.chat__header {
  padding: 12px 16px;
  border-bottom: 1px solid var(--color-border);
}
.chat__title {
  margin: 0;
  font-size: 16px;
  color: var(--color-text);
}
.chat__messages {
  flex: 1;
  overflow-y: auto;
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  background: var(--color-bg);
}
.chat__load-more {
  align-self: center;
  padding: 4px 10px;
  font-size: 12px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 999px;
  cursor: pointer;
  color: var(--color-text-muted);
}
.chat__hint {
  text-align: center;
  color: var(--color-text-subtle);
  font-size: 13px;
  margin: 8px 0;
}
.chat__bubble {
  max-width: 80%;
  align-self: flex-start;
  background: var(--color-surface-hover);
  color: var(--color-text);
  padding: 8px 12px;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.chat__bubble--mine {
  align-self: flex-end;
  background: var(--color-primary);
  color: var(--color-on-primary);
}
.chat__text {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-size: 14px;
  line-height: 1.4;
}
.chat__time {
  font-size: 11px;
  opacity: 0.75;
  align-self: flex-end;
}
.chat__form {
  display: flex;
  gap: 8px;
  padding: 8px;
  border-top: 1px solid var(--color-border);
}
.chat__input {
  flex: 1;
  resize: none;
  border: 1px solid var(--color-border-strong);
  border-radius: 6px;
  padding: 8px 10px;
  font-family: inherit;
  font-size: 14px;
  color: var(--color-text);
  background: var(--color-surface);
  outline: none;
}
.chat__input:focus {
  border-color: var(--color-focus-ring);
}
.chat__send {
  width: 40px;
  border: none;
  border-radius: 6px;
  background: var(--color-primary);
  color: var(--color-on-primary);
  cursor: pointer;
  font-size: 16px;
  transition: background 0.15s;
}
.chat__send:hover:not(:disabled) { background: var(--color-primary-hover); }
.chat__send:disabled { opacity: 0.5; cursor: not-allowed; }
.chat__error {
  margin: 0;
  padding: 6px 12px;
  font-size: 13px;
  color: var(--color-danger);
  background: var(--color-danger-subtle);
}
</style>
