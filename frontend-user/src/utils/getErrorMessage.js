export const getErrorMessage = (err, fallback = 'Что-то пошло не так') => {
  const data = err.response?.data
  if (!data) return fallback

  // Вложенный формат: { error: { code, message } }
  if (data.error) {
    const e = data.error
    if (e.code === 'invalid_credentials') return 'Неверный email или пароль'
    if (typeof e.message === 'string') return e.message
    if (typeof e === 'string') return e
  }

  // Плоский формат: { code, message } — на будущее
  if (data.code === 'invalid_credentials') return 'Неверный email или пароль'
  if (typeof data.message === 'string') return data.message

  // FastAPI 422: { detail: [{ msg, loc }] }
  if (Array.isArray(data.detail)) {
    const emailErr = data.detail.find((d) => d.loc?.includes('email'))
    if (emailErr) return 'Введите корректный email'
    const passErr = data.detail.find((d) => d.loc?.includes('password'))
    if (passErr) return 'Пароль слишком короткий'
    return data.detail.map((d) => d.msg).join(', ')
  }
  if (typeof data.detail === 'string') return data.detail

  return fallback
}
