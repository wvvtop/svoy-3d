export function extractApiError(err) {
  const data = err?.response?.data
  if (!data) return err?.message || 'Не удалось выполнить операцию'
  if (typeof data === 'string') return data
  if (data.message) return data.message
  if (typeof data.detail === 'string') return data.detail
  if (data.detail?.message) return data.detail.message
  if (Array.isArray(data.detail)) {
    return data.detail.map((d) => d.msg || String(d)).join('; ')
  }
  return 'Не удалось выполнить операцию'
}
