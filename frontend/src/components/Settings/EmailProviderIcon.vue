<template>
  <div
    class="flex items-center justify-center w-8 h-8 bg-surface-gray-2 cursor-pointer rounded-7 hover:bg-surface-gray-3"
    :class="{ 'ring-2 ring-outline-gray-4': selected }"
  >
    <img v-if="logo" :src="logo" class="w-4 h-4 object-contain" />
    <span v-else class="text-xs font-semibold text-ink-gray-7">@</span>
  </div>
  <p v-if="label" class="text-xs text-center text-ink-gray-6 mt-2">
    {{ label }}
  </p>
</template>

<script setup>
defineProps({
  logo: { type: String, default: '' },
  label: { type: String, default: '' },
  selected: { type: Boolean, default: false },
})
</script>
