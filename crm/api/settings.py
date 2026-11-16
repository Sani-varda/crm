import frappe
from frappe import _


@frappe.whitelist()
def create_email_account(data: dict):
	service = data.get("service")
	is_custom = (
		service in ("Custom", "Custom Provider", None, "") or service not in email_service_config
	)

	if not is_custom and service not in email_service_config:
		frappe.throw(_("Service not supported"))

	service_config = email_service_config.get(service, {})

	enable_incoming = bool(data.get("enable_incoming"))
	enable_outgoing = bool(data.get("enable_outgoing"))

	if not enable_incoming and not enable_outgoing:
		frappe.throw(_("Please enable at least Incoming or Outgoing email"))

	try:
		doc_dict = {
			"doctype": "Email Account",
			"email_id": data.get("email_id"),
			"email_account_name": data.get("email_account_name"),
			"service": "Custom" if is_custom else service,
			"enable_incoming": 1 if enable_incoming else 0,
			"enable_outgoing": 1 if enable_outgoing else 0,
			"default_incoming": 1 if data.get("default_incoming") else 0,
			"default_outgoing": 1 if data.get("default_outgoing") else 0,
			"create_lead_from_incoming_email": 1 if data.get("create_lead_from_incoming_email") else 0,
			"email_sync_option": "ALL",
			"initial_sync_count": 100,
			"create_contact": 1,
			"track_email_status": 1,
			"use_tls": 1,
			"use_imap": 1,
			"smtp_port": 587,
			**service_config,
		}

		if is_custom:
			incoming_port = data.get("incoming_port")
			smtp_port = data.get("smtp_port")
			doc_dict.update(
				{
					"email_server": data.get("email_server"),
					"incoming_port": int(incoming_port) if incoming_port else (993 if data.get("use_ssl", True) else 143),
					"use_ssl": 1 if data.get("use_ssl", True) else 0,
					"use_starttls": 1 if data.get("use_starttls") else 0,
					"use_imap": 1 if data.get("use_imap", True) else 0,
					"smtp_server": data.get("smtp_server"),
					"smtp_port": int(smtp_port) if smtp_port else (465 if data.get("use_ssl_for_outgoing") else 587),
					"use_tls": 1 if data.get("use_tls", True) else 0,
					"use_ssl_for_outgoing": 1 if data.get("use_ssl_for_outgoing") else 0,
					"login_id_is_different": 1 if data.get("login_id_is_different") else 0,
					"login_id": data.get("login_id") if data.get("login_id_is_different") else None,
				}
			)

		email_doc = frappe.get_doc(doc_dict)

		if service == "Frappe Mail":
			email_doc.api_key = data.get("api_key")
			email_doc.api_secret = data.get("api_secret")
			email_doc.frappe_mail_site = data.get("frappe_mail_site")
			email_doc.append_to = "CRM Lead"
		else:
			if enable_incoming:
				email_doc.append("imap_folder", {"append_to": "CRM Lead", "folder_name": "INBOX"})
			email_doc.password = data.get("password")
			# validate whether the credentials are correct
			if enable_incoming and email_doc.email_server and not frappe.local.flags.in_test:
				email_doc.get_incoming_server()

		# if correct credentials, save the email account
		email_doc.save()
		return email_doc.as_dict()
	except Exception as e:
		frappe.throw(str(e))


email_service_config = {
	"Frappe Mail": {
		"domain": None,
		"password": None,
		"awaiting_password": 0,
		"ascii_encode_password": 0,
		"login_id_is_different": 0,
		"login_id": None,
		"use_imap": 0,
		"use_ssl": 0,
		"validate_ssl_certificate": 0,
		"use_starttls": 0,
		"email_server": None,
		"incoming_port": 0,
		"always_use_account_email_id_as_sender": 1,
		"use_tls": 0,
		"use_ssl_for_outgoing": 0,
		"smtp_server": None,
		"smtp_port": None,
		"no_smtp_authentication": 0,
	},
	"GMail": {
		"email_server": "imap.gmail.com",
		"use_ssl": 1,
		"smtp_server": "smtp.gmail.com",
	},
	"Outlook": {
		"email_server": "imap-mail.outlook.com",
		"use_ssl": 1,
		"smtp_server": "smtp-mail.outlook.com",
	},
	"Sendgrid": {
		"smtp_server": "smtp.sendgrid.net",
		"smtp_port": 587,
	},
	"SparkPost": {
		"smtp_server": "smtp.sparkpostmail.com",
	},
	"Yahoo": {
		"email_server": "imap.mail.yahoo.com",
		"use_ssl": 1,
		"smtp_server": "smtp.mail.yahoo.com",
		"smtp_port": 587,
	},
	"Yandex": {
		"email_server": "imap.yandex.com",
		"use_ssl": 1,
		"smtp_server": "smtp.yandex.com",
		"smtp_port": 587,
	},
}
