# WhatsApp & AI Chatbot Integration Guide
## Sensora CRM · IDPS Borivali West

---

## 1. Executive Architecture Overview

Sensora CRM integrates Meta's official **WhatsApp Business Cloud API (Graph API v23.0)** and **Groq LPU (Llama 3.3 70B Versatile)** to deliver an automated, conversational school admissions pipeline tailored for **International Delhi Public School (IDPS), Borivali West, Mumbai**.

```
                           ┌────────────────────────────────────────────────────────┐
                           │               Meta Cloud Infrastructure                │
                           └──────────────────────────┬─────────────────────────────┘
                                                      │
                       Webhook Delivery (HTTPS POST)  │  Graph API (HTTPS POST)
                       hub.mode=subscribe             │  v23.0/{phone_number_id}/messages
                       X-Hub-Signature-256            │  Bearer System-User-Token
                                                      ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│                           Sensora CRM (Frappe Framework)                          │
│                                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────────────┐  │
│  │ 1. Webhook Ingestion: whatsapp.whatsapp.webhook.handler                     │  │
│  │    • Validates HMAC SHA-256 Signature using App Secret                      │  │
│  │    • Deduplicates by Meta message_id                                        │  │
│  │    • Resolves or creates WA Profile for parent's phone number               │  │
│  │    • Automatically creates or links CRM Lead (Organization: IDPS Borivali)   │  │
│  │    • Creates and submits incoming WA Message (direction="Incoming")         │  │
│  └──────────────────────────────────────┬──────────────────────────────────────┘  │
│                                         │                                         │
│                      Triggers after_insert / on_submit                            │
│                                         ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────────────┐  │
│  │ 2. Admissions AI Counselor & Background Engine (crm/api/chatbot.py)          │  │
│  │    • Checks 2-hour Human Counselor Takeover Guardrail                       │  │
│  │    • Builds multi-turn conversation context (last 6 messages)               │  │
│  │    • Calls Groq LPU (model: llama-3.3-70b-versatile, ~280 tokens/sec)       │  │
│  │    • Background entity extraction: student_name, grade, child_gender        │  │
│  │    • Automatically updates CRM Lead fields                                  │  │
│  │    • Submits outgoing WA Message (dispatches via Meta Graph API)            │  │
│  └──────────────────────────────────────┬──────────────────────────────────────┘  │
│                                         │                                         │
│                frappe.publish_realtime("whatsapp_message", ...)                   │
│                                         ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────────────┐  │
│  │ 3. Counselor Live Workspace (WhatsAppAutomation.vue)                        │  │
│  │    • Live Parent Inbox & 3-Way Chat Transcripts (Parent / Bot / Counselor)  │  │
│  │    • One-Click Takeover Toggle (Mute / Resume AI Bot)                       │  │
│  │    • Real-Time Meta Connection Tester (Phone status, Quality Rating)        │  │
│  │    • End-to-End Simulation Sandbox for Counselor Onboarding & QA            │  │
│  └─────────────────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Meta WhatsApp Business Cloud API (Official Specification)

### 2.1 Meta Developer App Prerequisites
1. **Meta App Type**: Must be created as a **Business** App at [developers.facebook.com](https://developers.facebook.com/apps).
2. **Products Added**: Add the **WhatsApp** product to the App.
3. **Required Identifiers**:
   - **App ID**: Found in App Dashboard or *App Settings > Basic*.
   - **App Secret**: Found in *App Settings > Basic* (used for HMAC-SHA256 signature verification).
   - **WhatsApp Business Account (WABA) ID**: Found under *WhatsApp > API Setup*.
   - **Phone Number ID**: Found under *WhatsApp > API Setup*.
4. **Permanent System User Token**:
   - The token shown on the *API Setup* page expires after 24 hours.
   - For 24/7 production uptime, go to **Meta Business Settings > Users > System Users**.
   - Create a System User (Role: Admin or Employee), assign the WhatsApp App and WABA account.
   - Generate a token with the following mandatory scopes:
     - `whatsapp_business_messaging`
     - `whatsapp_business_management`

### 2.2 Webhook Handshake & Verification Protocol
Meta verifies endpoints before activating them using a GET request:
- **Callback URL**: `https://<your-domain>/api/method/whatsapp.whatsapp.webhook.handler`
- **Parameters Sent by Meta**:
  - `hub.mode = "subscribe"`
  - `hub.challenge = "<random_integer_or_string>"`
  - `hub.verify_token = "<user_configured_token>"`
- **Required Response**: The endpoint must return the raw `hub.challenge` as `text/plain` with HTTP 200 within 3 seconds. Any JSON wrapping (e.g. `{"message": challenge}`) fails Meta's check.
- **Sensora Verify Token**: `sensora_idps_borivali_2026` (configurable in `WA Settings`).

### 2.3 Webhook Ingestion & HMAC Signature Verification
- **Delivery Protocol**: Meta sends HTTP POST requests with a JSON payload whenever messages or status updates occur.
- **Security Check (`X-Hub-Signature-256`)**:
  - Header: `X-Hub-Signature-256: sha256=<hmac_hash>`
  - The hash is computed using `hmac.new(secret.encode(), raw_payload.encode(), hashlib.sha256).hexdigest()`.
  - When `webhook_secret` is set in Sensora, unverified or spoofed requests are rejected immediately with HTTP 403.
- **Webhook Fields to Subscribe**:
  - `messages`: Inbound messages from parents, read receipts, delivery reports.
  - `message_template_status_update`: Meta approval/rejection updates for WhatsApp templates.

### 2.4 The 24-Hour Customer Care Window Rule
- **Within 24 Hours**: When a parent sends a WhatsApp message to the school, a **24-hour customer service session** opens. During this 24-hour window, the school can send free-form AI counseling responses or manual counselor messages without pre-approval.
- **Outside 24 Hours**: Once 24 hours elapse since the parent's last message, Meta forbids sending free-form text. Re-engagement must use **Meta Pre-Approved WhatsApp Templates** (e.g. Campus Tour Reminder, Application Checklist).

---

## 3. Frappe WhatsApp App Architecture

The official `frappe/whatsapp` app acts as the foundational WhatsApp engine.

### 3.1 DocTypes Matrix

| DocType | Role | Key Fields |
|---|---|---|
| **`WA Settings`** | Global singleton configuration | `webhook_verify_token`, `webhook_secret`, `whatsapp_api_url`, `whatsapp_api_version` (v23.0), `default_account` |
| **`WA Account`** | Meta Business connection | `account_name`, `phone_id`, `business_id`, `app_id`, `access_token` (encrypted password), `status`, `auto_read_receipts` |
| **`WA Profile`** | Normalized parent phone contact | `phone_number` (E.164, e.g. `+919820112345`), `profile_name`, `status` (Active / Blocked), `links` (Dynamic Links to CRM Lead) |
| **`WA Message`** | Full message document (Inbound & Outbound) | `to` (Link to WA Profile), `from`, `direction` (Incoming / Outgoing), `status` (Pending / Sent / Delivered / Read / Failed), `message`, `reference_doctype`, `reference_docname`, `message_id` |
| **`WA Template`** | Synced Meta WhatsApp templates | `template_name`, `status` (Approved / Rejected), `reference_doctype`, `template_variables` (named variables mapped to Lead fields) |
| **`WA Log`** | Complete audit trail | `event_type` (Webhook / Message / API / Template), `level`, `request_data`, `response_data` |

### 3.2 Inbound Message Flow
1. Meta Webhook delivers to `/api/method/whatsapp.whatsapp.webhook.handler`.
2. `webhook.py` validates signature and parses `contacts` and `messages`.
3. Calls `get_or_create_profile(phone_number, account_name)`.
4. Checks `CRM Lead` existence. If absent, automatically generates a new `CRM Lead` (`source="WhatsApp"`, `organization="IDPS Borivali"`, `status="New Inquiry"`).
5. Links `WA Profile` to `CRM Lead` via `WA Profile.links`.
6. Inserts and submits `WA Message` with `direction="Incoming"`.
7. Triggers `crm.api.chatbot.on_incoming_whatsapp_message` via doc_events hook.

### 3.3 Outbound Message Flow
1. Caller creates `WA Message` (`direction="Outgoing"`).
2. `doc.submit()` triggers `before_submit()`:
   - Resolves recipient phone from linked `WA Profile`.
   - Checks if profile is blocked.
   - Builds Meta Graph API payload.
   - Dispatches HTTP POST to `https://graph.facebook.com/v23.0/{phone_id}/messages`.
   - Records Meta message ID (`wamid.HBgL...`) and sets `status="Sent"`.
   - Logs full payload and response in `WA Log`.
3. Realtime event `whatsapp_message` is published over WebSocket to refresh all connected counselor screens.

---

## 4. Sensora Admissions AI & Counselor Hub (IDPS Borivali)

### 4.1 Groq Llama 3.3 70B Admissions Counselor
- **Inference Engine**: Groq Cloud LPU (`llama-3.3-70b-versatile`).
- **Knowledge Base**: Curated for IDPS Borivali West:
  - CBSE curriculum, STEAM labs, sports, robotics, GPS transport.
  - Grades: Playgroup, Nursery, Jr KG, Sr KG, Grade 1 to Grade 10.
  - Academic Year: 2026–2027 Admissions Open.
  - 5-Step Admission Journey: Inquiry ➔ Campus Tour ➔ Registration ➔ Interaction ➔ Enrolment.
  - Campus Timings: Mon–Sat, 9:00 AM – 3:30 PM.
- **Safety & Tone Guardrails**: Warm, polite, concise (2–3 short paragraphs), avoids quoting speculative fee numbers, proactively invites parents to campus visits, and gracefully hands off to human staff when requested.

### 4.2 Human Counselor Takeover & 2-Hour Auto-Pause
- Whenever an admissions counselor sends a manual WhatsApp reply to a parent from the Sensora UI:
  - The AI Counselor is **automatically muted for 2 hours** for that specific parent.
  - This ensures the AI never speaks over or contradicts human counselors.
  - Counselors can also manually toggle `⏸ Pause Bot` or `▶ Resume Bot` at any moment directly from the chat header.

### 4.3 Automated Entity Extraction into CRM Leads
- When an inquiring parent mentions details such as:
  *"Hi, I want to inquire about Grade 2 admission for my daughter Maya"*
- A fast background parser (`llama-3.1-8b-instant`) extracts:
  - `student_name`: `"Maya"`
  - `grade_applying_for`: `"Grade 2"`
  - `child_gender`: `"Girl"`
- The fields are immediately saved onto the parent's `CRM Lead` record, giving counselors instant context before making a follow-up call.

### 4.4 Real-Time End-to-End Simulator
- Admissions counselors and administrators can test the entire pipeline without a physical test phone.
- Located in **WhatsApp & Bot ➔ AI Counselor & Knowledge Base ➔ Simulate Live Parent WhatsApp Inquiry**.
- Generates a realistic incoming parent inquiry, verifies lead generation, runs AI reasoning, and displays the transcript in the Live Chats tab.

---

## 5. Live Production Setup Checklist

### Step 1: Webhook Registration
- URL: `https://<your-crm-domain>/api/method/whatsapp.whatsapp.webhook.handler`
- Verify Token: `sensora_idps_borivali_2026`
- Subscribe to Webhook Fields: `messages`, `message_template_status_update`.

### Step 2: Meta Credentials in Sensora
- Go to Sensora CRM ➔ **WhatsApp & Bot ➔ Real-Time Connection Setup**.
- Fill in:
  - Account Label: `IDPS Borivali Official`
  - Phone Number ID: From Meta API Setup
  - WABA ID: From Meta Business Manager
  - App ID: From Meta Developer Dashboard
  - Permanent Access Token: System user token with messaging permissions
  - App Secret (Optional): For HMAC validation
- Click **Test Meta Connection** to verify live communication with Meta Graph API.
- Click **Save & Connect Real Meta Account**.

### Step 3: Groq Cloud API Activation
Set the Groq API key on the site:
```bash
bench --site crm.localhost set-config groq_api_key "gsk_..."
```
The badge in the WhatsApp Hub header will immediately turn green: **Groq Llama 3.3 Active**.

---

## 6. Verification & Test Suite

All WhatsApp and chatbot components are covered by automated unit and integration tests:

```bash
# Run python chatbot test suite (7 tests)
bench --site crm.localhost run-tests --module crm.tests.test_chatbot

# Run full frontend test suite (413 tests)
cd apps/crm/frontend && yarn test:run
```

