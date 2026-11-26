<template>
  <select
    v-model="model"
    class="select"
    :class="`select--${size}`"
    :disabled="disabled"
    :required="required"
    @change="handleChange"
  >
    <option
      v-if="placeholder"
      value=""
      disabled
    >
      {{ placeholder }}
    </option>

    <option
      v-for="option in options"
      :key="option.value"
      :value="option.value"
      :disabled="option.disabled"
    >
      {{ option.label }}
    </option>
  </select>
</template>

<script setup>
// Поддерживаем строковые и числовые значения.
const model = defineModel({
  type: [String, Number],
})

defineProps({
  options: {
    type: Array,
    default: () => [],
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

const handleChange = () => {
  emit('change', model.value)
}
</script>

<style scoped>
.select {
  padding: 12px 14px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  font-size: 16px;
  font-family: inherit;
  box-sizing: border-box;
  background-color: var(--color-surface);
  color: var(--color-text);
  cursor: pointer;
  transition: border-color 0.2s ease, background 0.2s ease;
}

.select--sm {
  padding: 8px 12px;
  font-size: 14px;
}

.select--lg {
  padding: 14px 16px;
  font-size: 18px;
}

.select:hover:not(:disabled) {
  border-color: var(--color-border-strong);
}

.select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-subtle);
}

.select:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
