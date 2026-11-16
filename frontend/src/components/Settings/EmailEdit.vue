<template>
  <div class="flex flex-col h-full gap-4">
    <!-- title and desc -->
    <div role="heading" aria-level="1" class="flex justify-between gap-1">
      <h2 class="flex gap-2 text-2xl-semibold leading-none h-5 text-ink-gray-8">
        {{ __('Edit Email') }}
      </h2>
    </div>
    <div class="w-fit">
      <EmailProviderIcon
        :logo="emailIcon[accountData.service] || emailIcon.Custom"
        :label="accountData.service || __('Custom Provider')"
      />
    </div>
    <!-- banner for setting up email account -->
    <div
      class="flex items-center gap-2 p-2 rounded-5 ring-1 ring-outline-gray-3"
    >
      <CircleAlert
        class="size-6 text-ink-gray-4 w-min-5 w-max-5 min-h-5 max-w-5 shrink-0"
      />
      <div class="text-xs text-ink-gray-6 text-wrap">
        {{ info.description }}
        <a :href="info.link" target="_blank" class="underline">
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
            :placeholder="__('Leave blank to keep unchanged')"
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

      <!-- Routing & Defaults -->
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

      <ErrorMessage v-if="error" class="ml-1" :message="error" />
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
      <ErrorMessage v-if="error" class="ml-1" :message="error" />
    </div>

    <!-- action buttons -->
    <div class="flex justify-between mt-auto pt-4 border-t border-outline-gray-2">
      <Button
        :label="__('Back')"
        theme="gray"
        variant="outline"
        :disabled="loading || deleting"
        @click="emit('update:step', 'email-list')"
      />
      <div class="flex items-center gap-2">
        <Button
          :label="__('Delete')"
          theme="red"
          variant="outline"
          :disabled="loading"
          :loading="deleting"
          @click="showDeleteDialog = true"
        />
        <Button
          :label="__('Update Account')"
          variant="solid"
          :loading="loading"
          @click="updateAccount"
        />
      </div>
    </div>

    <!-- Delete Confirmation Dialog -->
    <Dialog
      v-model:open="showDeleteDialog"
      :title="__('Delete Email Account')"
    >
      <template #default>
        <div class="flex flex-col gap-4">
          <p class="text-p-base text-ink-gray-7">
            {{ __('Are you sure you want to delete this email account? This action cannot be undone.') }}
          </p>
          <div class="flex justify-end gap-2">
            <Button
              :label="__('Cancel')"
              variant="outline"
              @click="showDeleteDialog = false"
            />
            <Button
              :label="__('Delete')"
              theme="red"
              variant="solid"
              :loading="deleting"
              @click="deleteAccount"
            />
          </div>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { call, toast, Dialog } from 'frappe-ui'
import EmailProviderIcon from './EmailProviderIcon.vue'
import {
  emailIcon,
  services,
  popularProviderFields,
  customProviderFields,
  validateInputs,
  incomingOutgoingFields,
} from './emailConfig'
import CircleAlert from '~icons/lucide/circle-alert'

const props = defineProps({
  accountData: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['update:step'])

const state = reactive({
  email_account_name: props.accountData.email_account_name || '',
  service: props.accountData.service || '',
  email_id: props.accountData.email_id || '',
  password: '',
  login_id_is_different: Boolean(props.accountData.login_id_is_different),
  login_id: props.accountData.login_id || '',
  email_server: props.accountData.email_server || '',
  incoming_port: props.accountData.incoming_port || '993',
  use_ssl: Boolean(props.accountData.use_ssl),
  use_starttls: Boolean(props.accountData.use_starttls),
  smtp_server: props.accountData.smtp_server || '',
  smtp_port: props.accountData.smtp_port || '587',
  use_tls: Boolean(props.accountData.use_tls),
  use_ssl_for_outgoing: Boolean(props.accountData.use_ssl_for_outgoing),
  api_key: props.accountData?.api_key || null,
  api_secret: props.accountData?.api_secret || null,
  frappe_mail_site: props.accountData?.frappe_mail_site || '',
  enable_incoming: Boolean(props.accountData.enable_incoming),
  enable_outgoing: Boolean(props.accountData.enable_outgoing),
  default_outgoing: Boolean(props.accountData.default_outgoing),
  default_incoming: Boolean(props.accountData.default_incoming),
  create_lead_from_incoming_email: Boolean(
    props.accountData.create_lead_from_incoming_email,
  ),
})

const info = {
  description: __('To know more about setting up email accounts, click'),
  link: 'https://docs.erpnext.com/docs/user/manual/en/email-account',
}

const isFrappeMail = computed(() => props.accountData.service === 'Frappe Mail')

const isCustomProvider = computed(() => {
  const s = props.accountData.service
  return (
    !s ||
    s === 'Custom' ||
    s === 'Custom Provider' ||
    !services.some((item) => item.name === s && !item.isCustomProvider)
  )
})

const fields = computed(() => {
  if (isFrappeMail.value) {
    return customProviderFields
  }
  return popularProviderFields
})

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

const error = ref()
const loading = ref(false)
const deleting = ref(false)
const showDeleteDialog = ref(false)

async function updateAccount() {
  error.value = validateInputs(
    state,
    isCustomProvider.value
      ? 'custom'
      : isFrappeMail.value
        ? 'frappe_mail'
        : 'standard',
    true,
  )
  if (error.value) return

  const old = { ...props.accountData }
  const updatedEmailAccount = { ...state }

  const nameChanged =
    old.email_account_name !== updatedEmailAccount.email_account_name
  delete old.email_account_name
  delete updatedEmailAccount.email_account_name

  if (!updatedEmailAccount.password) {
    delete updatedEmailAccount.password
  }

  const otherFieldsChanged = isDirty.value
  const values = updatedEmailAccount

  if (!nameChanged && !otherFieldsChanged) {
    toast.info(__('No changes made'))
    return
  }

  if (nameChanged) {
    try {
      loading.value = true
      await callRenameDoc()
      if (!otherFieldsChanged) {
        successHandler()
        return
      }
    } catch (e) {
      errorHandler(e)
      return
    }
  }
  if (otherFieldsChanged) {
    try {
      loading.value = true
      await callSetValue(values)
      successHandler()
    } catch (e) {
      errorHandler(e)
      return
    }
  }
}

const isDirty = computed(() => {
  return (
    state.email_id !== props.accountData.email_id ||
    Boolean(state.password) ||
    state.api_key !== props.accountData.api_key ||
    state.api_secret !== props.accountData.api_secret ||
    Boolean(state.enable_incoming) !== Boolean(props.accountData.enable_incoming) ||
    Boolean(state.enable_outgoing) !== Boolean(props.accountData.enable_outgoing) ||
    Boolean(state.default_outgoing) !== Boolean(props.accountData.default_outgoing) ||
    Boolean(state.default_incoming) !== Boolean(props.accountData.default_incoming) ||
    Boolean(state.create_lead_from_incoming_email) !==
      Boolean(props.accountData.create_lead_from_incoming_email) ||
    state.frappe_mail_site !== (props.accountData.frappe_mail_site || '') ||
    state.email_server !== (props.accountData.email_server || '') ||
    String(state.incoming_port) !== String(props.accountData.incoming_port || '') ||
    Boolean(state.use_ssl) !== Boolean(props.accountData.use_ssl) ||
    Boolean(state.use_starttls) !== Boolean(props.accountData.use_starttls) ||
    state.smtp_server !== (props.accountData.smtp_server || '') ||
    String(state.smtp_port) !== String(props.accountData.smtp_port || '') ||
    Boolean(state.use_tls) !== Boolean(props.accountData.use_tls) ||
    Boolean(state.use_ssl_for_outgoing) !==
      Boolean(props.accountData.use_ssl_for_outgoing) ||
    Boolean(state.login_id_is_different) !==
      Boolean(props.accountData.login_id_is_different) ||
    state.login_id !== (props.accountData.login_id || '')
  )
})

async function callRenameDoc() {
  const d = await call('frappe.client.rename_doc', {
    doctype: 'Email Account',
    old_name: props.accountData.email_account_name,
    new_name: state.email_account_name,
  })
  return d
}

async function callSetValue(values) {
  const d = await call('frappe.client.set_value', {
    doctype: 'Email Account',
    name: state.email_account_name || props.accountData.name,
    fieldname: values,
  })
  return d.name
}

async function deleteAccount() {
  try {
    deleting.value = true
    await call('frappe.client.delete_doc', {
      doctype: 'Email Account',
      name: props.accountData.name,
    })
    toast.success(__('Email account deleted successfully'))
    emit('update:step', 'email-list')
  } catch (e) {
    toast.error(e?.message || __('Failed to delete email account'))
  } finally {
    deleting.value = false
    showDeleteDialog.value = false
  }
}

function successHandler() {
  emit('update:step', 'email-list')
  toast.success(__('Email account updated successfully'))
}

function errorHandler(e) {
  loading.value = false
  error.value =
    e?.messages?.[0] ||
    e?.message ||
    __('Failed to update email account: invalid credentials')
}
</script>

<style scoped></style>
