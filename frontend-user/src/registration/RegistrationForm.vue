<script setup>
import ButtonComponent from '@/components/ButtonComponent.vue';
import InputComponent from '@/components/InputComponent.vue';
import { useAuthStore } from '@/stores/auth';
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const authStore = useAuthStore()
const router = useRouter()
const email = ref('');
const password = ref('');
const errorMsg = ref('')

const handleSubmit = async () => {
  try {
    await authStore.register(email.value, password.value)
    router.push('/')
  }
  catch {
    errorMsg.value = authStore.error
  }
}
</script>

<template>
  <form class="auth-form" @submit.prevent="handleSubmit">
    <h1>Регистрация</h1>

    <div>
      <span>Почта</span>
      <InputComponent type="email" v-model="email" />
    </div>
    <div>
      <span>Пароль</span>
      <InputComponent type="password" v-model="password" />
    </div>
    <div class="auth-form__error">
      {{ errorMsg }}
    </div>
    <div>
      <ButtonComponent text="Регистрация!" type="submit" />
    </div>

    <div class="auth-form__footer">
      <p class="auth-form__footer">
        Есть аккаунт?
        <a href="/login" class="auth-form__link">Войти!</a>
      </p>
    </div>
  </form>
</template>

<style scoped>
.auth-form {
  background-color: var(--color-surface);
  max-width: 600px;
  display: flex;
  flex-direction: column;
  text-align: center;
  gap: 10px;
  border: 2px solid var(--color-border);
  border-radius: 5px;
  padding: 20px;
}
.auth-form__error {
  font-size: 10px;
  color: var(--red-500)
}
.auth-form__footer {
  margin-top: 14px;
  text-align: center;
  font-size: 14px;
  color: var(--color-text-muted);   /* второстепенный текст */
}

.auth-form__link {
  color: var(--color-primary);
  text-decoration: none;
  font-weight: 500;
}

.auth-form__link:hover {
  text-decoration: underline;
}

.auth-form__link:focus-visible {
  outline: 2px solid var(--color-focus-ring);
  outline-offset: 2px;
  border-radius: 2px;
}
</style>
