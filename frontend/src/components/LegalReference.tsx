'use client'

import { useState } from 'react'
import {
  Scale,
  Book,
  AlertTriangle,
  CheckCircle,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  Gavel
} from 'lucide-react'

interface LawArticle {
  law_name: string
  article_number: string
  article_title: string
  content: string
  source?: string
}

interface MissingClause {
  clause: string
  law: string
  severity: string
}

interface ChecklistItem {
  clause: string
  law: string
  required: boolean
}

interface LegalReferenceProps {
  relevantLaws?: LawArticle[]
  missingClauses?: MissingClause[]
  checklist?: ChecklistItem[]
  contractType: string
}

export function LegalReference({
  relevantLaws = [],
  missingClauses = [],
  checklist = [],
  contractType
}: LegalReferenceProps) {
  const [showLaws, setShowLaws] = useState(false)
  const [showChecklist, setShowChecklist] = useState(false)

  const requiredItems = checklist.filter(item => item.required)
  const optionalItems = checklist.filter(item => !item.required)

  return (
    <div className="space-y-4">
      {/* Missing Clauses Warning */}
      {missingClauses.length > 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-amber-600 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <h4 className="font-semibold text-amber-800 mb-2">
                누락된 필수 조항 ({missingClauses.length}개)
              </h4>
              <ul className="space-y-2">
                {missingClauses.map((item, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-sm">
                    <span className="w-1.5 h-1.5 bg-amber-500 rounded-full mt-2" />
                    <div>
                      <span className="font-medium text-amber-900">{item.clause}</span>
                      <span className="text-amber-700 ml-2">({item.law})</span>
                    </div>
                  </li>
                ))}
              </ul>
              <p className="text-xs text-amber-600 mt-3">
                위 조항들은 {contractType}에서 일반적으로 포함되어야 하는 항목입니다.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Relevant Laws Section */}
      {relevantLaws.length > 0 && (
        <div className="bg-white border rounded-xl overflow-hidden">
          <button
            onClick={() => setShowLaws(!showLaws)}
            className="w-full p-4 flex items-center justify-between hover:bg-gray-50 transition"
          >
            <div className="flex items-center gap-3">
              <Scale className="w-5 h-5 text-indigo-600" />
              <span className="font-semibold">관련 법령</span>
              <span className="text-sm text-gray-500">({relevantLaws.length}개)</span>
            </div>
            {showLaws ? (
              <ChevronUp className="w-5 h-5 text-gray-400" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-400" />
            )}
          </button>

          {showLaws && (
            <div className="px-4 pb-4 space-y-3">
              {relevantLaws.map((law, idx) => (
                <div key={idx} className="p-3 bg-indigo-50 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <Book className="w-4 h-4 text-indigo-600" />
                    <span className="font-medium text-indigo-900">
                      {law.law_name} {law.article_number}
                    </span>
                    {law.article_title && (
                      <span className="text-sm text-indigo-700">
                        ({law.article_title})
                      </span>
                    )}
                  </div>
                  {law.content && (
                    <p className="text-sm text-indigo-800 leading-relaxed">
                      {law.content}
                    </p>
                  )}
                  {law.source === 'api' && (
                    <div className="flex items-center gap-1 mt-2 text-xs text-indigo-600">
                      <ExternalLink className="w-3 h-3" />
                      <span>국가법령정보센터</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Checklist Section */}
      {checklist.length > 0 && (
        <div className="bg-white border rounded-xl overflow-hidden">
          <button
            onClick={() => setShowChecklist(!showChecklist)}
            className="w-full p-4 flex items-center justify-between hover:bg-gray-50 transition"
          >
            <div className="flex items-center gap-3">
              <Gavel className="w-5 h-5 text-purple-600" />
              <span className="font-semibold">{contractType} 체크리스트</span>
              <span className="text-sm text-gray-500">
                (필수 {requiredItems.length}개 / 선택 {optionalItems.length}개)
              </span>
            </div>
            {showChecklist ? (
              <ChevronUp className="w-5 h-5 text-gray-400" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-400" />
            )}
          </button>

          {showChecklist && (
            <div className="px-4 pb-4">
              {/* Required Items */}
              <div className="mb-4">
                <h5 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                  <span className="w-2 h-2 bg-red-500 rounded-full" />
                  필수 조항
                </h5>
                <div className="grid grid-cols-2 gap-2">
                  {requiredItems.map((item, idx) => (
                    <div
                      key={idx}
                      className="flex items-center gap-2 p-2 bg-red-50 rounded-lg text-sm"
                    >
                      <CheckCircle className="w-4 h-4 text-red-400" />
                      <span className="text-red-800">{item.clause}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Optional Items */}
              {optionalItems.length > 0 && (
                <div>
                  <h5 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                    <span className="w-2 h-2 bg-gray-400 rounded-full" />
                    선택 조항
                  </h5>
                  <div className="grid grid-cols-2 gap-2">
                    {optionalItems.map((item, idx) => (
                      <div
                        key={idx}
                        className="flex items-center gap-2 p-2 bg-gray-50 rounded-lg text-sm"
                      >
                        <CheckCircle className="w-4 h-4 text-gray-400" />
                        <span className="text-gray-700">{item.clause}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
