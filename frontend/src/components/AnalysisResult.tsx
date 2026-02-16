'use client'

import { useState } from 'react'
import Link from 'next/link'
import {
  AlertTriangle,
  CheckCircle,
  ChevronDown,
  ChevronUp,
  Copy,
  ExternalLink,
  RefreshCw,
  FileText,
  MessageCircle,
  Download,
  ArrowLeftRight
} from 'lucide-react'
import { DownloadButton } from './DownloadButton'
import { ReportDownloadButton } from './ReportDownloadButton'
import { ComparisonView } from './ComparisonView'

interface AnalysisResultProps {
  data: any
  onReset: () => void
}

export function AnalysisResult({ data, onReset }: AnalysisResultProps) {
  const [expandedClauses, setExpandedClauses] = useState<number[]>([])
  const [copiedId, setCopiedId] = useState<number | null>(null)
  const [showComparison, setShowComparison] = useState(false)

  const toggleClause = (index: number) => {
    setExpandedClauses(prev =>
      prev.includes(index)
        ? prev.filter(i => i !== index)
        : [...prev, index]
    )
  }

  const copyToClipboard = (text: string, id: number) => {
    navigator.clipboard.writeText(text)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
  }

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'low': return 'risk-low'
      case 'medium': return 'risk-medium'
      case 'high': return 'risk-high'
      case 'critical': return 'risk-critical'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getRiskBadge = (score: number) => {
    if (score >= 8) return { text: '위험', class: 'bg-red-500' }
    if (score >= 6) return { text: '주의', class: 'bg-orange-500' }
    if (score >= 4) return { text: '보통', class: 'bg-yellow-500' }
    return { text: '안전', class: 'bg-green-500' }
  }

  return (
    <div className="space-y-6 animate-slide-up">
      {/* Summary Card */}
      <div className={`p-6 rounded-2xl border-2 ${getRiskColor(data.overall_risk_level)}`}>
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2 mb-2">
              {data.overall_risk_level === 'low' ? (
                <CheckCircle className="w-6 h-6" />
              ) : (
                <AlertTriangle className="w-6 h-6" />
              )}
              <span className="text-lg font-semibold">분석 완료</span>
            </div>
            <h2 className="text-2xl font-bold mb-1">{data.contract_type}</h2>
            <p className="text-sm opacity-80">
              총 {data.total_clauses}개 조항 중 {data.high_risk_clauses}개 고위험 발견
            </p>
          </div>
          <div className="text-right">
            <div className="text-4xl font-bold">{data.average_risk_score}</div>
            <div className="text-sm">평균 위험도</div>
          </div>
        </div>

        <p className="mt-4 p-4 bg-white/50 rounded-lg text-sm">
          {data.summary}
        </p>
      </div>

      {/* Download Section */}
      {data.high_risk_clauses > 0 && (
        <div className="bg-white rounded-2xl shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-lg flex items-center gap-2">
                <Download className="w-5 h-5 text-primary-600" />
                안전한 계약서 다운로드
              </h3>
              <p className="text-sm text-gray-600 mt-1">
                위험 조항 {data.high_risk_clauses}개가 수정된 버전을 다운로드하세요
              </p>
            </div>
            <DownloadButton analysisResult={data} />
          </div>
        </div>
      )}

      {/* Report Download Section */}
      <div className="bg-white rounded-2xl shadow-sm p-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-lg flex items-center gap-2">
              <FileText className="w-5 h-5 text-purple-600" />
              분석 리포트 다운로드
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              전체 분석 결과를 PDF 리포트로 받아보세요
            </p>
          </div>
          <ReportDownloadButton analysisResult={data} />
        </div>
      </div>

      {/* Comparison View Section */}
      {data.high_risk_clauses > 0 && (
        <div className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-2xl p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl font-bold mb-1 flex items-center gap-2">
                <ArrowLeftRight className="w-6 h-6" />
                원본 vs 수정본 비교
              </h3>
              <p className="text-indigo-100">
                {data.high_risk_clauses}개 위험 조항의 변경 사항을 한눈에 비교하세요
              </p>
            </div>
            <button
              onClick={() => setShowComparison(true)}
              className="flex items-center gap-2 px-6 py-3 bg-white text-indigo-600 font-semibold rounded-xl hover:bg-indigo-50 transition"
            >
              <ArrowLeftRight className="w-5 h-5" />
              비교하기
            </button>
          </div>
        </div>
      )}

      {/* Clauses List */}
      <div className="bg-white rounded-2xl shadow-sm overflow-hidden">
        <div className="p-4 border-b bg-gray-50 flex items-center justify-between">
          <h3 className="font-semibold text-lg flex items-center gap-2">
            <FileText className="w-5 h-5" />
            조항별 분석 결과
          </h3>
          <button
            onClick={onReset}
            className="flex items-center gap-2 px-4 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition"
          >
            <RefreshCw className="w-4 h-4" />
            새로 분석
          </button>
        </div>

        <div className="divide-y">
          {data.clauses.map((clause: any, index: number) => {
            const isExpanded = expandedClauses.includes(index)
            const badge = getRiskBadge(clause.analysis.risk_score)
            const isHighRisk = clause.analysis.risk_score >= 6

            return (
              <div
                key={index}
                className={`${isHighRisk ? 'bg-red-50/50' : ''}`}
              >
                {/* Clause Header */}
                <button
                  onClick={() => toggleClause(index)}
                  className="w-full p-4 flex items-center justify-between hover:bg-gray-50 transition"
                >
                  <div className="flex items-center gap-3">
                    <span className={`px-2 py-1 rounded text-xs font-medium text-white ${badge.class}`}>
                      {badge.text}
                    </span>
                    <span className="font-medium">
                      {clause.title || `조항 ${clause.number}`}
                    </span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-sm text-gray-500">
                      위험도 {clause.analysis.risk_score}/10
                    </span>
                    {isExpanded ? (
                      <ChevronUp className="w-5 h-5 text-gray-400" />
                    ) : (
                      <ChevronDown className="w-5 h-5 text-gray-400" />
                    )}
                  </div>
                </button>

                {/* Expanded Content */}
                {isExpanded && (
                  <div className="px-4 pb-4 space-y-4">
                    {/* Original Content */}
                    <div className="p-3 bg-gray-100 rounded-lg text-sm">
                      <div className="text-xs text-gray-500 mb-1">원문</div>
                      {clause.content}
                    </div>

                    {/* Analysis */}
                    <div className="p-3 bg-blue-50 rounded-lg">
                      <div className="text-xs text-blue-600 mb-1">분석 결과</div>
                      <p className="text-sm font-medium">{clause.analysis.summary}</p>

                      {clause.analysis.issues?.length > 0 && (
                        <ul className="mt-2 space-y-1">
                          {clause.analysis.issues.map((issue: string, i: number) => (
                            <li key={i} className="text-sm text-gray-700 flex items-start gap-2">
                              <span className="text-red-500">•</span>
                              {issue}
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>

                    {/* Similar Cases */}
                    {clause.similar_cases?.length > 0 && (
                      <div className="p-3 bg-purple-50 rounded-lg">
                        <div className="text-xs text-purple-600 mb-2">관련 판례</div>
                        {clause.similar_cases.map((caseItem: any, i: number) => (
                          <div key={i} className="text-sm mb-2 last:mb-0">
                            <div className="font-medium flex items-center gap-2">
                              {caseItem.case_number}
                              <ExternalLink className="w-3 h-3 text-gray-400" />
                            </div>
                            <p className="text-gray-600">{caseItem.summary}</p>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Alternative */}
                    {clause.alternative && (
                      <div className="p-3 bg-green-50 rounded-lg">
                        <div className="flex items-center justify-between mb-1">
                          <div className="text-xs text-green-600">수정 제안</div>
                          <button
                            onClick={() => copyToClipboard(clause.alternative, index)}
                            className="flex items-center gap-1 text-xs text-green-600 hover:text-green-800"
                          >
                            <Copy className="w-3 h-3" />
                            {copiedId === index ? '복사됨!' : '복사'}
                          </button>
                        </div>
                        <p className="text-sm">{clause.alternative}</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>

      {/* Chat CTA */}
      <div className="bg-gradient-to-r from-primary-500 to-primary-600 rounded-2xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xl font-bold mb-1">추가 질문이 있으신가요?</h3>
            <p className="text-primary-100">
              AI 법률 상담사에게 계약서에 대해 더 자세히 물어보세요
            </p>
          </div>
          <Link
            href="/chat"
            className="flex items-center gap-2 px-6 py-3 bg-white text-primary-600 font-semibold rounded-xl hover:bg-primary-50 transition"
          >
            <MessageCircle className="w-5 h-5" />
            상담하기
          </Link>
        </div>
      </div>

      {/* Comparison View Modal */}
      {showComparison && (
        <ComparisonView
          data={data}
          onClose={() => setShowComparison(false)}
        />
      )}
    </div>
  )
}
