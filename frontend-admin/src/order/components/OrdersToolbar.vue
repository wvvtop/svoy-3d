<script setup>
import { reactive, watch } from 'vue'

import ButtonComponent from '@/components/ButtonComponent.vue'
import InputComponent from '@/components/InputComponent.vue'
import SelectComponent from '@/components/SelectComponent.vue'

import { useOrdersStore } from '../stores/orders.js'

const store = useOrdersStore()

// Варианты количества заказов.
const limitOptions = [
  { label: '10', value: 10 },
  { label: '20', value: 20 },
  { label: '50', value: 50 },
  { label: '100', value: 100 },
]

// Доступные поля сортировки.
const sortFieldOptions = [
  { label: 'Дата создания', value: 'created_at' },
  { label: 'ID заказа', value: 'id' },
]

// Направления сортировки.
const sortDirectionOptions = [
  { label: 'По убыванию', value: 'desc' },
  { label: 'По возрастанию', value: 'asc' },
]

// Черновик настроек до нажатия «Применить».
const draft = reactive({ ...store.settings })

// Синхронизируем поля при изменении настроек Store.
watch(
  () => store.settings,
  (value) => Object.assign(draft, value),
  { deep: true },
)

function apply() {
  store.applySettings({ ...draft })
}

function reset() {
  store.resetSettings()
  Object.assign(draft, store.settings)
}
</script>

<template>
  <form
    class="orders-toolbar"
    @submit.prevent="apply"
  >
    <label class="orders-toolbar__field">
      Поиск

      <InputComponent
        v-model="draft.search"
        type="search"
        placeholder="ID или пожелания"
        maxlength="200"
        size="sm"
      />
    </label>

    <label class="orders-toolbar__field">
      На странице

      <SelectComponent
        v-model="draft.limit"
        :options="limitOptions"
        size="sm"
      />
    </label>

    <label class="orders-toolbar__field">
      Сортировка

      <SelectComponent
        v-model="draft.sort_by"
        :options="sortFieldOptions"
        size="sm"
      />
    </label>

    <label class="orders-toolbar__field">
      Направление

      <SelectComponent
        v-model="draft.sort_dir"
        :options="sortDirectionOptions"
        size="sm"
      />
    </label>

    <div class="orders-toolbar__actions">
      <ButtonComponent
        text="Применить"
        type="submit"
        variant="primary"
        size="sm"
        :disabled="store.listLoading"
      />

      <ButtonComponent
        text="Сбросить"
        variant="secondary"
        size="sm"
        :disabled="store.listLoading"
        @action="reset"
      />
    </div>
  </form>
</template>

<style scoped>
.orders-toolbar {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: flex-end;
  gap: 12px;
  padding-bottom: 20px;
}

.orders-toolbar__field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  color: var(--color-text);
  font-size: 14px;
}

.orders-toolbar__actions {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
