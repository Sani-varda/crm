import { validateEmail } from '../../utils'

import LogoGmail from '@/images/gmail.png'
import LogoOutlook from '@/images/outlook.png'
import LogoSendgrid from '@/images/sendgrid.png'
import LogoSparkpost from '@/images/sparkpost.webp'
import LogoYahoo from '@/images/yahoo.png'
import LogoYandex from '@/images/yandex.png'
import LogoFrappeMail from '@/images/frappe-mail.svg'
import LogoCustom from '@/images/custom-email.svg'

const fixedFields = [
  {
    label: __('Account Name'),
    name: 'email_account_name',
    type: 'text',
    placeholder: __('Support / Sales'),
  },
  {
    label: __('Email ID'),
    name: 'email_id',
    type: 'email',
    placeholder: 'johndoe@example.com',
  },
]

export const incomingOutgoingFields = [
  {
    label: __('Enable Incoming'),
    name: 'enable_incoming',
    type: 'checkbox',
    description: __('If enabled, emails will be pulled from this account.'),
  },
  {
    label: __('Enable Outgoing'),
    name: 'enable_outgoing',
    type: 'checkbox',
    description: __(
      'If enabled, outgoing emails can be sent from this account.',
    ),
  },
  {
    label: __('Default Incoming'),
    name: 'default_incoming',
    type: 'checkbox',
    description: __(
      'If enabled, all replies to your company (eg: replies@yourcompany.com) will come to this account. Note: Only one account can be default incoming.',
    ),
  },
  {
    label: __('Default Outgoing'),
    name: 'default_outgoing',
    type: 'checkbox',
    description: __(
      'If enabled, all outgoing emails will be sent from this account. Note: Only one account can be default outgoing.',
    ),
  },
  {
    label: __('Create Lead from Incoming Emails'),
    name: 'create_lead_from_incoming_email',
    type: 'checkbox',
    description: __(
      'If enabled, a lead will be automatically created when an incoming email is received from an unknown contact.',
    ),
    condition: (state) => state.enable_incoming,
  },
]

export const popularProviderFields = [
  ...fixedFields,
  {
    label: __('Password'),
    name: 'password',
    type: 'password',
    placeholder: '********',
  },
]

export const customProviderFields = [
  ...fixedFields,
  {
    label: __('Frappe Mail Site'),
    name: 'frappe_mail_site',
    type: 'text',
    placeholder: 'https://frappemail.com',
  },
  {
    label: __('API Key'),
    name: 'api_key',
    type: 'text',
    placeholder: '********',
  },
  {
    label: __('API Secret'),
    name: 'api_secret',
    type: 'password',
    placeholder: '********',
  },
]

export const customAccountFields = [
  ...fixedFields,
  {
    label: __('Password'),
    name: 'password',
    type: 'password',
    placeholder: '********',
  },
  {
    label: __('Use different login ID'),
    name: 'login_id_is_different',
    type: 'checkbox',
    description: __(
      'Enable if your mailbox username is different from your email address.',
    ),
  },
  {
    label: __('Login ID'),
    name: 'login_id',
    type: 'text',
    placeholder: 'username',
    condition: (state) => state.login_id_is_different,
  },
]

export const customIncomingFields = [
  {
    label: __('Incoming IMAP Server'),
    name: 'email_server',
    type: 'text',
    placeholder: 'imap.example.com',
    condition: (state) => state.enable_incoming,
  },
  {
    label: __('IMAP Port'),
    name: 'incoming_port',
    type: 'text',
    placeholder: '993',
    condition: (state) => state.enable_incoming,
  },
  {
    label: __('Use SSL for Incoming'),
    name: 'use_ssl',
    type: 'checkbox',
    description: __('Recommended SSL/TLS port 993.'),
    condition: (state) => state.enable_incoming,
  },
  {
    label: __('Use STARTTLS for Incoming'),
    name: 'use_starttls',
    type: 'checkbox',
    description: __('For port 143.'),
    condition: (state) => state.enable_incoming && !state.use_ssl,
  },
]

export const customOutgoingFields = [
  {
    label: __('Outgoing SMTP Server'),
    name: 'smtp_server',
    type: 'text',
    placeholder: 'smtp.example.com',
    condition: (state) => state.enable_outgoing,
  },
  {
    label: __('SMTP Port'),
    name: 'smtp_port',
    type: 'text',
    placeholder: '587',
    condition: (state) => state.enable_outgoing,
  },
  {
    label: __('Use TLS for Outgoing'),
    name: 'use_tls',
    type: 'checkbox',
    description: __('STARTTLS on port 587 (recommended).'),
    condition: (state) => state.enable_outgoing,
  },
  {
    label: __('Use SSL for Outgoing'),
    name: 'use_ssl_for_outgoing',
    type: 'checkbox',
    description: __('Direct SSL on port 465.'),
    condition: (state) => state.enable_outgoing && !state.use_tls,
  },
]

export const services = [
  {
    name: 'GMail',
    label: 'Gmail',
    icon: LogoGmail,
    info: __(
      'Setting up GMail requires you to enable two factor authentication and app specific passwords. Read more',
    ),
    link: 'https://support.google.com/accounts/answer/185833',
    custom: false,
  },
  {
    name: 'Outlook',
    icon: LogoOutlook,
    info: __(
      'Setting up Outlook requires you to enable two factor authentication and app specific passwords. Read more',
    ),
    link: 'https://support.microsoft.com/en-us/account-billing/how-to-get-and-use-app-passwords-5896ed9b-4263-e681-128a-a6f2979a7944',
    custom: false,
  },
  {
    name: 'Custom',
    label: 'Custom',
    icon: LogoCustom,
    info: __(
      'Configure custom IMAP and SMTP email servers with your own domain and credentials. Read more',
    ),
    link: 'https://docs.erpnext.com/docs/user/manual/en/email-account',
    custom: false,
    isCustomProvider: true,
  },
  {
    name: 'Sendgrid',
    icon: LogoSendgrid,
    info: __(
      'Setting up Sendgrid requires you to enable two factor authentication and app specific passwords. Read more',
    ),
    link: 'https://sendgrid.com/docs/ui/account-and-settings/two-factor-authentication/',
    custom: false,
  },
  {
    name: 'SparkPost',
    icon: LogoSparkpost,
    info: __(
      'Setting up Sparkpost requires you to enable two factor authentication and app specific passwords. Read more',
    ),
    link: 'https://support.sparkpost.com/docs/my-account-and-profile/enabling-two-factor-authentication',
    custom: false,
  },
  {
    name: 'Yahoo',
    icon: LogoYahoo,
    info: __(
      'Setting up Yahoo requires you to enable two factor authentication and app specific passwords. Read more',
    ),
    link: 'https://help.yahoo.com/kb/SLN15241.html',
    custom: false,
  },
  {
    name: 'Yandex',
    icon: LogoYandex,
    info: __(
      'Setting up Yandex requires you to enable two factor authentication and app specific passwords. Read more',
    ),
    link: 'https://yandex.com/support/id/authorization/app-passwords.html',
    custom: false,
  },
  {
    name: 'Frappe Mail',
    icon: LogoFrappeMail,
    info: __(
      'Setting up Frappe Mail requires you to have an API key and API secret for your email account. Read more',
    ),
    link: 'https://github.com/frappe/mail',
    custom: true,
  },
]

export const emailIcon = {
  GMail: LogoGmail,
  Outlook: LogoOutlook,
  Sendgrid: LogoSendgrid,
  SparkPost: LogoSparkpost,
  Yahoo: LogoYahoo,
  Yandex: LogoYandex,
  'Frappe Mail': LogoFrappeMail,
  Custom: LogoCustom,
  'Custom Provider': LogoCustom,
  '': LogoCustom,
}

export function validateInputs(state, isCustomOrService, isEdit = false) {
  if (!state.email_account_name) {
    return __('Account name is required')
  }
  if (!state.email_id) {
    return __('Email ID is required')
  }
  const validEmail = validateEmail(state.email_id)
  if (!validEmail) {
    return __('Invalid email ID')
  }

  const isFrappeMail =
    isCustomOrService === true ||
    isCustomOrService === 'Frappe Mail' ||
    state.service === 'Frappe Mail'

  const isCustom =
    isCustomOrService === 'Custom' ||
    isCustomOrService === 'custom' ||
    state.service === 'Custom' ||
    (!isFrappeMail && !services.some((s) => s.name === state.service && !s.isCustomProvider))

  if (isFrappeMail) {
    if (!state.api_key) {
      return __('API key is required')
    }
    if (!state.api_secret) {
      return __('API secret is required')
    }
    return ''
  }

  if (!isEdit && !state.password) {
    return __('Password is required')
  }

  if (isCustom) {
    if (!state.enable_incoming && !state.enable_outgoing) {
      return __('Please enable at least Incoming or Outgoing email')
    }
    if (state.enable_incoming && !state.email_server) {
      return __('Incoming IMAP Server is required')
    }
    if (state.enable_outgoing && !state.smtp_server) {
      return __('Outgoing SMTP Server is required')
    }
    if (state.login_id_is_different && !state.login_id) {
      return __('Login ID is required when using a different login ID')
    }
  }

  return ''
}
