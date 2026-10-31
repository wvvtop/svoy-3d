<script setup>
import PageLayout from '@/layouts/PageLayout.vue';
// import CreateOrderForm from './CreateOrderForm.vue';
import OrderForm from '@/components/order/OrderForm.vue';

</script>

<template>
  <PageLayout>
    <template #page__content_item>
      <div class="form_wrapper">
        <OrderForm />
        <!-- <CreateOrderForm /> -->
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
