'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Briefcase, Loader2, Trash2, UserCheck } from 'lucide-react'
import { sendLaborChatMessage, ChatMessage, LaborConsultationInfo, CitedCase } from '@/lib/api'
import { ExpertConnectModal } from './ExpertConnectModal'

interface Message extends ChatMessage {
  cited_cases?: CitedCase[]
  needs_expert?: boolean
}

const STORAGE_KEY = 'labortalk_chat_history'

const INITIAL_MESSAGE = `안녕하세요! 노동톡입니다 👋

직장에서 겪고 계신 어려움이 있으신가요?
임금체불, 부당해고, 직장 내 괴롭힘 등
노동 관련 고민이라면 무엇이든 편하게 말씀해주세요.

어떤 상황인지 들려주시겠어요?`

export function LaborChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: INITIAL_MESSAGE }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [showExpertModal, setShowExpertModal] = useState(false)
  const [consultationSummary, setConsultationSummary] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // localStorage에서 대화 히스토리 로드
  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      try {
        const parsed = JSON.parse(saved)
        if (parsed.length > 0) {
          setMessages(parsed)
        }
      } catch (e) {
        console.error('Failed to load chat history:', e)
      }
    }
  }, [])

  // 메시지 변경 시 localStorage에 저장
  useEffect(() => {
    if (messages.length > 1) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(messages))
    }
  }, [messages])

  // 스크롤 자동 이동
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage: Message = { role: 'user', content: input.trim() }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const historyForApi: ChatMessage[] = [...messages, userMessage]
        .map(m => ({ role: m.role, content: m.content }))

      const response = await sendLaborChatMessage(
        userMessage.content,
        historyForApi.slice(0, -1)
      )

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.reply,
        cited_cases: response.cited_cases,
        needs_expert: response.needs_expert
      }
      setMessages(prev => [...prev, assistantMessage])

      // 상담 요약 업데이트
      if (response.needs_expert) {
        const summary = messages
          .filter(m => m.role === 'user')
          .map(m => m.content)
          .join('\n')
        setConsultationSummary(summary + '\n' + userMessage.content)
      }
    } catch (error: any) {
      const errorMessage: Message = {
        role: 'assistant',
        content: `죄송합니다. 오류가 발생했습니다: ${error.message}`
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const clearHistory = () => {
    setMessages([{ role: 'assistant', content: INITIAL_MESSAGE }])
    localStorage.removeItem(STORAGE_KEY)
  }

  const handleExpertConnect = () => {
    const summary = messages
      .filter(m => m.role === 'user')
      .map(m => m.content)
      .join('\n')
    setConsultationSummary(summary)
    setShowExpertModal(true)
  }

  return (
    <>
      <div className="flex flex-col h-[600px] bg-white rounded-2xl shadow-sm overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 bg-blue-600 text-white">
          <div className="flex items-center gap-2">
            <Briefcase className="w-5 h-5" />
            <span className="font-semibold">노동톡 - AI 노동상담</span>
          </div>
          <div className="flex items-center gap-2">
            {messages.length > 1 && (
              <button
                onClick={clearHistory}
                className="p-1.5 hover:bg-blue-700 rounded transition"
                title="대화 초기화"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>

        {/* Expert Connect Banner */}
        <button
          onClick={handleExpertConnect}
          className="px-4 py-2 bg-amber-50 border-b text-sm text-amber-700 hover:bg-amber-100 transition flex items-center justify-center gap-2"
        >
          <UserCheck className="w-4 h-4" />
          <span>전문 노무사 무료 상담 연결받기</span>
        </button>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex gap-3 ${message.role === 'user' ? 'flex-row-reverse' : ''}`}
            >
              {/* Avatar */}
              <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                message.role === 'user' ? 'bg-blue-100' : 'bg-gray-100'
              }`}>
                {message.role === 'user' ? (
                  <User className="w-4 h-4 text-blue-600" />
                ) : (
                  <Bot className="w-4 h-4 text-gray-600" />
                )}
              </div>

              {/* Message Content */}
              <div className={`flex flex-col max-w-[75%] ${message.role === 'user' ? 'items-end' : ''}`}>
                <div className={`px-4 py-2 rounded-2xl ${
                  message.role === 'user'
                    ? 'bg-blue-600 text-white rounded-tr-sm'
                    : 'bg-gray-100 text-gray-800 rounded-tl-sm'
                }`}>
                  <p className="whitespace-pre-wrap">{message.content}</p>
                </div>

                {/* Cited Cases */}
                {message.cited_cases && message.cited_cases.length > 0 && (
                  <div className="mt-2 p-3 bg-blue-50 rounded-lg text-sm max-w-full">
                    <p className="text-blue-700 font-medium mb-1">📎 관련 판례</p>
                    {message.cited_cases.map((c, i) => (
                      <div key={i} className="text-blue-600 mt-1">
                        <span className="font-medium">{c.case_number}</span>
                        <span className="text-blue-500 ml-1">- {c.summary}</span>
                      </div>
                    ))}
                  </div>
                )}

                {/* Expert Connect Suggestion */}
                {message.needs_expert && (
                  <button
                    onClick={handleExpertConnect}
                    className="mt-2 px-4 py-2 bg-amber-500 text-white rounded-lg text-sm font-medium hover:bg-amber-600 transition"
                  >
                    👉 전문 노무사 무료 상담 신청하기
                  </button>
                )}
              </div>
            </div>
          ))}

          {/* Loading */}
          {isLoading && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center">
                <Bot className="w-4 h-4 text-gray-600" />
              </div>
              <div className="px-4 py-2 bg-gray-100 rounded-2xl rounded-tl-sm">
                <Loader2 className="w-5 h-5 animate-spin text-gray-500" />
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <form onSubmit={handleSubmit} className="p-4 border-t bg-gray-50">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="노동 관련 고민을 말씀해주세요..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="px-4 py-2 bg-blue-600 text-white rounded-full hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
          <p className="text-xs text-gray-400 mt-2 text-center">
            본 상담은 법률 자문을 대체하지 않습니다. 정확한 상담은 전문 노무사와 상담하세요.
          </p>
        </form>
      </div>

      {/* Expert Connect Modal */}
      {showExpertModal && (
        <ExpertConnectModal
          onClose={() => setShowExpertModal(false)}
          consultationSummary={consultationSummary}
        />
      )}
    </>
  )
}
