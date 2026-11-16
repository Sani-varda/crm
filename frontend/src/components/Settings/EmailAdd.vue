<template>
  <div class="flex flex-col h-full gap-4">
    <!-- title and desc -->
    <div role="heading" aria-level="1" class="flex flex-col gap-1">
      <h2 class="flex gap-2 text-2xl-semibold leading-none h-5 text-ink-gray-8">
        {{ __('Setup Email') }}
      </h2>
      <p class="text-p-base text-ink-gray-6">
        {{ __('Choose the email service provider you want to configure.') }}
      </p>
    </div>
    <!-- email service provider selection -->
    <div class="flex flex-wrap items-center">
      <div
        v-for="s in services"
        :key="s.name"
        class="flex flex-col items-center gap-1 mt-4 w-[75px]"
        @click="handleSelect(s)"
      >
        <EmailProviderIcon
          :label="s.label || s.name"
          :logo="s.icon"
          :selected="selectedService?.name === s?.name"
        />
      </div>
    </div>
    <div v-if="selectedService" class="flex flex-col gap-4">
      <!-- email service provider info -->
      <div
        class="flex items-center gap-2 p-2 rounded-5 ring-1 ring-outline-gray-3 text-ink-gray-6"
      >
        <CircleAlert class="w-5 h-6 w-min-5 w-max-5 min-h-5 max-w-5 shrink-0" />
        <div class="text-xs text-wrap">
          {{ selectedService.info }}
          <a :href="selectedService.link" target="_blank" class="underline">
            {{ __('here') }}
          </a>
          .
        </div>
      </div>

      <!-- Custom Provider Form -->
      <div v-if="isCustomProvider" class="flex flex-col gap-5">
        <!-- Account & Credentials -->
        <div class="flex flex-col gap-3">
          <h3 class="text-sm font-semibold text-ink-gray-8">
            {{ __('Account & Authentication') }}
          </h3>
          <div class="grid grid-cols-2 gap-4">
            <FormControl
              v-model="state.email_account_name"
              :label="__('Account Name')"
              type="text"
              :placeholder="__('Support / Sales / Admissions')"
            />
            <FormControl
              v-model="state.email_id"
              :label="__('Email Address')"
              type="email"
              placeholder="admissions@yourdomain.com"
            />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <FormControl
              v-model="state.password"
              :label="__('Password / App Password')"
              type="password"
              placeholder="********"
            />
            <div class="flex flex-col justify-center gap-1 pt-4">
              <FormControl
                v-model="state.login_id_is_different"
                :label="__('Use different login username')"
                type="checkbox"
              />
              <p class="text-ink-gray-4 text-p-sm">
                {{ __('Enable if your mailbox login username differs from the email address.') }}
              </p>
            </div>
          </div>
          <div v-if="state.login_id_is_different" class="grid grid-cols-2 gap-4">
            <FormControl
              v-model="state.login_id"
              :label="__('Login Username')"
              type="text"
              placeholder="username"
            />
          </div>
        </div>

        <!-- Incoming (IMAP) Settings -->
        <div class="flex flex-col gap-3 p-3.5 bg-surface-gray-1 border border-outline-gray-2 rounded-6">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-sm font-semibold text-ink-gray-8">
                {{ __('Incoming Mail (IMAP)') }}
              </h3>
              <p class="text-xs text-ink-gray-5">
                {{ __('Fetch and sync incoming emails to CRM contacts and leads.') }}
              </p>
            </div>
            <FormControl
              v-model="state.enable_incoming"
              :label="__('Enable Incoming')"
              type="checkbox"
            />
          </div>

          <div v-if="state.enable_incoming" class="flex flex-col gap-3 pt-2 border-t border-outline-gray-2">
            <div class="grid grid-cols-3 gap-3">
              <div class="col-span-2">
                <FormControl
                  v-model="state.email_server"
                  :label="__('IMAP Host / Server')"
                  type="text"
                  placeholder="imap.yourdomain.com"
                />
              </div>
              <FormControl
                v-model="state.incoming_port"
                :label="__('Port')"
                type="text"
                placeholder="993"
              />
            </div>
            <div class="grid grid-cols-2 gap-3">
              <FormControl
                v-model="state.use_ssl"
                :label="__('Use SSL (Port 993)')"
                type="checkbox"
                @update:model-value="onIncomingSslToggle"
              />
              <FormControl
                v-model="state.use_starttls"
                :label="__('Use STARTTLS (Port 143)')"
                type="checkbox"
                @update:model-value="onIncomingStarttlsToggle"
              />
            </div>
          </div>
        </div>

        <!-- Outgoing (SMTP) Settings -->
        <div class="flex flex-col gap-3 p-3.5 bg-surface-gray-1 border border-outline-gray-2 rounded-6">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-sm font-semibold text-ink-gray-8">
                {{ __('Outgoing Mail (SMTP)') }}
              </h3>
              <p class="text-xs text-ink-gray-5">
                {{ __('Send individual emails, replies, and notifications from CRM.') }}
              </p>
            </div>
            <FormControl
              v-model="state.enable_outgoing"
              :label="__('Enable Outgoing')"
              type="checkbox"
            />
          </div>

          <div v-if="state.enable_outgoing" class="flex flex-col gap-3 pt-2 border-t border-outline-gray-2">
            <div class="grid grid-cols-3 gap-3">
              <div class="col-span-2">
                <FormControl
                  v-model="state.smtp_server"
                  :label="__('SMTP Host / Server')"
                  type="text"
                  placeholder="smtp.yourdomain.com"
                />
              </div>
              <FormControl
                v-model="state.smtp_port"
                :label="__('Port')"
                type="text"
                placeholder="587"
              />
            </div>
            <div class="grid grid-cols-2 gap-3">
              <FormControl
                v-model="state.use_tls"
                :label="__('Use TLS / STARTTLS (Port 587)')"
                type="checkbox"
                @update:model-value="onOutgoingTlsToggle"
              />
              <FormControl
                v-model="state.use_ssl_for_outgoing"
                :label="__('Use SSL (Port 465)')"
                type="checkbox"
                @update:model-value="onOutgoingSslToggle"
              />
            </div>
          </div>
        </div>

        <!-- Routing & CRM Defaults -->
        <div class="flex flex-col gap-3">
          <h3 class="text-sm font-semibold text-ink-gray-8">
            {{ __('Routing & Defaults') }}
          </h3>
          <div class="grid grid-cols-2 gap-4">
            <div class="flex flex-col gap-1">
              <FormControl
                v-model="state.default_incoming"
                :label="__('Default Incoming')"
                type="checkbox"
              />
              <p class="text-ink-gray-4 text-p-sm">
                {{ __('Replies to company will route to this account.') }}
              </p>
            </div>
            <div class="flex flex-col gap-1">
              <FormControl
                v-model="state.default_outgoing"
                :label="__('Default Outgoing')"
                type="checkbox"
              />
              <p class="text-ink-gray-4 text-p-sm">
                {{ __('Outbound emails will be sent from this account by default.') }}
              </p>
            </div>
            <div v-if="state.enable_incoming" class="flex flex-col gap-1 col-span-2">
              <FormControl
                v-model="state.create_lead_from_incoming_email"
                :label="__('Create Lead from Incoming Emails')"
                type="checkbox"
              />
              <p class="text-ink-gray-4 text-p-sm">
                {{ __('Automatically creates a CRM Lead when an incoming email arrives from an unknown contact.') }}
              </p>
            </div>
          </div>
        </div>

        <ErrorMessage class="ml-1" :message="error" />
      </div>

      <!-- Preset Service Provider Form (Gmail, Outlook, Frappe Mail, etc.) -->
      <div v-else class="flex flex-col gap-4">
        <div class="grid grid-cols-1 gap-4">
          <div
            v-for="field in fields"
            :key="field.name"
            class="flex flex-col gap-1"
          >
            <FormControl
              v-model="state[field.name]"
              :label="field.label"
              :name="field.name"
              :type="field.type"
              :placeholder="field.placeholder"
            />
          </div>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <template v-for="field in incomingOutgoingFields" :key="field.name">
            <div
              v-if="field.condition ? field.condition(state) : true"
              class="flex flex-col gap-1"
            >
              <FormControl
                v-model="state[field.name]"
                :label="field.label"
                :name="field.name"
                :type="field.type"
              />
              <p class="text-ink-gray-4 text-p-sm">{{ field.description }}</p>
            </div>
          </template>
        </div>
        <ErrorMessage class="ml-1" :message="error" />
      </div>
    </div>
    <!-- action button -->
    <div v-if="selectedService" class="flex justify-between mt-auto">
      <Button
        :label="__('Back')"
        variant="outline"
        :disabled="addEmailRes.loading"
        @click="emit('update:step', 'email-list')"
      />
      <Button
        :label="__('Create')"
        variant="solid"
        :loading="addEmailRes.loading"
        @click="createEmailAccount"
      />
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { createResource, toast } from 'frappe-ui'
import { useTelemetry } from '@framework/ui/telemetry'
import { useCrmOnboarding } from '@/composables/onboarding'
import CircleAlert from '~icons/lucide/circle-alert'
import {
  customProviderFields,
  popularProviderFields,
  services,
  validateInputs,
  incomingOutgoingFields,
} from './emailConfig'
import EmailProviderIcon from './EmailProviderIcon.vue'

const emit = defineEmits(['update:step'])

const state = reactive({
  service: '',
  email_account_name: '',
  email_id: '',
  password: '',
  login_id_is_different: false,
  login_id: '',
  email_server: '',
  incoming_port: '993',
  use_ssl: true,
  use_starttls: false,
  smtp_server: '',
  smtp_port: '587',
  use_tls: true,
  use_ssl_for_outgoing: false,
  api_key: '',
  api_secret: '',
  frappe_mail_site: '',
  enable_incoming: true,
  enable_outgoing: true,
  default_incoming: false,
  default_outgoing: false,
  create_lead_from_incoming_email: false,
})
const { capture } = useTelemetry()
const { completeStep } = useCrmOnboarding()

const selectedService = ref(null)

const isFrappeMail = computed(
  () => selectedService.value?.name === 'Frappe Mail',
)
const isCustomProvider = computed(
  () =>
    selectedService.value?.name === 'Custom' ||
    Boolean(selectedService.value?.isCustomProvider),
)

const fields = computed(() => {
  if (isFrappeMail.value) {
    return customProviderFields
  }
  return popularProviderFields
})

function handleSelect(service) {
  selectedService.value = service
  state.service = service.name
  error.value = ''
  if (service.name === 'Custom' || service.isCustomProvider) {
    state.enable_incoming = true
    state.enable_outgoing = true
    state.incoming_port = '993'
    state.use_ssl = true
    state.use_starttls = false
    state.smtp_port = '587'
    state.use_tls = true
    state.use_ssl_for_outgoing = false
  }
}

function onIncomingSslToggle(val) {
  if (val) {
    state.use_starttls = false
    if (!state.incoming_port || state.incoming_port === '143') {
      state.incoming_port = '993'
    }
  }
}

function onIncomingStarttlsToggle(val) {
  if (val) {
    state.use_ssl = false
    if (!state.incoming_port || state.incoming_port === '993') {
      state.incoming_port = '143'
    }
  }
}

function onOutgoingTlsToggle(val) {
  if (val) {
    state.use_ssl_for_outgoing = false
    if (!state.smtp_port || state.smtp_port === '465') {
      state.smtp_port = '587'
    }
  }
}

function onOutgoingSslToggle(val) {
  if (val) {
    state.use_tls = false
    if (!state.smtp_port || state.smtp_port === '587') {
      state.smtp_port = '465'
    }
  }
}

const addEmailRes = createResource({
  url: 'crm.api.settings.create_email_account',
  makeParams: (val) => {
    return {
      ...val,
    }
  },
  onSuccess: () => {
    toast.success(__('Email account created successfully'))
    completeStep('connect_your_email')
    emit('update:step', 'email-list')
  },
  onError: (err) => {
    error.value =
      err?.messages?.[0] ||
      err?.message ||
      __('Failed to create email account: invalid credentials')
  },
})

const error = ref()
function createEmailAccount() {
  error.value = validateInputs(
    state,
    isCustomProvider.value
      ? 'custom'
      : isFrappeMail.value
        ? 'frappe_mail'
        : 'standard',
  )
  if (error.value) return

  addEmailRes.submit({ data: state })
  capture('email_account_created')
}
</script>

<style scoped></style>
