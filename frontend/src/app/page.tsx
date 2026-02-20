'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { FileUpload } from '@/components/FileUpload'
import { AnalysisResult } from '@/components/AnalysisResult'
import { LoadingState } from '@/components/LoadingState'
import { analyzeContract } from '@/lib/api'
import { FileText, Shield, Scale, MessageCircle, Briefcase } from 'lucide-react'

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
              <div className="grid md:grid-cols-3 gap-6 mb-12">
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
              </div>
            </section>

            {/* Upload Section */}
            <FileUpload onUpload={handleFileUpload} />

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
      <footer className="bg-white border-t mt-12">
        <div className="max-w-7xl mx-auto px-4 py-6 text-center text-gray-500 text-sm">
          <p>ContractPilot - 조코딩 x OpenAI x 프라이머 해커톤</p>
          <p className="mt-1">본 서비스는 법률 자문을 대체하지 않습니다.</p>
        </div>
      </footer>
    </main>
  )
}
