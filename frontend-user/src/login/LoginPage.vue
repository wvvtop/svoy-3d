<template>
  <PageLayout>
    <template #page__content_item>
      <div class="form_wrapper">
        <AuthorizationForm />
      </div>

    </template>
  </PageLayout>
</template>

<script setup>
import PageLayout from '@/layouts/PageLayout.vue';
import AuthorizationForm from './AuthorizationForm.vue';

</script>

<style scoped>
.form_wrapper {
  display: flex;
  justify-content: center;
}
</style>
