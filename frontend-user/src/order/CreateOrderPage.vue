<script setup>
import PageLayout from '@/layouts/PageLayout.vue';
import CreateOrderForm from './CreateOrderForm.vue';

</script>

<template>
  <PageLayout>
    <template #page__content_item>
      <div class="form_wrapper">
        <CreateOrderForm />
      </div>
    </template>
  </PageLayout>
</template>

<style scoped>
.form_wrapper {
  display: flex;
  justify-content: center;
}
</style>
