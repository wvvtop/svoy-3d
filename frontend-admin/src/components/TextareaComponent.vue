<template>
  <textarea
    class="textarea"
    :value="modelValue"
    :placeholder="placeholder"
    :rows="rows"
    :required="required"
    :disabled="disabled"
    @input="handleInput"
    @change="handleChange"
  ></textarea>
</template>

<script setup>
defineProps({
  modelValue: String,
  placeholder: String,
  rows: {
    type: Number,
    default: 4,
  },
  required: Boolean,
  disabled: Boolean,
})

const emit = defineEmits(['update:modelValue', 'change'])

const handleInput = (event) => {
  emit('update:modelValue', event.target.value)
}

const handleChange = (event) => {
  emit('change', event.target.value)
}
</script>

<style scoped>
.textarea {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  font-size: 16px;
  font-family: inherit;
  box-sizing: border-box;
  transition: border-color 0.2s ease;
  resize: vertical;          /* ← можно растягивать ТОЛЬКО вниз */
  min-height: 80px;
  background: var(--color-surface);
  color: var(--color-text);
}

.textarea:focus {
  outline: none;
  border-color: var(--color-primary);
}

.textarea::placeholder {
  color: var(--color-text-subtle);
}

.textarea:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
