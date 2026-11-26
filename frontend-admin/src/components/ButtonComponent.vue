<template>
  <button
    class="button"
    :class="[
      `button--${variant}`,
      `button--${size}`,
    ]"
    :type="type"
    :disabled="disabled"
    @click="clickButton"
  >
    <slot>{{ text }}</slot>
  </button>
</template>

<script setup>
const props = defineProps({
  text: String,
  type: {
    type: String,
    default: 'button',
  },
  variant: {
    type: String,
    default: 'primary',
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value),
  },
  disabled: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['action'])

const clickButton = () => {
  if (!props.disabled) {
    emit('action')
  }
}
</script>

<style scoped>
.button--delete {
  color: var(--color-on-danger);
  background: var(--color-danger);
}

.button--delete:hover {
  background: var(--color-warning-hover);
}

.button--add-small {
  background: #f1f5f9;
  color: #475569;
  border: none;
  padding: 10px 16px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  margin-top: 6px;
  transition: all 0.2s;
}

.button--add-small:hover {
  background: #e0f2fe;
  color: var(--color-primary-blue);
}

.button {
  text-decoration: none;
  font-size: 16px;
  font-weight: 500;
  padding: 10px 20px;
  border-radius: 6px;
  transition: all 0.3s ease;
  display: inline-block;
  border: 0;
}

.button--circle {
  padding: 10px 10px;
  border-radius: 999px;
  padding: 10px 15px;
  cursor: pointer;
}

.button--circle-delete {
  background-color: var(--color-danger);
  line-height: 0.8;
  color: var(--color-on-danger);
  padding: 10px 10px;
  border-radius: 999px;
  padding: 15px 15px;
  cursor: pointer;
}

.button--circle-delete:hover {
  background: var(--color-warning-hover);
}

.button--circle-restore {
  background-color: var(--color-success);
  line-height: 0.8;
  color: var(--color-on-success);
  border-radius: 999px;
  padding: 15px 15px;
  cursor: pointer;
}

.button--circle-close {
  background-color: var(--color-surface);
  color: var(--color-text);
  line-height: 0.8;
  padding: 15px 15px;
  border-radius: 999px;
  cursor: pointer;
  line-height: 1;
}

.button--circle-close:hover {
  background-color: var(--color-surface-hover);
}

.button--circle-restore:hover {
  background: var(--color-success-hover);
}

/* .button:hover {
  transform: translateY(-1.3px);
} */

.button--primary:hover {
  background-color: var(--color-primary-hover);
}

.button--primary {
  color: var(--color-on-primary);
  background-color: var(--color-primary);
}

.button {
  font-family: inherit;
  box-sizing: border-box;
  cursor: pointer;
}

/* Нейтральная кнопка */
.button--secondary {
  color: var(--color-text);
  background-color: var(--color-surface);
  box-shadow: inset 0 0 0 1px var(--color-border);
}

.button--secondary:hover:not(:disabled) {
  background-color: var(--color-surface-hover);
  box-shadow: inset 0 0 0 1px var(--color-border-strong);
}

/* Компактная кнопка */
.button--sm {
  padding: 8px 12px;
  font-size: 14px;
}

/* Большая кнопка */
.button--lg {
  padding: 12px 24px;
  font-size: 18px;
}

/* Заблокированная кнопка */
.button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
}
</style>
