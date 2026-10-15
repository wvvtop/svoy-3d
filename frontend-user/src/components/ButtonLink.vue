<template>
  <router-link :to="link" class="button__link" :class="`button__link--${variant}`">
    {{ text }}
  </router-link>
</template>

<script setup>
defineProps({
  link: String,
  text: String,
  variant: {
    type: String,
    default: 'primary'
  }
})
</script>

<style scoped>
/* ============ Базовый: только общее ============ */
.button__link {
  display: inline-block;
  font-size: 16px;
  font-weight: 500;
  padding: 10px 20px;
  border-radius: 6px;
  border: 1px solid transparent;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

/* ============ nav — текущий стиль navbar ============ */
.button__link--nav {
  color: var(--color-text);
  background-color: var(--color-surface);
}

.button__link--nav:hover {
  background-color: var(--color-surface-hover);
  transform: translateY(-2px);
}

/* ============ primary — акцентная кнопка ============ */
.button__link--primary {
  color: var(--color-on-primary);
  background-color: var(--color-primary);
}

.button__link--primary:hover {
  background-color: var(--color-primary-hover);
  transform: translateY(-2px);
}

.orders__header-side .orders__nav-link.router-link-active {
  background: var(--color-primary-active);
}

/* ============ secondary — если понадобится ============ */
.button__link--secondary {
  color: var(--color-text);
  background-color: var(--color-surface);
  border-color: var(--color-border);
}

.button__link--secondary:hover {
  background-color: var(--color-surface-hover);
  border-color: var(--color-border-strong);
}

/* ============ danger — если понадобится ============ */
.button__link--danger {
  color: var(--color-danger);
  background-color: var(--color-danger-subtle);
}

.button__link--danger:hover {
  background-color: var(--color-danger);
  color: var(--color-on-danger);
}
</style>
