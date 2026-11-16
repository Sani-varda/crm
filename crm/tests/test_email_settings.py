import frappe
from frappe.tests.utils import FrappeTestCase
from crm.api.settings import create_email_account


class TestEmailSettings(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_create_custom_email_account(self):
		frappe.local.flags.in_test = True
		data = {
			"service": "Custom",
			"email_account_name": "_Test Custom Provider Account",
			"email_id": "test_custom_settings@sensora.co.in",
			"password": "secret_password",
			"enable_incoming": True,
			"email_server": "imap.sensora.co.in",
			"incoming_port": 993,
			"use_ssl": True,
			"enable_outgoing": True,
			"smtp_server": "smtp.sensora.co.in",
			"smtp_port": 587,
			"use_tls": True,
			"default_incoming": True,
			"default_outgoing": True,
			"create_lead_from_incoming_email": True,
		}
		result = create_email_account(data)
		self.assertEqual(result["service"], "Custom")
		self.assertEqual(result["email_account_name"], "_Test Custom Provider Account")

		doc = frappe.get_doc("Email Account", result["name"])
		self.assertEqual(doc.email_server, "imap.sensora.co.in")
		self.assertEqual(int(doc.incoming_port), 993)
		self.assertEqual(doc.use_ssl, 1)
		self.assertEqual(doc.smtp_server, "smtp.sensora.co.in")
		self.assertEqual(int(doc.smtp_port), 587)
		self.assertEqual(doc.use_tls, 1)
		self.assertEqual(doc.default_incoming, 1)
		self.assertEqual(doc.default_outgoing, 1)
		self.assertEqual(doc.create_lead_from_incoming_email, 1)

	def test_create_custom_email_account_requires_incoming_or_outgoing(self):
		data = {
			"service": "Custom",
			"email_account_name": "_Test Custom Provider Invalid",
			"email_id": "invalid@sensora.co.in",
			"password": "secret_password",
			"enable_incoming": False,
			"enable_outgoing": False,
		}
		with self.assertRaises(frappe.ValidationError):
			create_email_account(data)
