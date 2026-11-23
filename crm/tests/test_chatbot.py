# Copyright (c) 2026, Sensora and contributors
# For license information, please see license.txt

from unittest.mock import MagicMock, patch
import frappe
from frappe.tests.utils import FrappeTestCase
from crm.api.chatbot import (
    is_groq_bot_enabled,
    is_bot_paused,
    toggle_bot_pause,
    on_incoming_whatsapp_message,
    process_groq_reply,
    get_connection_details
)

class TestGroqChatbot(FrappeTestCase):
    def test_disabled_without_api_key(self):
        with patch("crm.api.chatbot.get_groq_api_key", return_value=None):
            self.assertFalse(is_groq_bot_enabled())

    def test_enabled_with_api_key(self):
        with patch("crm.api.chatbot.get_groq_api_key", return_value="gsk_mock_test_key"):
            self.assertTrue(is_groq_bot_enabled())

    def test_ignores_outgoing_messages(self):
        doc = MagicMock()
        doc.direction = "Outgoing"
        doc.message = "Hello from counselor"
        with patch("frappe.enqueue") as mock_enqueue:
            on_incoming_whatsapp_message(doc)
            mock_enqueue.assert_not_called()

    def test_enqueues_incoming_messages(self):
        doc = MagicMock()
        doc.direction = "Incoming"
        doc.name = "MSG-001"
        doc.message = "What are the school timings?"
        doc.to = "PROF-001"
        doc.whatsapp_account = "ACC-001"
        doc.reference_doctype = "CRM Lead"
        doc.reference_docname = "LEAD-001"
        doc.is_new.return_value = True

        with (
            patch("crm.api.chatbot.is_groq_bot_enabled", return_value=True),
            patch("crm.api.chatbot.is_bot_paused", return_value=False),
            patch("frappe.enqueue") as mock_enqueue
        ):
            on_incoming_whatsapp_message(doc)
            mock_enqueue.assert_called_once()
            args = mock_enqueue.call_args.kwargs
            self.assertEqual(args["message_body"], "What are the school timings?")
            self.assertEqual(args["account_name"], "ACC-001")

    def test_idempotent_ignores_saved_messages_without_body_change(self):
        doc = MagicMock()
        doc.direction = "Incoming"
        doc.message = "What are the school timings?"
        doc.is_new.return_value = False
        doc.has_value_changed.return_value = False

        with patch("frappe.enqueue") as mock_enqueue:
            on_incoming_whatsapp_message(doc)
            mock_enqueue.assert_not_called()

    @patch("requests.post")
    @patch("frappe.get_doc")
    def test_successful_groq_reply(self, mock_get_doc, mock_post):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "IDPS Borivali timings are 9:00 AM to 3:30 PM."}}]
        }
        mock_post.return_value = mock_resp

        mock_reply_doc = MagicMock()
        mock_get_doc.return_value = mock_reply_doc

        with (
            patch("crm.api.chatbot.get_groq_api_key", return_value="gsk_mock"),
            patch("crm.api.chatbot.is_bot_paused", return_value=False),
            patch("crm.api.chatbot._extract_and_update_lead_info") as mock_extract,
            patch("frappe.db.sql", return_value=[]),
            patch("frappe.get_all", return_value=[])
        ):
            process_groq_reply(
                docname="MSG-001",
                sender_profile="PROF-001",
                message_body="Timings?",
                account_name="ACC-001",
                reference_doctype="CRM Lead",
                reference_docname="LEAD-001"
            )

            mock_post.assert_called_once()
            mock_get_doc.assert_called_once()
            insert_args = mock_get_doc.call_args[0][0]
            self.assertEqual(insert_args["doctype"], "WA Message")
            self.assertEqual(insert_args["direction"], "Outgoing")
            self.assertEqual(insert_args["message"], "IDPS Borivali timings are 9:00 AM to 3:30 PM.")
            mock_reply_doc.insert.assert_called_once_with(ignore_permissions=True)
            mock_extract.assert_called_once_with("LEAD-001", "Timings?", "gsk_mock")

    def test_toggle_bot_pause(self):
        recipient = "TEST-PROF-123"
        res = toggle_bot_pause(recipient, True)
        self.assertTrue(res["is_bot_paused"])
        self.assertTrue(is_bot_paused(recipient))

        res2 = toggle_bot_pause(recipient, False)
        self.assertFalse(res2["is_bot_paused"])
        self.assertFalse(is_bot_paused(recipient))

    def test_get_connection_details(self):
        details = get_connection_details()
        self.assertIn("webhook_url", details)
        self.assertTrue(details["webhook_url"].endswith("/api/method/whatsapp.whatsapp.webhook.handler"))
        self.assertEqual(details["webhook_verify_token"], "sensora_idps_borivali_2026")
        self.assertTrue(bool(details["groq_model"]))
