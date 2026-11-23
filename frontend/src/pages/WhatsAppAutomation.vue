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
            <h1 class="text-lg font-semibold text-ink-gray-9">WhatsApp & Bot</h1>
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
          <Button variant="solid" theme="green" @click="activeTab = 'bot'">
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
                {{ conv.last_message }}
              </div>
            </button>
          </div>
        </div>

        <!-- Right Column: Interactive Chat & Counselor Intervention Panel -->
        <div v-if="currentConv" class="flex-1 flex flex-col bg-surface-white overflow-hidden">
          <!-- Chat Header Bar -->
          <div class="flex items-center justify-between border-b px-5 py-3 bg-surface-white">
            <div class="flex items-center gap-3">
              <div class="size-10 rounded-full bg-emerald-600/10 text-emerald-700 font-bold flex items-center justify-center text-sm">
                {{ (currentConv.parent_name || 'Parent').charAt(0) }}
              </div>
              <div>
                <div class="flex items-center gap-2">
                  <h2 class="text-sm font-bold text-ink-gray-9">{{ currentConv.parent_name }}</h2>
                  <span class="text-xs font-mono text-ink-gray-5">{{ currentConv.phone_number }}</span>
                  <Badge v-if="currentConv.is_bot_paused" theme="amber" size="sm">
                    AI Paused (Counselor Handling)
                  </Badge>
                  <Badge v-else theme="green" size="sm">
                    AI Auto-Reply Active
                  </Badge>
                </div>
                <div class="text-xs text-ink-gray-5 flex items-center gap-3 mt-0.5">
                  <span v-if="currentConv.lead?.student_name">Child: <strong>{{ currentConv.lead.student_name }}</strong></span>
                  <span v-if="currentConv.lead?.grade_applying_for">Grade: <strong>{{ currentConv.lead.grade_applying_for }}</strong></span>
                  <span v-if="currentConv.lead?.lead_status" class="capitalize">Status: <strong>{{ currentConv.lead.lead_status }}</strong></span>
                </div>
              </div>
            </div>

            <!-- Action buttons -->
            <div class="flex items-center gap-2">
              <Button
                v-if="currentConv.lead?.name"
                variant="outline"
                size="sm"
                icon-left="lucide-external-link"
                @click="openLeadRecord(currentConv.lead.name)"
              >
                Open Lead
              </Button>

              <Button
                size="sm"
                :variant="currentConv.is_bot_paused ? 'solid' : 'outline'"
                :theme="currentConv.is_bot_paused ? 'green' : 'gray'"
                @click="toggleBotPause(currentConv)"
              >
                {{ currentConv.is_bot_paused ? 'Resume AI Chatbot' : 'Pause AI (Take Over)' }}
              </Button>
            </div>
          </div>

          <!-- Messages Scroll View -->
          <div ref="chatScrollContainer" class="flex-1 overflow-y-auto p-5 space-y-3 bg-surface-gray-1">
            <div v-if="loadingMessages" class="flex justify-center p-4 text-xs text-ink-gray-5">
              Loading conversation transcript...
            </div>

            <div
              v-for="msg in currentMessages"
              :key="msg.name"
              class="flex flex-col"
              :class="msg.direction === 'inbound' ? 'items-start' : 'items-end'"
            >
              <div class="text-[10px] text-ink-gray-4 mb-1 px-1">
                <span v-if="msg.direction === 'inbound'">Parent ({{ msg.sender_phone }})</span>
                <span v-else-if="msg.sender_type === 'ai_bot'" class="text-emerald-700 font-semibold">🤖 IDPS AI Counselor</span>
                <span v-else class="text-blue-700 font-semibold">👤 Admissions Officer</span>
                · {{ formatMessageTime(msg.timestamp) }}
              </div>

              <div
                class="max-w-[75%] rounded-2xl p-3.5 text-xs sm:text-sm leading-relaxed shadow-sm whitespace-pre-wrap"
                :class="msg.direction === 'inbound'
                  ? 'bg-surface-white text-ink-gray-9 border rounded-tl-sm'
                  : msg.sender_type === 'ai_bot'
                    ? 'bg-emerald-50 text-emerald-950 border border-emerald-200 rounded-tr-sm'
                    : 'bg-blue-600 text-white rounded-tr-sm'"
              >
                {{ msg.content }}
              </div>

              <!-- Extra Meta Information Badge for Lead Fields Auto-Captured -->
              <div v-if="msg.extra_info" class="mt-1 text-[10px] text-ink-gray-5 bg-surface-white border rounded px-1.5 py-0.5">
                {{ msg.extra_info }}
              </div>
            </div>
          </div>

          <!-- Counselor Live Reply Composer -->
          <div class="p-3 border-t bg-surface-white">
            <div v-if="!currentConv.is_bot_paused" class="mb-2 text-[11px] text-amber-700 bg-amber-50 border border-amber-200 rounded px-2 py-1 flex items-center justify-between">
              <span>💡 Sending a manual message will automatically pause AI replies for 2 hours so you can speak directly with the parent.</span>
            </div>

            <div class="flex items-end gap-2">
              <textarea
                v-model="replyText"
                rows="2"
                class="flex-1 rounded-lg border border-outline-gray-2 p-2.5 text-xs sm:text-sm focus:border-emerald-600 focus:outline-none resize-none"
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

    <!-- TAB 2: AI Counselor Knowledge Base & Live Sandbox Simulator -->
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { call, Button, Badge, TextInput } from 'frappe-ui'
import { globalStore } from '@/stores/global'
import WhatsAppIcon from '@/components/Icons/WhatsAppIcon.vue'
import LucideMessageSquare from '~icons/lucide/message-square'
import LucideBot from '~icons/lucide/bot'

const router = useRouter()
const { $socket } = globalStore()

const activeTab = ref('chats')
const loading = ref(false)
const loadingMessages = ref(false)
const sendingReply = ref(false)
const testingBot = ref(false)

const simulatingInquiry = ref(false)
const simName = ref('Meera Singhania')
const simPhone = ref('+91 98201 88776')
const simMessage = ref('Hi, I want to inquire about Grade 3 admission for my daughter Anaya for 2026-27. What are the school timings and transport facilities?')
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
  has_active_account: false,
  has_groq_key: false,
  groq_model: 'llama-3.3-70b-versatile',
  lead_sync_endpoint: ''
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
  { id: 'bot', label: 'AI Counselor & Knowledge Base', icon: LucideBot }
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
    }
  } catch (e) {
    console.error('Failed to fetch data', e)
  } finally {
    loading.value = false
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

function onRealtimeMessage() {
  fetchOverview()
  if (currentConv.value) {
    selectConversation(currentConv.value)
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
