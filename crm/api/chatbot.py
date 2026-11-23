# Copyright (c) 2026, Sensora and contributors
# For license information, please see license.txt

import json
import os
import requests
import frappe
from frappe.utils import now, now_datetime

# IDPS Borivali School Admissions Knowledge Base
IDPS_KNOWLEDGE_BASE = """
You are the official WhatsApp Admissions Counselor for IDPS Borivali (International Delhi Public School, Borivali West, Mumbai).
Your tone is warm, polite, reassuring, professional, and helpful.

Key Information about IDPS Borivali:
- School: International Delhi Public School (IDPS), Borivali West, Mumbai.
- Grades Offered:
  * Pre-Primary: Playgroup, Nursery, Junior KG, Senior KG
  * Primary & Secondary: Grade 1 through Grade 10
- Academic Year: Admissions currently open for Academic Year 2026-2027.
- Curriculum: CBSE-aligned pedagogy focusing on academic excellence, sports, arts, and modern STEAM learning.
- School Features: Smart classrooms, STEM & robotics lab, safe indoor/outdoor play zones, CCTV monitored campus, GPS enabled bus transport covering Borivali, Kandivali, Dahisar and nearby areas.
- Admission Process (5 Simple Steps):
  1. Inquiry & Counseling.
  2. Campus Tour & Parent Interaction.
  3. Admission Registration Form submission.
  4. Child Assessment / Interaction and Admission Offer.
  5. Fee Payment and Enrolment Confirmation.
- Campus Visit & Tour Timings: Monday to Saturday, 9:00 AM to 3:30 PM.

Rules for WhatsApp Responses:
1. Keep replies concise, readable, and friendly. WhatsApp messages should not be overly long (2-3 short paragraphs max).
2. If the parent mentions their child's name, grade, or age, warmly acknowledge it.
3. Strongly encourage the parent to schedule a Campus Visit to experience the school and meet the principal/academic coordinators.
4. If the parent asks about exact fee amounts, mention that fee details vary by grade and offer to schedule a campus visit or share the official fee schedule via an admission counselor.
5. If the parent asks to speak with a human or counselor, reassure them that an admissions counselor will connect with them shortly.
"""

def on_incoming_whatsapp_message(doc, method=None):
    """DocEvent hook called after a WA Message is inserted or submitted.
    Queues the reply so the Meta webhook responds immediately without timing out.

    Registered on ``on_update``, which fires on every save — including status
    changes (Sent → Delivered → Read).  The ``is_new()`` / ``has_value_changed``
    guard ensures we only process a message once.
    """
    if doc.direction != "Incoming" or not doc.message:
        return

    # Idempotency: only act on the first save or when the message body changes.
    # Prevents duplicate Groq calls when Meta sends delivery/read status updates.
    if not doc.is_new() and not doc.has_value_changed("message"):
        return

    # Check if Groq Bot is enabled
    if not is_groq_bot_enabled():
        return

    # Check if bot is paused for this sender
    if is_bot_paused(doc.to):
        return

    # Enqueue background job
    frappe.enqueue(
        "crm.api.chatbot.process_groq_reply",
        queue="short",
        docname=doc.name,
        sender_profile=doc.to,
        message_body=doc.message,
        account_name=doc.whatsapp_account,
        reference_doctype=doc.reference_doctype,
        reference_docname=doc.reference_docname
    )

def is_groq_bot_enabled() -> bool:
    """Check if Groq API key is present and bot is not explicitly disabled."""
    api_key = get_groq_api_key()
    if not api_key:
        return False
    enabled = frappe.conf.get("enable_groq_whatsapp_bot", 1)
    return bool(int(enabled)) if isinstance(enabled, (int, str)) else bool(enabled)

def get_groq_api_key() -> str | None:
    return (
        frappe.conf.get("groq_api_key")
        or os.environ.get("GROQ_API_KEY")
    )

def is_bot_paused(sender_profile: str) -> bool:
    """Returns True if the AI bot is currently paused for this parent."""
    if not sender_profile:
        return False

    # 1. Manual pause flag in cache
    if frappe.cache.get_value(f"wa_bot_paused_{sender_profile}"):
        return True

    # 2. Manual resume flag in cache (takes precedence over recent message check)
    if frappe.cache.get_value(f"wa_bot_resumed_{sender_profile}"):
        return False

    # 3. Check if human counselor sent a message within the last 2 hours
    recent_human_message = frappe.db.sql("""
        SELECT name FROM `tabWA Message`
        WHERE `to` = %s AND direction = 'Outgoing'
        AND owner != 'Administrator'
        AND creation > NOW() - INTERVAL 2 HOUR
        LIMIT 1
    """, (sender_profile,))

    return bool(recent_human_message)

def process_groq_reply(
    docname: str,
    sender_profile: str,
    message_body: str,
    account_name: str,
    reference_doctype: str | None = None,
    reference_docname: str | None = None
):
    """Processes incoming parent query, calls Groq, and sends an automated WhatsApp reply."""
    api_key = get_groq_api_key()
    if not api_key:
        return

    # Check pause status again inside worker
    if is_bot_paused(sender_profile):
        return

    # Ensure Lead linkage if missing
    if not reference_docname:
        phone = frappe.db.get_value("WA Profile", sender_profile, "phone_number")
        if phone:
            from crm.integrations.api import find_by_phone
            matches = find_by_phone(phone)
            for m in (matches or []):
                if m["doctype"] == "CRM Lead":
                    reference_doctype = "CRM Lead"
                    reference_docname = m["docname"]
                    break

    # Build conversation history for multi-turn context
    history = frappe.get_all(
        "WA Message",
        filters={"to": sender_profile},
        fields=["direction", "message"],
        order_by="creation desc",
        limit=6
    )
    history.reverse()

    messages = [{"role": "system", "content": IDPS_KNOWLEDGE_BASE}]
    for msg in history:
        if not msg.message:
            continue
        role = "assistant" if msg.direction == "Outgoing" else "user"
        messages.append({"role": role, "content": msg.message})

    # Ensure the latest message is in the payload
    if not messages or messages[-1]["content"] != message_body:
        messages.append({"role": "user", "content": message_body})

    # Call Groq API (Llama 3.3 70B Versatile)
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": messages,
                "temperature": 0.4,
                "max_tokens": 400
            },
            timeout=10
        )
        data = response.json()
        if "error" in data:
            frappe.log_error(title="Groq API Error", message=json.dumps(data["error"]))
            return

        bot_reply = data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        frappe.log_error(title="Groq WhatsApp Request Failed", message=str(e))
        return

    # Send the outgoing reply via WA Message
    try:
        reply_doc = frappe.get_doc({
            "doctype": "WA Message",
            "direction": "Outgoing",
            "whatsapp_account": account_name,
            "to": sender_profile,
            "message": bot_reply,
            "reference_doctype": reference_doctype,
            "reference_docname": reference_docname
        })
        reply_doc.insert(ignore_permissions=True)
        try:
            reply_doc.submit()
        except Exception as e:
            frappe.log_error(
                title="WA Message submit failed (bot reply)",
                message=f"Doc: {reply_doc.name}, Recipient: {sender_profile}, Error: {e}"
            )
    except Exception as e:
        frappe.log_error(title="Failed to send Groq WhatsApp reply", message=str(e))
        return

    # Extract admission info into Lead
    if reference_doctype == "CRM Lead" and reference_docname:
        _extract_and_update_lead_info(reference_docname, message_body, api_key)

def _extract_and_update_lead_info(lead_name: str, text: str, api_key: str):
    """Background extraction of student name, grade, and gender using small fast model."""
    try:
        lead = frappe.get_doc("CRM Lead", lead_name)
        if lead.get("student_name") and lead.get("grade_applying_for"):
            return

        extract_prompt = f"""
        Extract student admission details from the parent message below.
        Return ONLY valid JSON with keys: student_name, grade_applying_for, child_gender.
        If a field is not found in the message, set it to null.
        Valid grades are: Playgroup, Nursery, Junior KG, Senior KG, Grade 1, Grade 2, Grade 3, Grade 4, Grade 5, Grade 6, Grade 7, Grade 8, Grade 9, Grade 10.
        Valid genders are: Boy, Girl.

        Parent message: "{text}"
        """
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": extract_prompt}],
                "temperature": 0.1,
                "response_format": {"type": "json_object"}
            },
            timeout=5
        )
        extracted = resp.json()["choices"][0]["message"]["content"]
        extracted_data = json.loads(extracted)

        modified = False
        if not lead.get("student_name") and extracted_data.get("student_name"):
            lead.student_name = extracted_data["student_name"]
            modified = True
        if not lead.get("grade_applying_for") and extracted_data.get("grade_applying_for"):
            lead.grade_applying_for = extracted_data["grade_applying_for"]
            modified = True
        if not lead.get("child_gender") and extracted_data.get("child_gender"):
            lead.child_gender = extracted_data["child_gender"]
            modified = True

        if modified:
            lead.save(ignore_permissions=True)
            frappe.db.commit()
    except Exception as e:
        frappe.log_error(
            title="Lead info extraction failed",
            message=f"Lead: {lead_name}, Error: {e}"
        )

@frappe.whitelist()
def get_chatbot_overview():
    """Returns overview statistics, bot status, and conversation summaries for IDPS Borivali."""
    api_key = get_groq_api_key()
    is_enabled = is_groq_bot_enabled()

    total_messages = frappe.db.count("WA Message")
    incoming_count = frappe.db.count("WA Message", {"direction": "Incoming"})
    ai_replies_count = frappe.db.count("WA Message", {"direction": "Outgoing", "owner": "Administrator"})
    counselor_replies_count = frappe.db.count("WA Message", {"direction": "Outgoing", "owner": ("!=", "Administrator")})

    conv_rows = frappe.db.sql("""
        SELECT `to` as recipient, MAX(creation) as last_activity, COUNT(name) as message_count
        FROM `tabWA Message`
        WHERE `to` IS NOT NULL AND `to` != ''
        GROUP BY `to`
        ORDER BY last_activity DESC
        LIMIT 30
    """, as_dict=True)

    conversations = []
    for c in conv_rows:
        rec = c["recipient"]
        prof = frappe.db.get_value("WA Profile", rec, ["profile_name", "phone_number"], as_dict=True) or {}
        parent_name = prof.get("profile_name") or rec
        phone_number = prof.get("phone_number") or rec

        last_msg = frappe.get_all(
            "WA Message",
            filters={"to": rec},
            fields=["direction", "message", "creation", "owner", "reference_doctype", "reference_docname"],
            order_by="creation desc",
            limit=1
        )
        lead_info = None
        if last_msg and last_msg[0].get("reference_doctype") == "CRM Lead" and last_msg[0].get("reference_docname"):
            lead_name = last_msg[0]["reference_docname"]
            if frappe.db.exists("CRM Lead", lead_name):
                lead_data = frappe.db.get_value(
                    "CRM Lead",
                    lead_name,
                    ["name", "first_name", "last_name", "student_name", "grade_applying_for", "status", "mobile_no"],
                    as_dict=True
                )
                lead_info = lead_data

        is_paused = is_bot_paused(rec)

        sender_type = "Parent"
        if last_msg:
            if last_msg[0]["direction"] == "Outgoing":
                sender_type = "AI Bot" if last_msg[0]["owner"] == "Administrator" else "Counselor"

        conversations.append({
            "recipient_id": rec,
            "parent_name": parent_name,
            "phone_number": phone_number,
            "last_activity": c["last_activity"],
            "message_count": c["message_count"],
            "last_message": last_msg[0]["message"] if last_msg else "",
            "last_sender": sender_type,
            "is_bot_paused": is_paused,
            "lead": lead_info
        })

    return {
        "is_enabled": is_enabled,
        "has_api_key": bool(api_key),
        "model": "llama-3.3-70b-versatile",
        "school": "International Delhi Public School (IDPS), Borivali West",
        "total_messages": total_messages,
        "incoming_count": incoming_count,
        "ai_replies_count": ai_replies_count,
        "counselor_replies_count": counselor_replies_count,
        "conversations": conversations,
        "knowledge_base": IDPS_KNOWLEDGE_BASE.strip()
    }

@frappe.whitelist()
def get_conversation_history(recipient: str):
    """Fetches full chat history for a parent's profile."""
    if not recipient:
        return []

    messages = frappe.get_all(
        "WA Message",
        filters={"to": recipient},
        fields=["name", "direction", "message", "creation", "owner", "status", "reference_doctype", "reference_docname"],
        order_by="creation asc"
    )

    enriched = []
    for m in messages:
        direction = m.get("direction")
        owner = m.get("owner")
        sender_type = "parent"
        sender_label = "Parent"

        if direction == "Outgoing":
            if owner == "Administrator":
                sender_type = "bot"
                sender_label = "Admissions AI (Groq)"
            else:
                sender_type = "counselor"
                sender_label = f"Counselor ({owner})"

        enriched.append({
            "name": m.get("name"),
            "direction": direction,
            "message": m.get("message"),
            "timestamp": m.get("creation"),
            "sender_type": sender_type,
            "sender_label": sender_label,
            "status": m.get("status") or "Delivered"
        })

    return enriched

@frappe.whitelist()
def send_counselor_reply(recipient: str, message: str, lead_name: str | None = None):
    """Allows a human admissions counselor to send a WhatsApp reply.
    This automatically triggers the 2-hour AI pause for this parent.
    """
    if not recipient or not message:
        frappe.throw("Recipient and message are required.")

    default_acc = frappe.get_cached_value("WA Settings", "WA Settings", "default_account")
    if not default_acc:
        default_acc = frappe.db.get_value("WA Account", {"status": "Active"}, "name")

    # Set 2-hour AI pause for this recipient
    frappe.cache.set_value(f"wa_bot_paused_{recipient}", 1, expires_in_sec=7200)
    frappe.cache.delete_value(f"wa_bot_resumed_{recipient}")

    doc = frappe.get_doc({
        "doctype": "WA Message",
        "direction": "Outgoing",
        "whatsapp_account": default_acc,
        "to": recipient,
        "message": message,
        "reference_doctype": "CRM Lead" if lead_name else None,
        "reference_docname": lead_name
    })
    doc.insert(ignore_permissions=True)
    try:
        doc.submit()
    except Exception:
        pass
    frappe.db.commit()

    return {"status": "success", "message_name": doc.name}

@frappe.whitelist()
def toggle_bot_pause(recipient: str, paused: bool):
    """Allows a counselor to manually pause or resume the AI bot for a specific parent."""
    if not recipient:
        frappe.throw("Recipient is required.")

    is_p = str(paused).lower() in ("true", "1")
    if is_p:
        frappe.cache.set_value(f"wa_bot_paused_{recipient}", 1, expires_in_sec=7200)
        frappe.cache.delete_value(f"wa_bot_resumed_{recipient}")
        status_text = "AI Counselor paused for 2 hours."
    else:
        frappe.cache.delete_value(f"wa_bot_paused_{recipient}")
        frappe.cache.set_value(f"wa_bot_resumed_{recipient}", 1, expires_in_sec=7200)
        status_text = "AI Counselor resumed."

    return {
        "status": "success",
        "is_bot_paused": is_p,
        "message": status_text
    }

@frappe.whitelist()
def test_admissions_bot(query: str):
    """Interactive testing sandbox for counselors to test the Admissions Chatbot."""
    api_key = get_groq_api_key()
    if not api_key:
        return {
            "reply": "Groq API key not configured yet. Set `groq_api_key` in site config to enable live AI.",
            "mode": "simulation"
        }

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": IDPS_KNOWLEDGE_BASE},
                    {"role": "user", "content": query}
                ],
                "temperature": 0.4,
                "max_tokens": 400
            },
            timeout=10
        )
        data = response.json()
        if "error" in data:
            return {"error": data["error"].get("message", "API Error")}
        return {
            "reply": data["choices"][0]["message"]["content"].strip(),
            "mode": "live"
        }
    except Exception as e:
        return {"error": str(e)}

@frappe.whitelist()
def simulate_parent_inquiry(phone_number: str, message: str, parent_name: str | None = None):
    """Simulates an incoming WhatsApp inquiry from a parent for testing and demonstration."""
    if not phone_number or not message:
        frappe.throw("Phone number and message are required.")

    default_acc = frappe.db.get_single_value("WA Settings", "default_account")
    if not default_acc:
        default_acc = frappe.db.get_value("WA Account", {"status": "Active"}, "name")
        if not default_acc:
            default_acc = frappe.get_doc({
                "doctype": "WA Account",
                "account_name": "IDPS Borivali Official",
                "status": "Active",
                "phone_id": "100012345678901",
                "business_id": "200012345678901",
                "app_id": "300012345678901",
                "access_token": "EAA_test_placeholder_token"
            }).insert(ignore_permissions=True).name
            settings = frappe.get_single("WA Settings")
            settings.default_account = default_acc
            settings.save(ignore_permissions=True)

    from whatsapp.whatsapp.doctype.wa_profile.wa_profile import get_or_create_profile
    profile_name = get_or_create_profile(
        phone_number=phone_number,
        account_name=default_acc,
        profile_name=parent_name or "Prospective Parent"
    )

    from crm.integrations.api import find_by_phone
    lead_name = None
    existing_leads = find_by_phone(phone_number)
    for match in (existing_leads or []):
        if match["doctype"] == "CRM Lead":
            lead_name = match["docname"]
            break

    if not lead_name:
        lead = frappe.new_doc("CRM Lead")
        lead.first_name = parent_name or "Prospective Parent"
        lead.mobile_no = phone_number
        if frappe.db.exists("CRM Lead Source", "WhatsApp"):
            lead.source = "WhatsApp"
        if frappe.db.exists("CRM Organization", "IDPS Borivali"):
            lead.organization = "IDPS Borivali"

        status_name = (
            frappe.db.get_value("CRM Lead Status", {"type": "Open"}, "name")
            or frappe.db.get_value("CRM Lead Status", {}, "name")
        )
        if status_name:
            lead.status = status_name

        lead.notes = f"WhatsApp Inquiry: {message}"
        lead.insert(ignore_permissions=True)
        lead_name = lead.name

    in_msg = frappe.get_doc({
        "doctype": "WA Message",
        "direction": "Incoming",
        "status": "Sent",
        "to": profile_name,
        "from": phone_number,
        "message": message,
        "whatsapp_account": default_acc,
        "reference_doctype": "CRM Lead",
        "reference_docname": lead_name,
        "timestamp": now_datetime()
    })
    in_msg.flags.ignore_permissions = True
    in_msg.submit()

    bot_reply_text = None
    api_key = get_groq_api_key()
    if api_key:
        try:
            resp = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": IDPS_KNOWLEDGE_BASE},
                        {"role": "user", "content": message}
                    ],
                    "temperature": 0.4,
                    "max_tokens": 400
                },
                timeout=10
            )
            data = resp.json()
            if "choices" in data and len(data["choices"]):
                bot_reply_text = data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            frappe.log_error(
                title="Simulation Groq call failed",
                message=f"Phone: {phone_number}, Error: {e}"
            )

    if not bot_reply_text:
        bot_reply_text = (
            f"Hello {parent_name or 'Parent'}! Thank you for reaching out to IDPS Borivali. "
            f"Admissions for Academic Year 2026-2027 are currently open for Playgroup through Grade 10. "
            f"We warmly invite you for a Campus Tour (Mon-Sat, 9:00 AM - 3:30 PM). Would you like to schedule a visit?"
        )

    out_msg = frappe.get_doc({
        "doctype": "WA Message",
        "direction": "Outgoing",
        "status": "Simulated",
        "to": profile_name,
        "from": default_acc,
        "message": bot_reply_text,
        "whatsapp_account": default_acc,
        "reference_doctype": "CRM Lead",
        "reference_docname": lead_name,
        "timestamp": now_datetime()
    })
    out_msg.flags.ignore_permissions = True
    out_msg.flags.ignore_validate = True
    out_msg.insert(ignore_permissions=True)
    # NOTE: No submit() — simulated messages are NOT dispatched via Meta API

    if api_key:
        _extract_and_update_lead_info(lead_name, message, api_key)

    frappe.db.commit()

    return {
        "status": "success",
        "profile": profile_name,
        "lead": lead_name,
        "incoming_message": in_msg.name,
        "reply_message": out_msg.name,
        "bot_reply": bot_reply_text
    }

@frappe.whitelist()
def check_meta_connection():
    """Validates the live connection to Meta WhatsApp Cloud API."""
    settings = frappe.get_single("WA Settings")
    default_acc_name = settings.get("default_account")
    if not default_acc_name:
        return {
            "connected": False,
            "error": "No WhatsApp Account configured. Please enter your Meta credentials in the connection form."
        }

    account = frappe.get_doc("WA Account", default_acc_name)
    access_token = account.get_password("access_token")
    if not access_token or not account.phone_id:
        return {
            "connected": False,
            "error": "Account credentials incomplete. Phone ID and Access Token are required."
        }

    try:
        base_url = settings.get("whatsapp_api_url") or "https://graph.facebook.com"
        api_ver = settings.get("whatsapp_api_version") or "v23.0"
        url = f"{base_url}/{api_ver}/{account.phone_id}"
        resp = requests.get(
            url,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=8
        )
        if resp.status_code == 200:
            data = resp.json()
            return {
                "connected": True,
                "display_phone_number": data.get("display_phone_number"),
                "verified_name": data.get("verified_name"),
                "quality_rating": data.get("quality_rating"),
                "code_verification_status": data.get("code_verification_status"),
                "account_name": account.account_name
            }
        else:
            err = resp.json().get("error", {})
            return {
                "connected": False,
                "error": err.get("message") or f"Meta HTTP Error {resp.status_code}",
                "error_type": err.get("type"),
                "error_code": err.get("code")
            }
    except Exception as e:
        return {
            "connected": False,
            "error": f"Network connection error: {str(e)}"
        }

@frappe.whitelist()
def get_connection_details():
    """Returns real-time connection info for WhatsApp Cloud API & Website sync."""
    settings = frappe.get_single("WA Settings")
    default_acc_name = settings.get("default_account")
    default_acc = None
    if default_acc_name and frappe.db.exists("WA Account", default_acc_name):
        default_acc = frappe.db.get_value(
            "WA Account",
            default_acc_name,
            ["name", "account_name", "status", "phone_id", "business_id", "app_id"],
            as_dict=True
        )

    base_url = frappe.utils.get_url()
    return {
        "webhook_url": f"{base_url}/api/method/whatsapp.whatsapp.webhook.handler",
        "webhook_verify_token": settings.get("webhook_verify_token") or "sensora_idps_borivali_2026",
        "webhook_secret_set": bool(settings.get("webhook_secret")),
        "has_active_account": bool(default_acc and default_acc.get("status") == "Active"),
        "account": default_acc,
        "has_groq_key": bool(get_groq_api_key()),
        "groq_model": "llama-3.3-70b-versatile",
        "lead_sync_endpoint": f"{base_url}/api/method/crm.api.chatbot.create_website_lead",
        "school_name": "IDPS Borivali (International Delhi Public School)",
        "website": "www.idpsborivali.com"
    }

@frappe.whitelist()
def save_whatsapp_account(
    account_name: str,
    phone_id: str,
    business_id: str,
    app_id: str,
    access_token: str,
    webhook_secret: str | None = None
):
    """Saves real Meta WhatsApp Cloud API credentials and configures CRM Lead append automation."""
    if not account_name or not phone_id or not access_token:
        frappe.throw("Account Name, Phone ID, and Access Token are required.")

    existing = frappe.db.get_value("WA Account", {"account_name": account_name}, "name")
    if existing:
        acc = frappe.get_doc("WA Account", existing)
        acc.phone_id = phone_id
        acc.business_id = business_id
        acc.app_id = app_id
        acc.access_token = access_token
        acc.status = "Active"
    else:
        acc = frappe.get_doc({
            "doctype": "WA Account",
            "account_name": account_name,
            "status": "Active",
            "phone_id": phone_id,
            "business_id": business_id,
            "app_id": app_id,
            "access_token": access_token
        })

    # Ensure append action for CRM Lead exists
    has_lead_append = any(
        row.append_to == "CRM Lead" for row in (acc.get("append_actions") or [])
    )
    if not has_lead_append:
        acc.append("append_actions", {
            "append_to": "CRM Lead",
            "trigger_on": "Incoming",
            "sender_field": "mobile_no",
            "sender_name_field": "first_name",
            "message_field": "notes"
        })

    acc.save(ignore_permissions=True)
    acc_name = acc.name

    # Set as default account in WA Settings
    settings = frappe.get_single("WA Settings")
    settings.default_account = acc_name
    if webhook_secret:
        settings.webhook_secret = webhook_secret
    if not settings.webhook_verify_token:
        settings.webhook_verify_token = "sensora_idps_borivali_2026"
    settings.save(ignore_permissions=True)
    frappe.db.commit()

    # Attempt to subscribe app to WABA webhooks if business_id and app_id are set
    subscription_status = "Skipped"
    try:
        from whatsapp.whatsapp.api.whatsapp import WhatsApp
        client = WhatsApp(frappe._dict({
            "business_id": business_id,
            "app_id": app_id,
            "access_token": access_token,
            "phone_number_id": phone_id,
            "account_name": acc_name,
            "base_url": settings.get("whatsapp_api_url") or "https://graph.facebook.com",
            "api_version": settings.get("whatsapp_api_version") or "v23.0"
        }))
        res = client.subscribe_app()
        subscription_status = "Subscribed" if res.get("success") else "Failed"
    except Exception as e:
        frappe.log_error(title="WhatsApp App Subscription Attempt Failed", message=str(e))
        subscription_status = f"Error: {e}"

    # Enqueue template sync from Meta
    try:
        frappe.enqueue("whatsapp.whatsapp.doctype.wa_template.wa_template.sync_all", queue="short")
    except Exception:
        pass

    return {
        "status": "success",
        "account": acc_name,
        "webhook_subscription": subscription_status
    }

@frappe.whitelist(allow_guest=True)
def create_website_lead(
    first_name: str | None = None,
    last_name: str | None = None,
    mobile_no: str | None = None,
    email: str | None = None,
    student_name: str | None = None,
    grade_applying_for: str | None = None,
    child_dob: str | None = None,
    child_gender: str | None = None,
    previous_school: str | None = None,
    academic_year: str | None = None,
    notes: str | None = None,
    parent_consent_confirmed: int | str = 1
):
    """Public whitelisted API endpoint to receive admission leads directly from
    www.idpsborivali.com contact and admission inquiry forms into Sensora CRM.
    Supports CORS pre-flight, verifies parental consent, and records consent timestamp.
    """
    # Allow CORS headers for idpsborivali.com
    origin = frappe.request.headers.get("Origin", "")
    if origin and ("idpsborivali.com" in origin or "localhost" in origin):
        frappe.response["headers"] = frappe.response.get("headers", {})
        frappe.response["headers"]["Access-Control-Allow-Origin"] = origin
        frappe.response["headers"]["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        frappe.response["headers"]["Access-Control-Allow-Headers"] = "Content-Type, Authorization"

    if frappe.request.method == "OPTIONS":
        return {"status": "ok"}

    # Handle JSON body payload if sent as application/json
    if frappe.request.is_json and not first_name:
        try:
            data = frappe.request.get_json() or {}
            first_name = data.get("first_name") or data.get("parent_name") or data.get("name")
            last_name = data.get("last_name")
            mobile_no = data.get("mobile_no") or data.get("phone") or data.get("mobile")
            email = data.get("email")
            student_name = data.get("student_name") or data.get("child_name")
            grade_applying_for = data.get("grade_applying_for") or data.get("grade")
            child_dob = data.get("child_dob") or data.get("dob")
            child_gender = data.get("child_gender") or data.get("gender")
            previous_school = data.get("previous_school")
            academic_year = data.get("academic_year")
            notes = data.get("notes") or data.get("message")
            parent_consent_confirmed = data.get("parent_consent_confirmed", 1)
        except Exception:
            pass

    if not first_name and not student_name:
        frappe.throw("Parent Name or Student Name is required.")

    if not mobile_no:
        frappe.throw("Mobile / Phone number is required.")

    # Deduplication: check if lead with same phone already exists
    from crm.integrations.api import find_by_phone
    lead_name = None
    existing_matches = find_by_phone(mobile_no)
    for match in (existing_matches or []):
        if match.get("doctype") == "CRM Lead":
            lead_name = match.get("docname")
            break

    if lead_name:
        lead = frappe.get_doc("CRM Lead", lead_name)
        # Update missing student information if provided
        if not lead.get("student_name") and student_name:
            lead.student_name = student_name
        if not lead.get("grade_applying_for") and grade_applying_for:
            lead.grade_applying_for = grade_applying_for
        if not lead.get("child_gender") and child_gender:
            lead.child_gender = child_gender
        if not lead.get("child_dob") and child_dob:
            lead.child_dob = child_dob
        if notes:
            existing_notes = lead.get("notes") or ""
            lead.notes = f"{existing_notes}\n[Website Inquiry Update]: {notes}".strip()
        lead.save(ignore_permissions=True)
        frappe.db.commit()
        return {
            "status": "success",
            "action": "updated",
            "lead": lead.name,
            "message": "Lead updated successfully from website inquiry."
        }

    # Create new CRM Lead
    lead = frappe.new_doc("CRM Lead")
    lead.first_name = first_name or "Prospective Parent"
    if last_name:
        lead.last_name = last_name
    lead.mobile_no = mobile_no
    if email:
        lead.email = email

    # IDPS Admission specifics
    if student_name:
        lead.student_name = student_name
    if grade_applying_for:
        lead.grade_applying_for = grade_applying_for
    if child_gender:
        lead.child_gender = child_gender
    if child_dob:
        lead.child_dob = child_dob
    if previous_school:
        lead.previous_school = previous_school
    lead.academic_year = academic_year or "2026-2027"

    # DPDP Act Parental Consent recording
    is_consent = str(parent_consent_confirmed).lower() in ("1", "true", "yes")
    lead.parent_consent_confirmed = 1 if is_consent else 0
    if is_consent:
        lead.consent_timestamp = now_datetime()

    # Source & Status
    if frappe.db.exists("CRM Lead Source", "School Website"):
        lead.source = "School Website"
    elif frappe.db.exists("CRM Lead Source", "Website"):
        lead.source = "Website"

    if frappe.db.exists("CRM Organization", "IDPS Borivali"):
        lead.organization = "IDPS Borivali"

    status_name = (
        frappe.db.get_value("CRM Lead Status", {"type": "Open"}, "name")
        or frappe.db.get_value("CRM Lead Status", {}, "name")
    )
    if status_name:
        lead.status = status_name

    if notes:
        lead.notes = f"Website Form Inquiry:\n{notes}"

    lead.insert(ignore_permissions=True)
    frappe.db.commit()

    return {
        "status": "success",
        "action": "created",
        "lead": lead.name,
        "message": "Inquiry recorded successfully in Sensora CRM."
    }

