<template>
  <div class="flex h-full flex-col bg-surface-white text-ink-gray-9 overflow-hidden">
    <!-- Top Header Bar -->
    <header class="flex items-center justify-between border-b px-5 py-3.5 bg-surface-white">
      <div class="flex items-center gap-3">
        <div class="flex size-9 items-center justify-center rounded-lg bg-emerald-500/10 text-emerald-600">
          <WhatsAppIcon class="size-5" />
        </div>
        <div>
          <div class="flex items-center gap-2">
            <h1 class="text-lg font-semibold text-ink-gray-9">WhatsApp Automation & Chatbot</h1>
            <Badge :theme="connection.has_active_account ? 'green' : 'amber'" size="sm">
              <span class="flex items-center gap-1.5">
                <span class="size-1.5 rounded-full" :class="connection.has_active_account ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'"></span>
                {{ connection.has_active_account ? 'Meta WhatsApp Connected' : 'Waiting for Credentials' }}
              </span>
            </Badge>
            <Badge :theme="connection.has_groq_key ? 'green' : 'gray'" size="sm">
              {{ connection.has_groq_key ? 'Groq Llama 3.3 Active' : 'Groq Standby' }}
            </Badge>
          </div>
          <p class="text-xs text-ink-gray-5">IDPS Borivali Admissions · Live Real-time WhatsApp Cloud API & AI Counselor</p>
        </div>
      </div>

      <!-- Quick Metrics & Refresh -->
      <div class="flex items-center gap-3">
        <div class="hidden sm:flex items-center gap-4 text-xs text-ink-gray-6 border rounded-lg px-3 py-1.5 bg-surface-gray-1">
          <div><span class="font-semibold text-ink-gray-8">{{ stats.total_messages || 0 }}</span> Live Messages</div>
          <div class="h-3 w-px bg-outline-gray-2"></div>
          <div><span class="font-semibold text-ink-gray-8">{{ stats.ai_replies_count || 0 }}</span> AI Replies</div>
          <div class="h-3 w-px bg-outline-gray-2"></div>
          <div><span class="font-semibold text-ink-gray-8">{{ stats.counselor_replies_count || 0 }}</span> Counselor Messages</div>
        </div>

        <Button
          variant="outline"
          icon-left="lucide-refresh-cw"
          :loading="loading"
          @click="fetchOverview"
        >
          Refresh
        </Button>
      </div>
    </header>

    <!-- Subheader Tabs Navigation -->
    <div class="flex border-b px-5 bg-surface-white">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        class="flex items-center gap-2 border-b-2 px-3.5 py-2.5 text-sm font-medium transition-colors"
        :class="activeTab === tab.id
          ? 'border-emerald-600 text-emerald-600 font-semibold'
          : 'border-transparent text-ink-gray-6 hover:text-ink-gray-8'"
        @click="activeTab = tab.id"
      >
        <component :is="tab.icon" class="size-4" />
        {{ tab.label }}
        <span
          v-if="tab.badge"
          class="ml-1 rounded-full px-1.5 py-0.5 text-[10px] font-semibold"
          :class="activeTab === tab.id ? 'bg-emerald-100 text-emerald-700' : 'bg-surface-gray-2 text-ink-gray-6'"
        >
          {{ tab.badge }}
        </span>
      </button>
    </div>

    <!-- TAB 1: Live Parent Chats & Interaction View -->
    <div v-if="activeTab === 'chats'" class="flex flex-1 overflow-hidden">
      <!-- If No Messages exist yet (Pure Live Empty State) -->
      <div v-if="!stats.conversations?.length" class="flex-1 flex flex-col items-center justify-center p-8 bg-surface-gray-1 text-center">
        <div class="size-16 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center mb-4">
          <WhatsAppIcon class="size-8" />
        </div>
        <h2 class="text-lg font-bold text-ink-gray-9 mb-1">Live WhatsApp Admissions Inbox Active</h2>
        <p class="text-sm text-ink-gray-6 max-w-md mb-6">
          No messages received yet. As soon as a parent sends a WhatsApp message or submits an admission inquiry, their live conversation and AI counselor interactions will appear here in real time.
        </p>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-lg w-full text-left">
          <div class="border rounded-xl p-4 bg-surface-white shadow-sm">
            <div class="text-xs font-semibold text-emerald-700 mb-1">Meta Webhook Listener</div>
            <div class="text-xs text-ink-gray-6">
              Status: <span class="font-bold text-emerald-600">Active & Ready</span>
            </div>
            <div class="text-[11px] text-ink-gray-4 mt-2">
              Ready to receive real-time messages from Meta Cloud API.
            </div>
          </div>

          <div class="border rounded-xl p-4 bg-surface-white shadow-sm">
            <div class="text-xs font-semibold text-blue-700 mb-1">School Website Form Sync</div>
            <div class="text-xs text-ink-gray-6">
              Status: <span class="font-bold text-blue-600">Active</span>
            </div>
            <div class="text-[11px] text-ink-gray-4 mt-2">
              Website lead submissions auto-sync into CRM Leads.
            </div>
          </div>
        </div>

        <div class="mt-6 flex gap-3">
          <Button variant="solid" theme="green" @click="activeTab = 'connection'">
            View Real-Time Connection Setup
          </Button>
          <Button variant="outline" @click="activeTab = 'bot'">
            Test AI Admissions Chatbot
          </Button>
        </div>
      </div>

      <!-- If Conversations Exist -->
      <template v-else>
        <!-- Left Column: Conversations List -->
        <div class="w-80 sm:w-96 flex flex-col border-r bg-surface-gray-1 overflow-hidden">
          <div class="p-3 border-b bg-surface-white">
            <TextInput
              v-model="searchQuery"
              placeholder="Search parent name, phone, student..."
              size="sm"
              icon-left="lucide-search"
            />
          </div>

          <div class="flex-1 overflow-y-auto divide-y divide-outline-gray-2">
            <button
              v-for="conv in filteredConversations"
              :key="conv.recipient_id"
              class="w-full text-left p-3.5 transition-colors hover:bg-surface-white flex flex-col gap-1.5"
              :class="selectedRecipient === conv.recipient_id ? 'bg-surface-white border-l-4 border-l-emerald-600 shadow-sm' : ''"
              @click="selectConversation(conv)"
            >
              <div class="flex items-center justify-between">
                <span class="font-semibold text-sm text-ink-gray-9 truncate">{{ conv.parent_name }}</span>
                <span class="text-[11px] text-ink-gray-4 whitespace-nowrap">{{ formatTimeAgo(conv.last_activity) }}</span>
              </div>

              <div class="flex items-center gap-2 text-xs text-ink-gray-5">
                <span>{{ conv.phone_number }}</span>
                <span v-if="conv.lead?.student_name" class="rounded bg-emerald-50 px-1.5 py-0.5 text-[10px] font-medium text-emerald-700">
                  Student: {{ conv.lead.student_name }}
                </span>
                <span v-if="conv.lead?.grade_applying_for" class="rounded bg-blue-50 px-1.5 py-0.5 text-[10px] font-medium text-blue-700">
                  {{ conv.lead.grade_applying_for }}
                </span>
              </div>

              <div class="text-xs text-ink-gray-6 line-clamp-2 mt-0.5">
                <span v-if="conv.last_sender === 'AI Bot'" class="font-medium text-emerald-600">🤖 AI: </span>
                <span v-else-if="conv.last_sender === 'Counselor'" class="font-medium text-blue-600">👩‍💼 Counselor: </span>
                <span v-else class="font-medium text-ink-gray-7">Parent: </span>
                {{ conv.last_message }}
              </div>

              <div class="flex items-center gap-2 mt-1">
                <span v-if="conv.is_bot_paused" class="inline-flex items-center gap-1 rounded bg-amber-50 px-1.5 py-0.5 text-[10px] font-medium text-amber-700">
                  <span class="size-1.5 rounded-full bg-amber-500"></span>
                  Counselor Active (Bot Muted)
                </span>
                <span v-else class="inline-flex items-center gap-1 rounded bg-emerald-50 px-1.5 py-0.5 text-[10px] font-medium text-emerald-700">
                  <span class="size-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                  AI Answering
                </span>
                <span class="text-[10px] text-ink-gray-4 ml-auto">{{ conv.message_count }} msgs</span>
              </div>
            </button>
          </div>
        </div>

        <!-- Right Column: Chat Transcript & Actions -->
        <div v-if="currentConv" class="flex-1 flex flex-col bg-[#efeae2] overflow-hidden">
          <!-- Chat Header -->
          <div class="flex items-center justify-between border-b px-4 py-2.5 bg-surface-white shadow-sm">
            <div class="flex items-center gap-3">
              <div class="size-10 rounded-full bg-emerald-100 text-emerald-700 font-bold flex items-center justify-center text-sm">
                {{ currentConv.parent_name?.slice(0, 2).toUpperCase() || 'PA' }}
              </div>
              <div>
                <div class="flex items-center gap-2">
                  <h3 class="font-semibold text-sm text-ink-gray-9">{{ currentConv.parent_name }}</h3>
                  <span class="text-xs text-ink-gray-5">{{ currentConv.phone_number }}</span>
                </div>
                <div class="flex items-center gap-2 text-xs">
                  <span v-if="currentConv.lead?.student_name" class="text-emerald-700 font-medium">
                    Applying for: {{ currentConv.lead.student_name }} ({{ currentConv.lead.grade_applying_for || 'Grade N/A' }})
                  </span>
                  <span v-if="currentConv.lead" class="text-ink-gray-4">· Lead ID: {{ currentConv.lead.name }}</span>
                </div>
              </div>
            </div>

            <div class="flex items-center gap-2">
              <Button
                v-if="currentConv.lead"
                variant="subtle"
                icon-left="lucide-external-link"
                size="sm"
                @click="openLeadRecord(currentConv.lead.name)"
              >
                Open Lead
              </Button>

              <Button
                :variant="currentConv.is_bot_paused ? 'solid' : 'outline'"
                :theme="currentConv.is_bot_paused ? 'blue' : 'gray'"
                size="sm"
                @click="toggleBotPause(currentConv)"
              >
                {{ currentConv.is_bot_paused ? '▶ Resume AI Bot' : '⏸ Take Over (Pause Bot)' }}
              </Button>
            </div>
          </div>

          <!-- Messages Stream -->
          <div class="flex-1 overflow-y-auto p-4 space-y-3" ref="chatScrollContainer">
            <div v-if="loadingMessages" class="py-8 text-center text-ink-gray-5 text-sm">
              Loading transcript...
            </div>

            <div
              v-for="msg in currentMessages"
              :key="msg.name"
              class="flex flex-col"
              :class="msg.direction === 'Incoming' ? 'items-start' : 'items-end'"
            >
              <div class="flex items-center gap-1.5 mb-1 text-[11px] font-medium px-1"
                :class="msg.direction === 'Incoming' ? 'text-ink-gray-6' : 'text-emerald-700'"
              >
                <span>{{ msg.sender_label }}</span>
              </div>

              <div
                class="max-w-[75%] rounded-lg px-3.5 py-2.5 shadow-sm text-sm"
                :class="msg.direction === 'Incoming'
                  ? 'bg-surface-white text-ink-gray-9 rounded-tl-none border'
                  : msg.sender_type === 'bot'
                    ? 'bg-[#d9fdd3] text-ink-gray-9 rounded-tr-none border border-emerald-200'
                    : 'bg-[#c7e9fb] text-ink-gray-9 rounded-tr-none border border-blue-200'"
              >
                <p class="whitespace-pre-wrap leading-relaxed">{{ msg.message }}</p>
                <div class="mt-1 flex items-center justify-end gap-1 text-[10px] text-ink-gray-5">
                  <span>{{ formatMessageTime(msg.timestamp) }}</span>
                  <span v-if="msg.direction === 'Outgoing'">✓✓</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Counselor Live Reply Box -->
          <div class="p-3 bg-surface-white border-t">
            <div class="flex items-center justify-between text-xs text-ink-gray-5 mb-2 px-1">
              <span>
                <span v-if="currentConv.is_bot_paused" class="text-amber-700 font-medium">⚠️ Bot is paused for this parent.</span>
                <span v-else class="text-emerald-700 font-medium">🤖 AI Bot is actively answering parent questions.</span>
                Sending a manual message will pause the AI for 2 hours.
              </span>
            </div>

            <div class="flex gap-2">
              <textarea
                v-model="replyText"
                rows="2"
                class="flex-1 rounded-md border border-outline-gray-2 p-2.5 text-sm text-ink-gray-9 focus:border-emerald-600 focus:outline-none resize-none"
                placeholder="Type a counselor response to send on WhatsApp..."
                @keydown.ctrl.enter="sendReply"
              ></textarea>
              <Button
                variant="solid"
                theme="green"
                class="self-end !h-10 px-4"
                :loading="sendingReply"
                :disabled="!replyText.trim()"
                @click="sendReply"
              >
                Send
              </Button>
            </div>
          </div>
        </div>

        <div v-else class="flex-1 flex items-center justify-center bg-surface-gray-1 text-ink-gray-5 text-sm">
          Select a conversation from the left to view the interactive admissions transcript.
        </div>
      </template>
    </div>

    <!-- TAB 2: Real-Time Connection Setup (Meta Cloud API, Groq & Website Sync) -->
    <div v-else-if="activeTab === 'connection'" class="flex-1 overflow-y-auto p-6 max-w-5xl mx-auto w-full space-y-6">
      <div>
        <h2 class="text-lg font-bold text-ink-gray-9">Real-Time Data & API Connections</h2>
        <p class="text-xs text-ink-gray-5">Configure live Meta WhatsApp Cloud API credentials, webhook verification, and website lead synchronization.</p>
      </div>

      <!-- 1. Meta WhatsApp Cloud API Configuration -->
      <div class="border rounded-xl p-5 bg-surface-white shadow-sm space-y-4">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-base font-bold text-ink-gray-9">1. Meta WhatsApp Cloud API Webhook</h3>
            <p class="text-xs text-ink-gray-5">Copy these parameters into your Meta Developer App (WhatsApp ➔ Configuration).</p>
          </div>
          <Badge :theme="connection.has_active_account ? 'green' : 'amber'" size="sm">
            {{ connection.has_active_account ? 'Active' : 'Awaiting Setup' }}
          </Badge>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-semibold text-ink-gray-7 mb-1">Callback URL (Webhook)</label>
            <div class="flex gap-2">
              <input
                type="text"
                readonly
                :value="connection.webhook_url"
                class="flex-1 rounded-md border border-outline-gray-2 bg-surface-gray-1 p-2 text-xs font-mono text-ink-gray-8"
              />
              <Button size="sm" @click="copyToClipboard(connection.webhook_url)">Copy</Button>
            </div>
            <p class="text-[11px] text-ink-gray-4 mt-1">Meta delivers all incoming messages & status updates to this endpoint.</p>
          </div>

          <div>
            <label class="block text-xs font-semibold text-ink-gray-7 mb-1">Verify Token</label>
            <div class="flex gap-2">
              <input
                type="text"
                readonly
                :value="connection.webhook_verify_token"
                class="flex-1 rounded-md border border-outline-gray-2 bg-surface-gray-1 p-2 text-xs font-mono text-ink-gray-8"
              />
              <Button size="sm" @click="copyToClipboard(connection.webhook_verify_token)">Copy</Button>
            </div>
            <p class="text-[11px] text-ink-gray-4 mt-1">Enter this exact token in Meta Developer Portal during webhook registration.</p>
          </div>
        </div>

        <div class="rounded-lg bg-surface-gray-1 p-3 border text-xs text-ink-gray-7 space-y-1">
          <div class="font-semibold text-ink-gray-9">Quick Meta Developer Portal Checklist:</div>
          <div>1. Go to <span class="font-mono text-emerald-700">developers.facebook.com</span> ➔ Your App ➔ WhatsApp ➔ Configuration.</div>
          <div>2. Paste the <strong>Callback URL</strong> and <strong>Verify Token</strong> above and click <em>Verify and Save</em>.</div>
          <div>3. Under <strong>Webhook fields</strong>, subscribe to <span class="font-mono text-emerald-700 font-semibold">messages</span> and <span class="font-mono text-emerald-700 font-semibold">message_template_status_update</span>.</div>
        </div>

        <hr class="border-t my-2" />

        <!-- Live Credentials Form -->
        <div>
          <h4 class="text-xs font-bold uppercase tracking-wider text-ink-gray-6 mb-3">Meta Business Account Credentials</h4>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-medium text-ink-gray-7 mb-1">Account Label</label>
              <TextInput v-model="accountForm.account_name" placeholder="e.g. IDPS Borivali Official" />
            </div>
            <div>
              <label class="block text-xs font-medium text-ink-gray-7 mb-1">Phone Number ID</label>
              <TextInput v-model="accountForm.phone_id" placeholder="From Meta App > WhatsApp > API Setup" />
            </div>
            <div>
              <label class="block text-xs font-medium text-ink-gray-7 mb-1">WhatsApp Business Account ID (WABA ID)</label>
              <TextInput v-model="accountForm.business_id" placeholder="WABA ID from Meta Business Manager" />
            </div>
            <div>
              <label class="block text-xs font-medium text-ink-gray-7 mb-1">App ID</label>
              <TextInput v-model="accountForm.app_id" placeholder="Meta App ID" />
            </div>
            <div class="md:col-span-2">
              <label class="block text-xs font-medium text-ink-gray-7 mb-1">App Secret (for HMAC-SHA256 Webhook Verification)</label>
              <TextInput v-model="accountForm.webhook_secret" placeholder="From Meta App Settings > Basic > App Secret (Optional but recommended)" />
            </div>
            <div class="md:col-span-2">
              <label class="block text-xs font-medium text-ink-gray-7 mb-1">Permanent Access Token (System User Token)</label>
              <textarea
                v-model="accountForm.access_token"
                rows="2"
                class="w-full rounded-md border border-outline-gray-2 p-2 text-xs font-mono text-ink-gray-9 focus:border-emerald-600 focus:outline-none"
                placeholder="EAA..."
              ></textarea>
              <p class="text-[11px] text-ink-gray-4 mt-1">Generate via Meta Business Settings > Users > System Users with <span class="font-mono">whatsapp_business_messaging</span> and <span class="font-mono">whatsapp_business_management</span>.</p>
            </div>
          </div>

          <div class="mt-4 flex items-center justify-between gap-3 flex-wrap">
            <span v-if="accountSavedMsg" class="text-xs font-semibold" :class="accountSavedMsg.startsWith('Error') ? 'text-red-600' : 'text-emerald-600'">{{ accountSavedMsg }}</span>
            <div class="flex items-center gap-2 ml-auto">
              <Button
                variant="outline"
                :loading="checkingMeta"
                @click="testMetaConnection"
              >
                Test Meta Connection
              </Button>
              <Button
                variant="solid"
                theme="green"
                :loading="savingAccount"
                @click="saveMetaAccount"
              >
                Save & Connect Real Meta Account
              </Button>
            </div>
          </div>

          <!-- Connection Test Feedback Panel -->
          <div v-if="metaTestFeedback" class="mt-3 p-3 rounded-lg border text-xs leading-relaxed"
            :class="metaTestFeedback.connected ? 'bg-emerald-50 border-emerald-200 text-emerald-800' : 'bg-red-50 border-red-200 text-red-800'">
            <div class="font-bold mb-1">
              {{ metaTestFeedback.connected ? '✓ Meta WhatsApp Cloud API Connected Successfully' : '⚠️ Connection Failed' }}
            </div>
            <div v-if="metaTestFeedback.connected">
              <div>Phone Number: <span class="font-mono font-bold">{{ metaTestFeedback.display_phone_number || 'N/A' }}</span></div>
              <div>Verified Name: <span class="font-bold">{{ metaTestFeedback.verified_name || 'N/A' }}</span></div>
              <div>Quality Rating: <span class="font-bold uppercase">{{ metaTestFeedback.quality_rating || 'GREEN' }}</span></div>
            </div>
            <div v-else>
              {{ metaTestFeedback.error }}
            </div>
          </div>
        </div>
      </div>

      <!-- 2. School Website Lead Form Real-Time Sync -->
      <div class="border rounded-xl p-5 bg-surface-white shadow-sm space-y-3">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-base font-bold text-ink-gray-9">2. School Website Lead Form Real-Time Sync</h3>
            <p class="text-xs text-ink-gray-5">When prospective parents fill the admission form on your website, sync leads instantly to this CRM.</p>
          </div>
          <Badge theme="blue" size="sm">REST API</Badge>
        </div>

        <div>
          <label class="block text-xs font-semibold text-ink-gray-7 mb-1">Lead Submission Endpoint</label>
          <div class="flex gap-2 mb-2">
            <input
              type="text"
              readonly
              :value="connection.lead_sync_endpoint"
              class="flex-1 rounded-md border border-outline-gray-2 bg-surface-gray-1 p-2 text-xs font-mono text-ink-gray-8"
            />
            <Button size="sm" @click="copyToClipboard(connection.lead_sync_endpoint)">Copy Endpoint</Button>
          </div>

          <label class="block text-xs font-semibold text-ink-gray-7 mb-1">Website Form Integration Snippet (JavaScript)</label>
          <pre class="rounded-lg bg-surface-gray-2 p-3 text-[11px] font-mono text-ink-gray-8 overflow-x-auto border leading-relaxed">// Send form data from website to CRM in real time:
fetch("{{ connection.lead_sync_endpoint }}", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    first_name: parentFirstName,
    last_name: parentLastName,
    mobile_no: parentPhone,
    email: parentEmail,
    student_name: childName,
    grade_applying_for: selectedGrade,
    source: "School Website"
  })
});</pre>
        </div>
      </div>
    </div>

    <!-- TAB 3: AI Counselor Knowledge Base & Live Sandbox Simulator -->
    <div v-else-if="activeTab === 'bot'" class="flex-1 overflow-y-auto p-6 max-w-6xl mx-auto w-full space-y-6">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="border rounded-xl p-4 bg-surface-white shadow-sm">
          <div class="text-xs text-ink-gray-5 font-medium">Active AI Model</div>
          <div class="text-lg font-bold text-ink-gray-9 mt-1">Llama 3.3 70B Versatile</div>
          <p class="text-xs text-ink-gray-5 mt-1">Hosted on Groq LPU (~280 tokens/sec response time)</p>
        </div>
        <div class="border rounded-xl p-4 bg-surface-white shadow-sm">
          <div class="text-xs text-ink-gray-5 font-medium">School Target</div>
          <div class="text-lg font-bold text-ink-gray-9 mt-1">IDPS Borivali West</div>
          <p class="text-xs text-ink-gray-5 mt-1">Academic Year 2026-2027 Admissions</p>
        </div>
        <div class="border rounded-xl p-4 bg-surface-white shadow-sm">
          <div class="text-xs text-ink-gray-5 font-medium">Human Takeover Guardrail</div>
          <div class="text-lg font-bold text-ink-gray-9 mt-1">2-Hour Auto-Pause</div>
          <p class="text-xs text-ink-gray-5 mt-1">Bot mutes whenever a counselor replies manually</p>
        </div>
      </div>

      <!-- Live Parent Inquiry Simulator (End-to-End Test) -->
      <div class="border rounded-xl p-5 bg-surface-white shadow-sm space-y-4">
        <div>
          <div class="flex items-center justify-between">
            <h2 class="text-base font-bold text-ink-gray-9">🚀 Simulate Live Parent WhatsApp Inquiry</h2>
            <Badge theme="green" size="sm">End-to-End Pipeline</Badge>
          </div>
          <p class="text-xs text-ink-gray-5">Simulates an incoming WhatsApp message as if sent by a parent. It automatically creates a CRM Lead, triggers the AI Admissions Counselor, updates lead fields, and appears in the Live Chats tab.</p>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-medium text-ink-gray-7 mb-1">Parent Name</label>
            <TextInput v-model="simName" placeholder="e.g., Meera Singhania" />
          </div>
          <div>
            <label class="block text-xs font-medium text-ink-gray-7 mb-1">Parent Mobile Number</label>
            <TextInput v-model="simPhone" placeholder="e.g., +91 98201 88776" />
          </div>
          <div class="sm:col-span-2">
            <label class="block text-xs font-medium text-ink-gray-7 mb-1">WhatsApp Message</label>
            <textarea
              v-model="simMessage"
              rows="2"
              class="w-full rounded-md border border-outline-gray-2 p-2.5 text-xs text-ink-gray-9 focus:border-emerald-600 focus:outline-none resize-none"
              placeholder="e.g., Hi, I want to inquire about Grade 3 admission for my daughter Anaya for 2026-27. What are the school timings and transport facilities?"
            ></textarea>
          </div>
        </div>

        <div class="flex items-center justify-between">
          <span v-if="simFeedback" class="text-xs font-semibold text-emerald-600">{{ simFeedback }}</span>
          <Button
            variant="solid"
            theme="green"
            class="ml-auto"
            :loading="simulatingInquiry"
            :disabled="!simPhone.trim() || !simMessage.trim()"
            @click="simulateInquiry"
          >
            Dispatch Simulated Inquiry
          </Button>
        </div>
      </div>

      <!-- Quick AI Bot Testing Sandbox -->
      <div class="border rounded-xl p-5 bg-surface-white shadow-sm space-y-4">
        <div>
          <h2 class="text-base font-bold text-ink-gray-9">🧪 Quick Question Testing (Sandbox)</h2>
          <p class="text-xs text-ink-gray-5">Ask a single question as a prospective parent to preview the AI counselor's reasoning and response.</p>
        </div>

        <div class="flex gap-2">
          <TextInput
            v-model="testQuery"
            placeholder="e.g., What are the school timings? Or: What sports and activities do you offer?"
            class="flex-1"
            @keydown.enter="runTestQuery"
          />
          <Button
            variant="solid"
            theme="green"
            :loading="testingBot"
            :disabled="!testQuery.trim()"
            @click="runTestQuery"
          >
            Ask AI
          </Button>
        </div>

        <div v-if="testResult" class="rounded-lg border bg-surface-gray-1 p-4">
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-semibold text-emerald-700">🤖 AI Admissions Counselor Preview</span>
            <span class="text-[10px] text-ink-gray-5">{{ testResultMode }}</span>
          </div>
          <p class="whitespace-pre-wrap text-sm text-ink-gray-9 leading-relaxed">{{ testResult }}</p>
        </div>
      </div>

      <!-- School Knowledge Base Reference -->
      <div class="border rounded-xl p-5 bg-surface-white shadow-sm space-y-3">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-base font-bold text-ink-gray-9">IDPS Borivali Admissions Knowledge Base</h2>
            <p class="text-xs text-ink-gray-5">The prompt and guidelines given to the AI counselor on WhatsApp.</p>
          </div>
          <Badge theme="blue" size="sm">Active Prompt</Badge>
        </div>

        <div class="rounded-lg bg-surface-gray-2 p-4 text-xs font-mono text-ink-gray-8 whitespace-pre-wrap max-h-80 overflow-y-auto leading-relaxed border">
{{ stats.knowledge_base }}
        </div>
      </div>
    </div>

    <!-- TAB 4: Automations & Pre-Approved Templates -->
    <div v-else-if="activeTab === 'automations'" class="flex-1 overflow-y-auto p-6 max-w-5xl mx-auto w-full space-y-6">
      <div>
        <h2 class="text-lg font-bold text-ink-gray-9">School Admission WhatsApp Automations</h2>
        <p class="text-xs text-ink-gray-5">Standardized message flows to engage parents at each step of the admission journey.</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="border rounded-xl p-4 bg-surface-white shadow-sm space-y-2">
          <div class="flex items-center justify-between">
            <span class="font-bold text-sm text-ink-gray-9">1. Instant Website Lead Welcome</span>
            <Badge theme="green" size="sm">Active</Badge>
          </div>
          <p class="text-xs text-ink-gray-6">Triggers immediately when a parent submits the admission inquiry form on the school website.</p>
          <div class="rounded bg-surface-gray-1 p-2.5 text-xs text-ink-gray-8 italic border">
            "Hello {{parent_name}}! Thank you for inquiring about admission for {{student_name}} for {{grade}} at IDPS Borivali. Our counseling desk has received your request. We invite you for a campus tour Monday–Saturday, 9:00 AM–3:30 PM."
          </div>
        </div>

        <div class="border rounded-xl p-4 bg-surface-white shadow-sm space-y-2">
          <div class="flex items-center justify-between">
            <span class="font-bold text-sm text-ink-gray-9">2. Campus Tour Appointment Confirmation</span>
            <Badge theme="green" size="sm">Active</Badge>
          </div>
          <p class="text-xs text-ink-gray-6">Sent when a counselor books a visit date and time with the parent.</p>
          <div class="rounded bg-surface-gray-1 p-2.5 text-xs text-ink-gray-8 italic border">
            "Dear {{parent_name}}, your campus visit to IDPS Borivali is confirmed for {{visit_date}} at {{visit_time}}. Location: Borivali West campus. Location link: https://maps.google.com/?q=IDPS+Borivali. See you soon!"
          </div>
        </div>

        <div class="border rounded-xl p-4 bg-surface-white shadow-sm space-y-2">
          <div class="flex items-center justify-between">
            <span class="font-bold text-sm text-ink-gray-9">3. Application Checklist & Documents Reminder</span>
            <Badge theme="green" size="sm">Active</Badge>
          </div>
          <p class="text-xs text-ink-gray-6">Assists parents with required enrollment documents for Grade 1–10 admissions.</p>
          <div class="rounded bg-surface-gray-1 p-2.5 text-xs text-ink-gray-8 italic border">
            "Dear {{parent_name}}, to finalize the admission application for {{student_name}}, please keep ready: 1) Birth Certificate, 2) Previous School Report Card, 3) 2 Passport Photos, 4) Address Proof. Reply here if you need any assistance."
          </div>
        </div>

        <div class="border rounded-xl p-4 bg-surface-white shadow-sm space-y-2">
          <div class="flex items-center justify-between">
            <span class="font-bold text-sm text-ink-gray-9">4. Admission Offer & Seat Confirmation</span>
            <Badge theme="green" size="sm">Active</Badge>
          </div>
          <p class="text-xs text-ink-gray-6">Sent when the principal approves admission and generates the offer letter.</p>
          <div class="rounded bg-surface-gray-1 p-2.5 text-xs text-ink-gray-8 italic border">
            "Congratulations! We are delighted to offer admission to {{student_name}} in {{grade}} at IDPS Borivali for AY 2026-27! Please complete the fee token payment before {{deadline}} to secure your seat."
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { call, Button, Badge, TextInput } from 'frappe-ui'
import { globalStore } from '@/stores/global'
import WhatsAppIcon from '@/components/Icons/WhatsAppIcon.vue'
import LucideMessageSquare from '~icons/lucide/message-square'
import LucideRadio from '~icons/lucide/radio'
import LucideBot from '~icons/lucide/bot'
import LucideWorkflow from '~icons/lucide/workflow'

const router = useRouter()
const { $socket } = globalStore()

const activeTab = ref('chats')
const loading = ref(false)
const savingAccount = ref(false)
const accountSavedMsg = ref('')
const loadingMessages = ref(false)
const sendingReply = ref(false)
const testingBot = ref(false)
const checkingMeta = ref(false)
const metaTestFeedback = ref(null)

const simulatingInquiry = ref(false)
const simName = ref('Meera Singhania')
const simPhone = ref('+91 98201 88776')
const simMessage = ref('Hi, I want to inquire about Grade 3 admission for my daughter Anaya for 2026-27. What are the school timings?')
const simFeedback = ref('')

const stats = ref({
  is_enabled: true,
  has_api_key: false,
  total_messages: 0,
  ai_replies_count: 0,
  counselor_replies_count: 0,
  conversations: [],
  knowledge_base: ''
})

const connection = ref({
  webhook_url: '',
  webhook_verify_token: '',
  has_active_account: false,
  account: null,
  has_groq_key: false,
  groq_model: 'llama-3.3-70b-versatile',
  lead_sync_endpoint: ''
})

const accountForm = ref({
  account_name: 'IDPS Borivali Official',
  phone_id: '',
  business_id: '',
  app_id: '',
  access_token: '',
  webhook_secret: ''
})

const selectedRecipient = ref(null)
const currentConv = ref(null)
const currentMessages = ref([])
const replyText = ref('')
const searchQuery = ref('')
const testQuery = ref('')
const testResult = ref('')
const testResultMode = ref('')
const chatScrollContainer = ref(null)

const tabs = computed(() => [
  { id: 'chats', label: 'Parent Chats & Transcripts', icon: LucideMessageSquare, badge: stats.value.conversations?.length || 0 },
  { id: 'connection', label: 'Real-Time Connection Setup', icon: LucideRadio },
  { id: 'bot', label: 'AI Counselor & Knowledge Base', icon: LucideBot },
  { id: 'automations', label: 'Automations & Templates', icon: LucideWorkflow }
])

const filteredConversations = computed(() => {
  if (!searchQuery.value.trim()) return stats.value.conversations || []
  const q = searchQuery.value.toLowerCase()
  return (stats.value.conversations || []).filter((c) => {
    return (
      c.parent_name?.toLowerCase().includes(q) ||
      c.phone_number?.includes(q) ||
      c.lead?.student_name?.toLowerCase().includes(q) ||
      c.lead?.grade_applying_for?.toLowerCase().includes(q)
    )
  })
})

async function fetchOverview() {
  loading.value = true
  try {
    const [resStats, resConn] = await Promise.all([
      call('crm.api.chatbot.get_chatbot_overview'),
      call('crm.api.chatbot.get_connection_details')
    ])
    if (resStats) {
      stats.value = resStats
      if (!selectedRecipient.value && resStats.conversations?.length) {
        selectConversation(resStats.conversations[0])
      }
    }
    if (resConn) {
      connection.value = resConn
      if (resConn.account) {
        accountForm.value.account_name = resConn.account.account_name || 'IDPS Borivali Official'
        accountForm.value.phone_id = resConn.account.phone_id || ''
        accountForm.value.business_id = resConn.account.business_id || ''
        accountForm.value.app_id = resConn.account.app_id || ''
      }
    }
  } catch (e) {
    console.error('Failed to fetch data', e)
  } finally {
    loading.value = false
  }
}

async function saveMetaAccount() {
  savingAccount.value = true
  accountSavedMsg.value = ''
  try {
    const res = await call('crm.api.chatbot.save_whatsapp_account', {
      account_name: accountForm.value.account_name,
      phone_id: accountForm.value.phone_id,
      business_id: accountForm.value.business_id,
      app_id: accountForm.value.app_id,
      access_token: accountForm.value.access_token,
      webhook_secret: accountForm.value.webhook_secret || null
    })
    if (res.status === 'success') {
      accountSavedMsg.value = '✓ Meta WhatsApp Account saved and connected!'
      await fetchOverview()
    }
  } catch (e) {
    accountSavedMsg.value = 'Error: ' + (e.messages?.[0] || e.message)
  } finally {
    savingAccount.value = false
  }
}

async function testMetaConnection() {
  checkingMeta.value = true
  metaTestFeedback.value = null
  try {
    const res = await call('crm.api.chatbot.check_meta_connection')
    metaTestFeedback.value = res
  } catch (e) {
    metaTestFeedback.value = {
      connected: false,
      error: e.messages?.[0] || e.message
    }
  } finally {
    checkingMeta.value = false
  }
}

async function selectConversation(conv) {
  selectedRecipient.value = conv.recipient_id
  currentConv.value = conv
  loadingMessages.value = true
  try {
    const res = await call('crm.api.chatbot.get_conversation_history', {
      recipient: conv.recipient_id
    })
    currentMessages.value = res || []
    scrollToBottom()
  } catch (e) {
    console.error('Failed to load conversation history', e)
  } finally {
    loadingMessages.value = false
  }
}

async function sendReply() {
  if (!replyText.value.trim() || !currentConv.value) return
  sendingReply.value = true
  try {
    await call('crm.api.chatbot.send_counselor_reply', {
      recipient: currentConv.value.recipient_id,
      message: replyText.value.trim(),
      lead_name: currentConv.value.lead?.name || null
    })
    replyText.value = ''
    await selectConversation(currentConv.value)
    currentConv.value.is_bot_paused = true
  } catch (e) {
    console.error('Failed to send reply', e)
  } finally {
    sendingReply.value = false
  }
}

async function toggleBotPause(conv) {
  const newStatus = !conv.is_bot_paused
  try {
    const res = await call('crm.api.chatbot.toggle_bot_pause', {
      recipient: conv.recipient_id,
      paused: newStatus
    })
    conv.is_bot_paused = res.is_bot_paused
  } catch (e) {
    console.error('Failed to toggle bot pause', e)
  }
}

async function simulateInquiry() {
  if (!simPhone.value.trim() || !simMessage.value.trim()) return
  simulatingInquiry.value = true
  simFeedback.value = ''
  try {
    const res = await call('crm.api.chatbot.simulate_parent_inquiry', {
      phone_number: simPhone.value.trim(),
      parent_name: simName.value.trim(),
      message: simMessage.value.trim()
    })
    if (res.status === 'success') {
      simFeedback.value = `✓ Inquiry simulated! Created Lead: ${res.lead}. Switching to Live Chats...`
      await fetchOverview()
      setTimeout(() => {
        activeTab.value = 'chats'
        const matchingConv = (stats.value.conversations || []).find(c => c.recipient_id === res.profile)
        if (matchingConv) {
          selectConversation(matchingConv)
        }
      }, 700)
    }
  } catch (e) {
    simFeedback.value = 'Error: ' + (e.messages?.[0] || e.message)
  } finally {
    simulatingInquiry.value = false
  }
}

async function runTestQuery() {
  if (!testQuery.value.trim()) return
  testingBot.value = true
  testResult.value = ''
  try {
    const res = await call('crm.api.chatbot.test_admissions_bot', {
      query: testQuery.value.trim()
    })
    testResult.value = res.reply || res.error || 'No response.'
    testResultMode.value = res.mode === 'live' ? 'Live Groq Llama 3.3 70B' : 'Simulated Response'
  } catch (e) {
    testResult.value = 'Error running test query: ' + e.message
  } finally {
    testingBot.value = false
  }
}

function openLeadRecord(leadName) {
  router.push({ name: 'Lead', params: { leadId: leadName } })
}

function copyToClipboard(text) {
  if (!text) return
  navigator.clipboard.writeText(text)
  alert('Copied to clipboard: ' + text)
}

function scrollToBottom() {
  nextTick(() => {
    if (chatScrollContainer.value) {
      chatScrollContainer.value.scrollTop = chatScrollContainer.value.scrollHeight
    }
  })
}

function formatTimeAgo(dateStr) {
  if (!dateStr) return ''
  const diff = Date.now() - new Date(dateStr).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'Just now'
  if (mins < 60) return `${mins}m ago`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}h ago`
  return `${Math.floor(hours / 24)}d ago`
}

function formatMessageTime(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

function onRealtimeMessage(data) {
  // If we receive a realtime message update, refresh conversations and current chat if open
  fetchOverview()
  if (selectedRecipient.value) {
    loadConversation(selectedRecipient.value)
  }
}

onMounted(() => {
  fetchOverview()
  if ($socket) {
    $socket.on('whatsapp_message', onRealtimeMessage)
  }
})

onUnmounted(() => {
  if ($socket) {
    $socket.off('whatsapp_message', onRealtimeMessage)
  }
})
</script>
