<script setup>
import BrandComponent from '@/components/BrandComponent.vue';
import NavbarCenterComponent from '@/navbar/NavbarCenterComponent.vue';
import NavbarRightComponent from '@/navbar/NavbarRightComponent.vue';
</script>

<template>
  <div class="page">
    <nav class="page__navbar">
      <div class="page__navbar_left">
        <BrandComponent/>
      </div>

      <div class="page__navbar_center">
        <!-- <NavbarCenterLinks class="page__navbar_center-item" /> -->
          <NavbarCenterComponent />
          <!-- <NavbarCenterComponent /> -->
      </div>

      <div class="page__navbar_right">
        <!-- <slot class="page__navbar_right-item" name="page__navbar_right"></slot> -->
        <NavbarRightComponent />
      </div>
    </nav>

    <main class="page__content">
      <slot name="page__content_item"></slot>
    </main>
  </div>
</template>

<style scoped>
.page__navbar_left {
  display: flex;
  justify-content: flex-start;
  align-items: center;
}

.page__navbar_center {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 40px;
}

.page__navbar {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  background-color: var(--color-header-bg);
  padding: 15px;
  border-radius: 0 0 8px 8px;
  /* margin-bottom: 20px; */
}

.page__navbar_right {
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.page__content {
  padding: 20px;
}
</style>
