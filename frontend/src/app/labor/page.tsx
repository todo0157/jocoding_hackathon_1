'use client'

import Link from 'next/link'
import { LaborChatInterface } from '@/components/LaborChatInterface'
import { Briefcase, FileText, ArrowLeft, Shield, Clock, Users } from 'lucide-react'

export default function LaborPage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-gray-100">
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
              <Briefcase className="w-6 h-6 text-blue-600" />
              <h1 className="text-xl font-bold text-gray-900">노동톡</h1>
            </div>
          </div>
          <Link
            href="/"
            className="flex items-center gap-2 text-sm text-gray-600 hover:text-blue-600 transition"
          >
            <FileText className="w-4 h-4" />
            계약서 분석
          </Link>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Info Banner */}
        <div className="mb-6 p-4 bg-blue-600 rounded-xl text-white">
          <h2 className="font-semibold text-lg mb-1">AI 노동상담 서비스</h2>
          <p className="text-sm text-blue-100">
            임금체불, 부당해고, 직장 내 괴롭힘 등 노동 관련 고민을 AI가 상담해드립니다.
            <br />
            필요시 전문 노무사 연결도 도와드려요.
          </p>
        </div>

        {/* Chat Interface */}
        <LaborChatInterface />

        {/* Features */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-white rounded-xl shadow-sm flex items-start gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Shield className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="font-medium text-gray-800">법률 근거 기반</p>
              <p className="text-sm text-gray-600">근로기준법 등 관련 법률을 기반으로 안내</p>
            </div>
          </div>
          <div className="p-4 bg-white rounded-xl shadow-sm flex items-start gap-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <Clock className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="font-medium text-gray-800">24시간 상담</p>
              <p className="text-sm text-gray-600">언제든지 편하게 상담 가능</p>
            </div>
          </div>
          <div className="p-4 bg-white rounded-xl shadow-sm flex items-start gap-3">
            <div className="p-2 bg-amber-100 rounded-lg">
              <Users className="w-5 h-5 text-amber-600" />
            </div>
            <div>
              <p className="font-medium text-gray-800">전문가 연결</p>
              <p className="text-sm text-gray-600">필요시 노무사 무료 상담 연결</p>
            </div>
          </div>
        </div>

        {/* Tips */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-white rounded-xl shadow-sm border-l-4 border-blue-500">
            <p className="font-medium text-gray-800 mb-1">💡 질문 예시</p>
            <p className="text-sm text-gray-600">"3개월째 월급을 못 받았어요"</p>
          </div>
          <div className="p-4 bg-white rounded-xl shadow-sm border-l-4 border-blue-500">
            <p className="font-medium text-gray-800 mb-1">💡 질문 예시</p>
            <p className="text-sm text-gray-600">"갑자기 해고 통보를 받았어요"</p>
          </div>
          <div className="p-4 bg-white rounded-xl shadow-sm border-l-4 border-blue-500">
            <p className="font-medium text-gray-800 mb-1">💡 질문 예시</p>
            <p className="text-sm text-gray-600">"상사가 계속 폭언을 해요"</p>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-white border-t mt-12">
        <div className="max-w-4xl mx-auto px-4 py-6 text-center text-gray-500 text-sm">
          <p>노동톡 - AI 노동상담 서비스</p>
          <p className="mt-1">본 서비스는 법률 자문을 대체하지 않습니다. 정확한 상담은 전문 노무사와 상담하세요.</p>
        </div>
      </footer>
    </main>
  )
}
