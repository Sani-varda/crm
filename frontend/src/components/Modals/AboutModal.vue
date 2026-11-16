<template>
  <Dialog v-model:open="show" :size="'sm'" bare>
    <template #default>
      <div class="p-4 pt-5">
        <div class="flex justify-center">
          <div class="flex flex-col items-center">
            <CRMLogo class="mb-3 size-12" />
            <Dialog.Title as-child>
              <h3 class="text-2xl-semibold text-ink-gray-9">Sensora</h3>
            </Dialog.Title>
            <p class="text-sm text-ink-gray-6 mt-1">Customer Relation Management · IDPS Borivali</p>
          </div>
        </div>
        <hr class="border-t my-3 mx-2" />
        <div>
          <a
            v-for="link in links"
            :key="link.label"
            class="flex py-2 px-2 hover:bg-surface-gray-1 rounded-4 cursor-pointer"
            target="_blank"
            :href="link.url"
          >
            <component
              :is="link.icon"
              v-if="link.icon"
              class="size-4 mr-2 text-ink-gray-7"
            />
            <span class="text-base text-ink-gray-8">
              {{ link.label }}
            </span>
          </a>
        </div>
        <hr class="border-t my-3 mx-2" />
        <p class="text-sm text-ink-gray-6 px-2 mt-2">
          © Sensora and contributors
        </p>
      </div>
    </template>
  </Dialog>
</template>
<script setup>
import CRMLogo from '@/components/Icons/CRMLogo.vue'
import LucideGlobe from '~icons/lucide/globe'
import LucideHeadset from '~icons/lucide/headset'
import { Dialog } from 'frappe-ui'

let show = defineModel({ type: Boolean })

let links = [
  {
    label: __('Website'),
    url: 'https://www.sensora.co.in',
    icon: LucideGlobe,
  },
  {
    label: __('Contact Support'),
    url: 'mailto:support@sensora.co.in',
    icon: LucideHeadset,
  },
]
</script>
