import { describe, expect, it } from 'vitest'
import {
  services,
  emailIcon,
  validateInputs,
  customAccountFields,
  customIncomingFields,
  customOutgoingFields,
} from '@/components/Settings/emailConfig'

describe('emailConfig', () => {
  it('includes Custom provider in services list', () => {
    const customService = services.find((s) => s.name === 'Custom')
    expect(customService).toBeDefined()
    expect(customService.label).toBe('Custom')
    expect(customService.isCustomProvider).toBe(true)
  })

  it('provides icon mapping for Custom and empty fallback', () => {
    expect(emailIcon.Custom).toBeDefined()
    expect(emailIcon['']).toBeDefined()
    expect(emailIcon['Custom Provider']).toBeDefined()
  })

  it('defines custom account, incoming, and outgoing fields', () => {
    expect(customAccountFields.some((f) => f.name === 'login_id_is_different')).toBe(true)
    expect(customIncomingFields.some((f) => f.name === 'email_server')).toBe(true)
    expect(customIncomingFields.some((f) => f.name === 'incoming_port')).toBe(true)
    expect(customOutgoingFields.some((f) => f.name === 'smtp_server')).toBe(true)
    expect(customOutgoingFields.some((f) => f.name === 'smtp_port')).toBe(true)
  })

  describe('validateInputs', () => {
    it('validates required email account name and valid email id', () => {
      expect(validateInputs({ email_account_name: '', email_id: 'test@example.com' }, 'custom')).toBe(
        'Account name is required',
      )
      expect(validateInputs({ email_account_name: 'Work', email_id: '' }, 'custom')).toBe(
        'Email ID is required',
      )
      expect(validateInputs({ email_account_name: 'Work', email_id: 'invalid-email' }, 'custom')).toBe(
        'Invalid email ID',
      )
    })

    it('requires password for standard providers on creation', () => {
      const state = {
        email_account_name: 'Work',
        email_id: 'work@gmail.com',
        password: '',
      }
      expect(validateInputs(state, 'GMail')).toBe('Password is required')
    })

    it('requires API key and secret for Frappe Mail', () => {
      const state = {
        email_account_name: 'Work',
        email_id: 'work@domain.com',
        api_key: '',
        api_secret: '',
      }
      expect(validateInputs(state, 'Frappe Mail')).toBe('API key is required')

      state.api_key = 'some_key'
      expect(validateInputs(state, 'Frappe Mail')).toBe('API secret is required')

      state.api_secret = 'some_secret'
      expect(validateInputs(state, 'Frappe Mail')).toBe('')
    })

    it('requires at least incoming or outgoing enabled for custom provider', () => {
      const state = {
        email_account_name: 'Support',
        email_id: 'support@idpsborivali.com',
        password: 'password123',
        enable_incoming: false,
        enable_outgoing: false,
      }
      expect(validateInputs(state, 'custom')).toBe(
        'Please enable at least Incoming or Outgoing email',
      )
    })

    it('validates server host requirements when incoming/outgoing are enabled', () => {
      const state = {
        email_account_name: 'Support',
        email_id: 'support@idpsborivali.com',
        password: 'password123',
        enable_incoming: true,
        email_server: '',
        enable_outgoing: false,
      }
      expect(validateInputs(state, 'custom')).toBe('Incoming IMAP Server is required')

      state.email_server = 'imap.idpsborivali.com'
      state.enable_outgoing = true
      state.smtp_server = ''
      expect(validateInputs(state, 'custom')).toBe('Outgoing SMTP Server is required')

      state.smtp_server = 'smtp.idpsborivali.com'
      expect(validateInputs(state, 'custom')).toBe('')
    })

    it('validates login ID when login_id_is_different is true', () => {
      const state = {
        email_account_name: 'Support',
        email_id: 'support@idpsborivali.com',
        password: 'password123',
        enable_incoming: true,
        email_server: 'imap.idpsborivali.com',
        enable_outgoing: true,
        smtp_server: 'smtp.idpsborivali.com',
        login_id_is_different: true,
        login_id: '',
      }
      expect(validateInputs(state, 'custom')).toBe(
        'Login ID is required when using a different login ID',
      )

      state.login_id = 'idps_support'
      expect(validateInputs(state, 'custom')).toBe('')
    })

    it('does not require password when editing existing accounts', () => {
      const state = {
        email_account_name: 'Support',
        email_id: 'support@idpsborivali.com',
        password: '',
        enable_incoming: true,
        email_server: 'imap.idpsborivali.com',
        enable_outgoing: true,
        smtp_server: 'smtp.idpsborivali.com',
      }
      expect(validateInputs(state, 'custom', true)).toBe('')
    })
  })
})
