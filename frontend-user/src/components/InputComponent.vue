<template>
  <input
    v-model="model"
    class="input"
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
})

const emit = defineEmits(['change'])

const handleChange = (event) => {
  emit('change', event.target.value)
}
</script>

<style scoped>
.input {
  /* width: 100%; */
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
