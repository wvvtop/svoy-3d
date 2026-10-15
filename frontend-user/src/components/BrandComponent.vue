<template>
  <router-link to="/" class="brand_link">
    <div class="brand">
      <span class="brand__text">Свой3д</span>
    </div>
  </router-link>
</template>

<style scoped>
.brand {
  transition: all 0.07s ease;
}

.brand:hover {
  outline: 2px solid var(--color-header-border);
  outline-offset: 4px;
  border-radius: 3px;
}

.brand_link {
  text-decoration: none;
  /* убираем подчеркивание */
  color: inherit;
  /* наследуем цвет от родителя */
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
}

.brand__text {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: var(--color-header-text)
  /* color: #2c3e50; */
}
</style>

<script setup>
</script>
