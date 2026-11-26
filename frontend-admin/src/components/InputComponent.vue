<template>
  <input
    v-model="model"
    class="input"
    :class="`input--${size}`"
    :type="type"
    :placeholder="placeholder"
    :required="required"
    :disabled="disabled"
    @change="handleChange"
  />
</template>

<script setup>
const model = defineModel({ type: String })

defineProps({
  type: {
    type: String,
    default: 'text',
  },
  placeholder: String,
  required: Boolean,
  disabled: Boolean,
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value),
  },
})

const emit = defineEmits(['change'])

const handleChange = (event) => {
  emit('change', event.target.value)
}
</script>

<style scoped>
.input {
  padding: 12px 14px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  font-size: 16px;
  font-family: inherit;
  box-sizing: border-box;
  transition: border-color 0.2s ease, background 0.2s ease;
  background: var(--color-surface);
  color: var(--color-text);
}

.input--sm {
  padding: 8px 12px;
  font-size: 14px;
}

.input--lg {
  padding: 14px 16px;
  font-size: 18px;
}

.input::placeholder {
  color: var(--color-text-subtle);
}

.input:hover:not(:disabled) {
  border-color: var(--color-border-strong);
}

.input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-subtle);
}

.input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
