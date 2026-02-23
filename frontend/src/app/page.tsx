'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { FileUpload } from '@/components/FileUpload'
import { AnalysisResult } from '@/components/AnalysisResult'
import { LoadingState } from '@/components/LoadingState'
import { analyzeContract } from '@/lib/api'
import { FileText, Shield, Scale, MessageCircle, Briefcase, Lock } from 'lucide-react'

const CONTRACT_CONTEXT_KEY = 'contractpilot_analysis_result'

export default function Home() {
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const handleFileUpload = async (file: File) => {
    setIsAnalyzing(true)
    setError(null)
    setResult(null)

    try {
      const data = await analyzeContract(file)
      setResult(data)
      // 분석 결과를 localStorage에 저장 (챗봇에서 사용)
      localStorage.setItem(CONTRACT_CONTEXT_KEY, JSON.stringify(data))
    } catch (err: any) {
      setError(err.message || '분석 중 오류가 발생했습니다.')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleReset = () => {
    setResult(null)
    setError(null)
  }

  return (
    <main className="min-h-screen">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Scale className="w-8 h-8 text-primary-600" />
            <h1 className="text-2xl font-bold text-gray-900">ContractPilot</h1>
          </div>
          <nav className="flex items-center gap-4">
            <Link
              href="/labor"
              className="flex items-center gap-2 px-4 py-2 text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition"
            >
              <Briefcase className="w-5 h-5" />
              <span className="font-medium">노동상담</span>
            </Link>
            <Link
              href="/chat"
              className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-primary-600 hover:bg-gray-50 rounded-lg transition"
            >
              <MessageCircle className="w-5 h-5" />
              <span className="font-medium">계약상담</span>
            </Link>
          </nav>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {!result && !isAnalyzing && (
          <>
            {/* Hero Section */}
            <section className="text-center mb-12">
              <h2 className="text-4xl font-bold text-gray-900 mb-4">
                계약서 검토, <span className="text-primary-600">AI가 10분 안에</span>
              </h2>
              <p className="text-xl text-gray-600 mb-8">
                한국 판례 기반으로 위험 조항을 찾아내고 수정안을 제안합니다
              </p>

              {/* Features */}
              <div className="grid md:grid-cols-4 gap-6 mb-12">
                <div className="bg-white p-6 rounded-xl shadow-sm">
                  <FileText className="w-10 h-10 text-primary-600 mx-auto mb-4" />
                  <h3 className="font-semibold text-lg mb-2">조항별 분석</h3>
                  <p className="text-gray-600 text-sm">
                    계약서를 조항별로 분리하여 각각의 위험도를 분석합니다
                  </p>
                </div>
                <div className="bg-white p-6 rounded-xl shadow-sm">
                  <Scale className="w-10 h-10 text-primary-600 mx-auto mb-4" />
                  <h3 className="font-semibold text-lg mb-2">판례 기반 근거</h3>
                  <p className="text-gray-600 text-sm">
                    대법원 판례를 인용하여 법적 근거를 제시합니다
                  </p>
                </div>
                <div className="bg-white p-6 rounded-xl shadow-sm">
                  <Shield className="w-10 h-10 text-primary-600 mx-auto mb-4" />
                  <h3 className="font-semibold text-lg mb-2">수정안 제안</h3>
                  <p className="text-gray-600 text-sm">
                    위험한 조항에 대해 공정한 수정안을 자동 생성합니다
                  </p>
                </div>
                <div className="bg-white p-6 rounded-xl shadow-sm border-2 border-green-200">
                  <Lock className="w-10 h-10 text-green-600 mx-auto mb-4" />
                  <h3 className="font-semibold text-lg mb-2">개인정보 보호</h3>
                  <p className="text-gray-600 text-sm">
                    개인정보 자동 익명화로 안전하게 분석합니다
                  </p>
                </div>
              </div>
            </section>

            {/* Upload Section */}
            <FileUpload onUpload={handleFileUpload} />

            {/* Privacy Notice */}
            <div className="mt-4 flex items-center justify-center gap-2 text-sm text-gray-500">
              <Lock className="w-4 h-4 text-green-600" />
              <span>
                업로드된 문서의 개인정보(이름, 연락처, 주소 등)는 자동 익명화 처리됩니다
              </span>
            </div>

            {error && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-center">
                {error}
              </div>
            )}
          </>
        )}

        {isAnalyzing && <LoadingState />}

        {result && (
          <AnalysisResult data={result} onReset={handleReset} />
        )}
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white mt-12">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="grid md:grid-cols-2 gap-8">
            <div>
              <h4 className="font-semibold text-lg mb-3">ContractPilot</h4>
              <p className="text-gray-400 text-sm">
                AI 기반 계약서 분석 도구로, 계약 검토 시간을 단축하고
                위험 요소를 사전에 파악할 수 있도록 도와드립니다.
              </p>
            </div>
            <div>
              <h4 className="font-semibold text-lg mb-3">면책 조항</h4>
              <p className="text-gray-400 text-sm">
                본 서비스는 AI 기반 <strong className="text-amber-400">정보 제공 도구</strong>로서 법률 자문이 아닙니다.
                ContractPilot의 분석 결과는 참고용이며, 최종 의사결정은 반드시
                변호사 등 법률 전문가와 상담 후 진행하시기 바랍니다.
                서비스 이용으로 인한 결과에 대해 ContractPilot은 법적 책임을 지지 않습니다.
              </p>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-6 pt-6 text-center text-gray-500 text-sm">
            <p>조코딩 x OpenAI x 프라이머 해커톤 | PDF, HWP, HWPX 지원</p>
          </div>
        </div>
      </footer>
    </main>
  )
}
