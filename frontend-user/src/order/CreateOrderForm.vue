<template>
  <form class="order-form" @submit.prevent="handleSubmit">
    <h1>Создать заказ</h1>
    <SpacerComponent />
    <p class="order-form__description">
      Вам необоходимо загрузить фотографии с разных ракурсов которые указаны в форме,
      постарайтесь сделать фотографии перпендикулярно объекту
    </p>
    <SpacerComponent />
    <h2 class="order-form__requests">Ваши пожелания(можете оставить пустым)</h2>
    <TextAreaComponent v-model="order_request" :rows="8"
    placeholder="Ваши пожелания по заказу(можете оставить пустым)"/>

    <SpacerComponent/>
    <div class="order-form__images">
      <div style="width: 200px">
        <span>Фото спереди</span>
        <ImageUploader v-model="front_photo"/>
        <p v-if="errors.front" class="order-form__error">{{ errors.front }}</p>
      </div>
      <div style="width: 200px">
        <span>Фото сзади</span>
        <ImageUploader v-model="back_photo"/>
        <p v-if="errors.back" class="order-form__error">{{ errors.back }}</p>
      </div>
      <div style="width: 200px">
        <span>Фото слева</span>
        <ImageUploader v-model="left_photo"/>
        <p v-if="errors.left" class="order-form__error">{{ errors.left }}</p>
      </div>
    </div>
    <SpacerComponent />
    <ButtonComponent text="Создать!" type="submit"/>
  </form>
</template>

<script setup>
import { ordersApi } from '@/api/orders';
import ButtonComponent from '@/components/ButtonComponent.vue';
import ImageUploader from '@/components/ImageUploader.vue';
import SpacerComponent from '@/components/SpacerComponent.vue';
import TextAreaComponent from '@/components/TextareaComponent.vue';
import { ref, watch } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

const order_request = ref('');
const left_photo = ref(null);
const front_photo = ref(null);
const back_photo = ref(null);

const errors = ref({})
const submitting = ref(false)


function validate() {
  const e = {}
  if (!front_photo.value) e.front = 'Загрузите фото спереди'
  if (!back_photo.value)  e.back  = 'Загрузите фото сзади'
  if (!left_photo.value)  e.left  = 'Загрузите фото слева'
  errors.value = e
  return Object.keys(e).length === 0
}

// очищаем ошибку поля, как только фото появилось
watch(front_photo, (v) => { if (v) delete errors.value.front })
watch(back_photo,  (v) => { if (v) delete errors.value.back  })
watch(left_photo,  (v) => { if (v) delete errors.value.left  })

const handleSubmit = async () => {
  if (!validate()) return

  submitting.value = true
  try {
    const order = await ordersApi.create({
      front: front_photo.value,
      left:  left_photo.value,
      back:  back_photo.value,
    });

    console.log('Создан заказ:', order);

    front_photo.value = null;
    back_photo.value  = null;
    left_photo.value  = null;
    order_request.value = '';

    router.push({ name: "orders" })
  } catch (err) {
    alert(err.value)
    console.error(err);
  } finally {
    submitting.value = false;
  }
}
</script>

<style scoped>
.order-form__images {
  display: flex;
  flex-direction: column;
  gap: 15px;
  /* justify-content: center; */
  align-items: center;
}
.order-form {
  border: 2px solid var(--color-border);
  padding: 20px;
  max-width: 600px;
  background-color: var(--color-surface);
  border-radius: 5px;
}
.order-form__description {
  font-size: 16px;
  color: var(--color-text-muted);
}
.order-form__requests {
  color: var(--color-text-muted);
  font-size: 18px;
}
.order-form__error {
  font-size: 14px;
  color: var(--color-danger);
}
</style>
