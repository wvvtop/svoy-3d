<template>
  <div
    class="spacer"
    :class="[`spacer--${size}`, `spacer--${axis}`]"
  ></div>
</template>

<script setup>
defineProps({
  size: {
    type: String,
    default: 'md',
    validator: (v) => ['xs', 'sm', 'md', 'lg', 'xl'].includes(v),
  },
  axis: {
    type: String,
    default: 'vertical',
    validator: (v) => ['vertical', 'horizontal'].includes(v),
  },
})
</script>

<style scoped>
.spacer {
  flex-shrink: 0;
}

/* Вертикальный — высота */
.spacer--vertical.spacer--xs { height: 4px; }
.spacer--vertical.spacer--sm { height: 8px; }
.spacer--vertical.spacer--md { height: 16px; }
.spacer--vertical.spacer--lg { height: 24px; }
.spacer--vertical.spacer--xl { height: 32px; }

/* Горизонтальный — ширина */
.spacer--horizontal.spacer--xs { width: 4px; }
.spacer--horizontal.spacer--sm { width: 8px; }
.spacer--horizontal.spacer--md { width: 16px; }
.spacer--horizontal.spacer--lg { width: 24px; }
.spacer--horizontal.spacer--xl { width: 32px; }
</style>
