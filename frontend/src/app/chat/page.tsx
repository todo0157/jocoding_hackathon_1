'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { ChatInterface } from '@/components/ChatInterface'
import { Scale, FileText, ArrowLeft } from 'lucide-react'
import { ContractContext } from '@/lib/api'

const CONTRACT_CONTEXT_KEY = 'contractpilot_analysis_result'

export default function ChatPage() {
  const [contractContext, setContractContext] = useState<ContractContext | undefined>()

  // localStorage에서 분석 결과 로드
  useEffect(() => {
    const saved = localStorage.getItem(CONTRACT_CONTEXT_KEY)
    if (saved) {
      try {
        const data = JSON.parse(saved)
        setContractContext({
          contract_type: data.contract_type,
          summary: data.summary,
          high_risk_clauses: data.clauses
            ?.filter((c: any) => c.analysis?.risk_score >= 6)
            ?.map((c: any) => ({
              title: c.title,
              summary: c.analysis?.summary
            }))
        })
      } catch (e) {
        console.error('Failed to load contract context:', e)
      }
    }
  }, [])

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link
              href="/"
              className="flex items-center gap-1 text-gray-500 hover:text-gray-700 transition"
            >
              <ArrowLeft className="w-4 h-4" />
              <span className="text-sm">돌아가기</span>
            </Link>
            <div className="flex items-center gap-2">
              <Scale className="w-6 h-6 text-primary-600" />
              <h1 className="text-xl font-bold text-gray-900">법률 상담</h1>
            </div>
          </div>
          <Link
            href="/"
            className="flex items-center gap-2 text-sm text-gray-600 hover:text-primary-600 transition"
          >
            <FileText className="w-4 h-4" />
            계약서 분석
          </Link>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Info Banner */}
        <div className="mb-6 p-4 bg-blue-50 rounded-xl border border-blue-100">
          <h2 className="font-semibold text-blue-800 mb-1">AI 법률 상담사</h2>
          <p className="text-sm text-blue-600">
            계약서 관련 궁금한 점을 질문해보세요. 관련 판례를 기반으로 답변해드립니다.
          </p>
        </div>

        {/* Chat Interface */}
        <ChatInterface contractContext={contractContext} />

        {/* Tips */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-white rounded-xl shadow-sm">
            <p className="font-medium text-gray-800 mb-1">💡 질문 예시</p>
            <p className="text-sm text-gray-600">"손해배상 조항이 불리한 것 같아요"</p>
          </div>
          <div className="p-4 bg-white rounded-xl shadow-sm">
            <p className="font-medium text-gray-800 mb-1">💡 질문 예시</p>
            <p className="text-sm text-gray-600">"경업금지 조항 기간이 너무 길어요"</p>
          </div>
          <div className="p-4 bg-white rounded-xl shadow-sm">
            <p className="font-medium text-gray-800 mb-1">💡 질문 예시</p>
            <p className="text-sm text-gray-600">"위약금 조항을 수정하고 싶어요"</p>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-white border-t mt-12">
        <div className="max-w-4xl mx-auto px-4 py-6 text-center text-gray-500 text-sm">
          <p>ContractPilot - 조코딩 x OpenAI x 프라이머 해커톤</p>
          <p className="mt-1">본 서비스는 법률 자문을 대체하지 않습니다.</p>
        </div>
      </footer>
    </main>
  )
}
