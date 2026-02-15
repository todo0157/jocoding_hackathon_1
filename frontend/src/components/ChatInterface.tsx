'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Scale, Loader2, Trash2 } from 'lucide-react'
import { sendChatMessage, ChatMessage, ContractContext, CitedCase } from '@/lib/api'

interface ChatInterfaceProps {
  contractContext?: ContractContext
}

interface Message extends ChatMessage {
  cited_cases?: CitedCase[]
}

const STORAGE_KEY = 'contractpilot_chat_history'

export function ChatInterface({ contractContext }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // localStorage에서 대화 히스토리 로드
  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      try {
        setMessages(JSON.parse(saved))
      } catch (e) {
        console.error('Failed to load chat history:', e)
      }
    }
  }, [])

  // 메시지 변경 시 localStorage에 저장
  useEffect(() => {
    if (messages.length > 0) {
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
      // API 호출을 위한 히스토리 준비 (cited_cases 제외)
      const historyForApi: ChatMessage[] = [...messages, userMessage].map(m => ({
        role: m.role,
        content: m.content
      }))

      const response = await sendChatMessage(
        userMessage.content,
        historyForApi.slice(0, -1), // 현재 메시지 제외
        contractContext
      )

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.reply,
        cited_cases: response.cited_cases
      }
      setMessages(prev => [...prev, assistantMessage])
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
    setMessages([])
    localStorage.removeItem(STORAGE_KEY)
  }

  return (
    <div className="flex flex-col h-[600px] bg-white rounded-2xl shadow-sm overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-primary-600 text-white">
        <div className="flex items-center gap-2">
          <Scale className="w-5 h-5" />
          <span className="font-semibold">법률 상담 AI</span>
        </div>
        {messages.length > 0 && (
          <button
            onClick={clearHistory}
            className="p-1.5 hover:bg-primary-700 rounded transition"
            title="대화 초기화"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Contract Context Banner */}
      {contractContext?.contract_type && (
        <div className="px-4 py-2 bg-blue-50 border-b text-sm text-blue-700">
          분석 중인 계약서: <span className="font-medium">{contractContext.contract_type}</span>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-8">
            <Bot className="w-12 h-12 mx-auto mb-3 text-gray-300" />
            <p className="font-medium">안녕하세요! 계약 관련 질문을 도와드리겠습니다.</p>
            <p className="text-sm mt-1">예: "손해배상 조항이 불리한 것 같아요"</p>
          </div>
        )}

        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex gap-3 ${message.role === 'user' ? 'flex-row-reverse' : ''}`}
          >
            {/* Avatar */}
            <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
              message.role === 'user' ? 'bg-primary-100' : 'bg-gray-100'
            }`}>
              {message.role === 'user' ? (
                <User className="w-4 h-4 text-primary-600" />
              ) : (
                <Bot className="w-4 h-4 text-gray-600" />
              )}
            </div>

            {/* Message Content */}
            <div className={`flex flex-col max-w-[75%] ${message.role === 'user' ? 'items-end' : ''}`}>
              <div className={`px-4 py-2 rounded-2xl ${
                message.role === 'user'
                  ? 'bg-primary-600 text-white rounded-tr-sm'
                  : 'bg-gray-100 text-gray-800 rounded-tl-sm'
              }`}>
                <p className="whitespace-pre-wrap">{message.content}</p>
              </div>

              {/* Cited Cases */}
              {message.cited_cases && message.cited_cases.length > 0 && (
                <div className="mt-2 p-3 bg-purple-50 rounded-lg text-sm max-w-full">
                  <p className="text-purple-700 font-medium mb-1">📎 관련 판례</p>
                  {message.cited_cases.map((c, i) => (
                    <div key={i} className="text-purple-600 mt-1">
                      <span className="font-medium">{c.case_number}</span>
                      <span className="text-purple-500 ml-1">- {c.summary}</span>
                    </div>
                  ))}
                </div>
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
            placeholder="계약 관련 질문을 입력하세요..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="px-4 py-2 bg-primary-600 text-white rounded-full hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        <p className="text-xs text-gray-400 mt-2 text-center">
          본 상담은 법률 자문을 대체하지 않습니다.
        </p>
      </form>
    </div>
  )
}
