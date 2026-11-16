# IDPS Borivali WhatsApp AI Chatbot (Powered by Groq)

Sensora includes an ultra-fast AI WhatsApp admissions chatbot powered by **Groq** (running Llama 3.3 70B Versatile and Llama 3.1 8B Instant).

---

## 1. How It Works

1. **Incoming Message**: A prospective parent messages the school's WhatsApp Business number.
2. **Meta Webhook**: Meta WhatsApp Cloud API posts the event to `frappe/whatsapp` in Sensora.
3. **Lead & Chatbot Hook**: 
   - A `CRM Lead` is created/identified automatically.
   - The message triggers `crm.api.chatbot.on_incoming_whatsapp_message`.
4. **AI Generation**: 
   - The parent's message and recent chat history are combined with IDPS Borivali's admissions knowledge base.
   - Groq responds in `< 500ms`.
5. **Instant Outgoing Reply**: The bot sends an automated reply back to the parent on WhatsApp.
6. **Smart Field Extraction**: If the parent mentions the student's name, grade, or gender (e.g. *"Looking for Nursery admission for my son Vivaan"*), the bot automatically extracts and updates the fields on the student's `CRM Lead` record!

---

## 2. Configuration & Activation

### Step 1: Obtain a Groq API Key
1. Sign in to [Groq Console](https://console.groq.com/keys).
2. Generate an API Key (begins with `gsk_...`).

### Step 2: Configure in Sensora

Run this command inside the bench container or VPS:

```bash
bench --site crm.localhost set-config groq_api_key "gsk_your_actual_key_here"
bench --site crm.localhost set-config enable_groq_whatsapp_bot 1
```

*Alternatively, you can pass `GROQ_API_KEY` as an environment variable in your `docker-compose.yml`.*

---

## 3. Human Counselor Handoff

The chatbot is designed to assist, not replace, human counselors:
- **Automatic Pause**: If an admission counselor manually sends a message to the parent from the Sensora UI, the AI chatbot **automatically pauses** for that parent for 2 hours.
- **Escalation**: If a parent requests to speak with a human or schedule an in-person campus tour, the AI reassures them that an admission counselor will contact them shortly.

---

## 4. Customizing the School Knowledge Base

To update the school's FAQs, timings, fees policy, or event notices, edit `IDPS_KNOWLEDGE_BASE` in:
`crm/api/chatbot.py`

Key parameters you can update:
- Campus tour timings
- Transportation routes (Borivali, Kandivali, Dahisar, etc.)
- Sports, lab, and extracurricular details
- Documents required for admission verification

