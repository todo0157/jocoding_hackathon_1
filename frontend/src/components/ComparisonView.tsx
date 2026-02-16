'use client'

import { useState } from 'react'
import { X, ArrowLeftRight, AlertTriangle, CheckCircle, ChevronLeft, ChevronRight } from 'lucide-react'

interface ComparisonViewProps {
  data: any
  onClose: () => void
}

export function ComparisonView({ data, onClose }: ComparisonViewProps) {
  const [currentIndex, setCurrentIndex] = useState(0)

  // 수정된 조항만 필터링 (alternative가 있는 것)
  const modifiedClauses = data.clauses.filter(
    (clause: any) => clause.alternative && clause.analysis?.risk_score >= 7
  )

  // 수정된 조항이 없으면 전체 조항 표시
  const clausesToShow = modifiedClauses.length > 0 ? modifiedClauses : data.clauses

  const currentClause = clausesToShow[currentIndex]

  const goNext = () => {
    if (currentIndex < clausesToShow.length - 1) {
      setCurrentIndex(currentIndex + 1)
    }
  }

  const goPrev = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1)
    }
  }

  const getRiskBadge = (score: number) => {
    if (score >= 8) return { text: '위험', bgClass: 'bg-red-500', textClass: 'text-red-600' }
    if (score >= 6) return { text: '주의', bgClass: 'bg-orange-500', textClass: 'text-orange-600' }
    if (score >= 4) return { text: '보통', bgClass: 'bg-yellow-500', textClass: 'text-yellow-600' }
    return { text: '안전', bgClass: 'bg-green-500', textClass: 'text-green-600' }
  }

  const badge = getRiskBadge(currentClause?.analysis?.risk_score || 0)
  const hasAlternative = currentClause?.alternative

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-6xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-primary-600 to-primary-700 text-white p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <ArrowLeftRight className="w-6 h-6" />
            <div>
              <h2 className="text-xl font-bold">계약서 비교 뷰</h2>
              <p className="text-primary-100 text-sm">
                {modifiedClauses.length > 0
                  ? `수정된 조항 ${currentIndex + 1} / ${clausesToShow.length}`
                  : `전체 조항 ${currentIndex + 1} / ${clausesToShow.length}`
                }
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/20 rounded-lg transition"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Clause Title */}
        <div className="bg-gray-50 px-6 py-3 border-b flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className={`px-3 py-1 rounded-full text-sm font-medium text-white ${badge.bgClass}`}>
              {badge.text}
            </span>
            <h3 className="font-semibold text-lg">
              {currentClause?.title || `조항 ${currentClause?.number}`}
            </h3>
            <span className="text-gray-500 text-sm">
              위험도 {currentClause?.analysis?.risk_score}/10
            </span>
          </div>

          {/* Navigation */}
          <div className="flex items-center gap-2">
            <button
              onClick={goPrev}
              disabled={currentIndex === 0}
              className="p-2 rounded-lg hover:bg-gray-200 disabled:opacity-30 disabled:cursor-not-allowed transition"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <span className="text-sm text-gray-600 min-w-[60px] text-center">
              {currentIndex + 1} / {clausesToShow.length}
            </span>
            <button
              onClick={goNext}
              disabled={currentIndex === clausesToShow.length - 1}
              className="p-2 rounded-lg hover:bg-gray-200 disabled:opacity-30 disabled:cursor-not-allowed transition"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Comparison Content */}
        <div className="flex-1 overflow-auto p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 h-full">
            {/* Original */}
            <div className="flex flex-col">
              <div className="flex items-center gap-2 mb-3">
                <AlertTriangle className="w-5 h-5 text-red-500" />
                <h4 className="font-semibold text-red-700">원본 계약서</h4>
              </div>
              <div className={`
                flex-1 p-4 rounded-xl border-2
                ${hasAlternative ? 'border-red-200 bg-red-50' : 'border-gray-200 bg-gray-50'}
              `}>
                <p className={`
                  text-sm leading-relaxed whitespace-pre-wrap
                  ${hasAlternative ? 'text-red-900' : 'text-gray-700'}
                `}>
                  {currentClause?.content}
                </p>

                {/* Issues */}
                {currentClause?.analysis?.issues?.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-red-200">
                    <p className="text-xs font-semibold text-red-600 mb-2">발견된 문제점:</p>
                    <ul className="space-y-1">
                      {currentClause.analysis.issues.map((issue: string, i: number) => (
                        <li key={i} className="text-xs text-red-700 flex items-start gap-1">
                          <span className="text-red-500 mt-0.5">•</span>
                          {issue}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>

            {/* Modified */}
            <div className="flex flex-col">
              <div className="flex items-center gap-2 mb-3">
                <CheckCircle className="w-5 h-5 text-green-500" />
                <h4 className="font-semibold text-green-700">수정된 계약서</h4>
              </div>
              <div className={`
                flex-1 p-4 rounded-xl border-2
                ${hasAlternative ? 'border-green-200 bg-green-50' : 'border-gray-200 bg-gray-50'}
              `}>
                {hasAlternative ? (
                  <>
                    <p className="text-sm leading-relaxed whitespace-pre-wrap text-green-900">
                      {currentClause.alternative}
                    </p>
                    <div className="mt-4 pt-4 border-t border-green-200">
                      <p className="text-xs font-semibold text-green-600 mb-1">AI 수정 적용</p>
                      <p className="text-xs text-green-700">
                        위험 요소가 제거되어 균형 잡힌 조항으로 변경되었습니다.
                      </p>
                    </div>
                  </>
                ) : (
                  <div className="h-full flex items-center justify-center text-gray-400">
                    <div className="text-center">
                      <CheckCircle className="w-12 h-12 mx-auto mb-2 opacity-50" />
                      <p className="text-sm">수정이 필요 없는 조항입니다</p>
                      <p className="text-xs mt-1">원본 그대로 유지됩니다</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="bg-gray-50 px-6 py-4 border-t">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-600">
              {modifiedClauses.length > 0 ? (
                <span>
                  총 <strong className="text-red-600">{modifiedClauses.length}개</strong> 조항이 수정되었습니다
                </span>
              ) : (
                <span>수정이 필요한 고위험 조항이 없습니다</span>
              )}
            </div>

            {/* Quick Navigation Dots */}
            <div className="flex items-center gap-1">
              {clausesToShow.map((_: any, index: number) => (
                <button
                  key={index}
                  onClick={() => setCurrentIndex(index)}
                  className={`
                    w-2.5 h-2.5 rounded-full transition
                    ${index === currentIndex
                      ? 'bg-primary-600 scale-125'
                      : 'bg-gray-300 hover:bg-gray-400'
                    }
                  `}
                />
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
