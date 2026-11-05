const STATUS_MAP = {
  pending:   { label: 'Ожидает',    variant: 'warning' },
  paid:      { label: 'Оплачен',    variant: 'success' },
  shipped:   { label: 'Отправлен',  variant: 'primary' },
  delivered: { label: 'Доставлен',  variant: 'success' },
  cancelled: { label: 'Отменён',    variant: 'danger'  },
}

export const getStatus = (status) =>
  STATUS_MAP[status] ?? { label: status, variant: 'muted' }
