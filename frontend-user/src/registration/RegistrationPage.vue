<template>
  <PageLayout>
    <template #page__content_item>
      <div class="form_wrapper">
        <RegistrationForm />
      </div>
    </template>
  </PageLayout>
</template>

<script setup>
import PageLayout from '@/layouts/PageLayout.vue';
import RegistrationForm from './RegistrationForm.vue';


</script>

<style scoped>
.form_wrapper {
  display: flex;
  justify-content: center;
}
</style>
