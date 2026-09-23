import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Zap, RefreshCw } from 'lucide-react'
import { sendCopilotMessage } from '../api/client.js'
import EvidencePanel from '../components/EvidencePanel.jsx'
import clsx from 'clsx'

const QUICK_ACTIONS = [
  { label: 'Why is my task delayed?',         msg: 'Why is my task taking longer today?' },
  { label: 'Is my machine normal?',           msg: 'Is the machine operating normally?' },
  { label: 'What should I know before continuing?', msg: 'What should I know before continuing the current task?' },
  { label: 'Explain my safety score',         msg: 'Explain my current safety score.' },
  { label: 'What if rain starts?',            msg: 'What happens if rain starts now?' },
  { label: 'Generate shift handover',         msg: 'Generate shift handover for this machine.' },
  { label: 'Something feels wrong',           msg: 'Something feels wrong with the machine.' },
  { label: 'Call CAT Expert',                 msg: 'I need to connect to a CAT expert.' },
]

function Message({ msg }) {
  const isUser = msg.role === 'user'
  return (
    <div className={clsx('flex gap-3', isUser && 'flex-row-reverse')}>
      <div className={clsx(
        'w-8 h-8 rounded-full flex items-center justify-center shrink-0',
        isUser ? 'bg-surface-500' : 'bg-cat-500'
      )}>
        {isUser ? <User size={14} className="text-gray-200" /> : <Bot size={14} className="text-surface-900" />}
      </div>
      <div className={clsx(
        'max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed',
        isUser ? 'bg-surface-500 text-gray-200 rounded-tr-sm' : 'bg-surface-600 border border-surface-500 text-gray-200 rounded-tl-sm'
      )}>
        {/* Render markdown-ish bold */}
        {msg.content.split('\n').map((line, i) => {
          const parts = line.split(/\*\*(.*?)\*\*/g)
          return (
            <p key={i} className={i > 0 ? 'mt-2' : ''}>
              {parts.map((p, j) => j % 2 === 1 ? <strong key={j} className="font-semibold text-white">{p}</strong> : p)}
            </p>
          )
        })}

        {/* Tool calls */}
        {msg.tools_called?.length > 0 && (
          <div className="mt-2 pt-2 border-t border-surface-400 flex flex-wrap gap-1">
            {msg.tools_called.map((t, i) => (
              <span key={i} className="text-xs px-1.5 py-0.5 bg-surface-500 rounded text-surface-100 font-mono">
                {t.tool}
              </span>
            ))}
          </div>
        )}

        {/* Feature 10 — Evidence panel */}
        {!isUser && msg.evidence && <EvidencePanel evidence={msg.evidence} />}
      </div>
    </div>
  )
}

export default function CopilotPage({ machineId }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: `CAT Smart Operator Copilot online.\n\nI have access to live machine data, ML predictions, safety status, weather forecasts, and XAI explanations for **${machineId}**.\n\nHow can I help?`,
    },
  ])
  const [input, setInput]       = useState('')
  const [sending, setSending]   = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const send = async (text) => {
    const userMsg = text || input.trim()
    if (!userMsg || sending) return
    setInput('')
    setMessages(m => [...m, { role: 'user', content: userMsg }])
    setSending(true)
    try {
      const res = await sendCopilotMessage({ message: userMsg, machine_id: machineId })
      setMessages(m => [...m, {
        role: 'assistant',
        content: res.response,
        tools_called: res.tools_called,
        evidence: res.evidence,
      }])
    } catch (e) {
      setMessages(m => [...m, {
        role: 'assistant',
        content: `Sorry — I couldn't reach the backend. Please check the server is running. (${e.message})`,
      }])
    } finally {
      setSending(false)
    }
  }

  const reset = () => {
    setMessages([{
      role: 'assistant',
      content: `CAT Smart Operator Copilot ready for **${machineId}**. How can I help?`,
    }])
  }

  return (
    <div className="flex flex-col h-[calc(100vh-7rem)] max-w-3xl mx-auto">

      {/* Header */}
      <div className="flex items-center justify-between mb-4 shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-cat-500 rounded-full flex items-center justify-center">
            <Bot size={18} className="text-surface-900" />
          </div>
          <div>
            <div className="font-semibold text-white">AI Copilot</div>
            <div className="text-xs text-surface-100">Tool-calling · {machineId}</div>
          </div>
          <span className="w-2 h-2 rounded-full bg-green-400 pulse-dot" />
        </div>
        <button onClick={reset} className="btn-secondary text-xs">
          <RefreshCw size={12} /> New Session
        </button>
      </div>

      {/* Quick actions */}
      <div className="flex flex-wrap gap-2 mb-4 shrink-0">
        {QUICK_ACTIONS.map(qa => (
          <button key={qa.label} onClick={() => send(qa.msg)}
            className="inline-flex items-center gap-1 px-2.5 py-1 bg-surface-600 border border-surface-400 rounded-full text-xs text-gray-300 hover:border-cat-500 hover:text-cat-500 transition-colors">
            <Zap size={10} />
            {qa.label}
          </button>
        ))}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-1">
        {messages.map((msg, i) => <Message key={i} msg={msg} />)}
        {sending && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-cat-500 flex items-center justify-center shrink-0">
              <Bot size={14} className="text-surface-900" />
            </div>
            <div className="bg-surface-600 border border-surface-500 rounded-2xl rounded-tl-sm px-4 py-3">
              <div className="flex gap-1">
                {[0, 1, 2].map(i => (
                  <div key={i} className="w-1.5 h-1.5 rounded-full bg-surface-200 animate-bounce"
                    style={{ animationDelay: `${i * 0.15}s` }} />
                ))}
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="mt-4 flex gap-2 shrink-0">
        <input
          className="input flex-1"
          placeholder={`Ask about ${machineId}…`}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && !e.shiftKey && send()}
          disabled={sending}
        />
        <button
          onClick={() => send()}
          disabled={!input.trim() || sending}
          className="btn-primary px-4 disabled:opacity-40"
        >
          <Send size={16} />
        </button>
      </div>

      <p className="text-xs text-surface-200 text-center mt-2 shrink-0">
        AI uses real machine data via tool calls. Safety decisions remain with the deterministic engine.
      </p>
    </div>
  )
}
