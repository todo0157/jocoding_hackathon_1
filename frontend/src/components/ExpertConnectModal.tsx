'use client'

import { useState } from 'react'
import { X, UserCheck, Loader2, CheckCircle } from 'lucide-react'
import { requestExpertConnect } from '@/lib/api'

interface ExpertConnectModalProps {
  onClose: () => void
  consultationSummary?: string
}

export function ExpertConnectModal({ onClose, consultationSummary }: ExpertConnectModalProps) {
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    preferredTime: '',
    agreePrivacy: false
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSubmitted, setIsSubmitted] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsSubmitting(true)

    try {
      await requestExpertConnect({
        name: formData.name,
        phone: formData.phone,
        preferred_time: formData.preferredTime,
        consultation_summary: consultationSummary,
        agree_privacy: formData.agreePrivacy
      })
      setIsSubmitted(true)
    } catch (err: any) {
      setError(err.message || '상담 신청 중 오류가 발생했습니다.')
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isSubmitted) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
        <div className="bg-white rounded-2xl p-8 max-w-md w-full text-center">
          <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-gray-900 mb-2">상담 신청 완료!</h2>
          <p className="text-gray-600 mb-6">
            24시간 내에 전문 노무사가
            <br />
            연락드릴 예정이에요.
          </p>
          <button
            onClick={onClose}
            className="w-full py-3 bg-blue-600 text-white rounded-xl font-semibold hover:bg-blue-700 transition"
          >
            확인
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-2xl p-6 max-w-md w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <UserCheck className="w-6 h-6 text-blue-600" />
            <h2 className="text-lg font-bold text-gray-900">전문 노무사 상담 신청</h2>
          </div>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-100 rounded-full transition"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        <p className="text-sm text-gray-600 mb-6">
          전문 노무사가 24시간 내에 연락드려요.
          <br />
          초기 상담은 <span className="font-semibold text-blue-600">무료</span>입니다.
        </p>

        {error && (
          <div className="mb-4 p-3 bg-red-50 text-red-600 rounded-lg text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              이름
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="홍길동"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              연락처
            </label>
            <input
              type="tel"
              value={formData.phone}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
              placeholder="010-1234-5678"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              희망 연락 시간
            </label>
            <select
              value={formData.preferredTime}
              onChange={(e) => setFormData({ ...formData, preferredTime: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="">선택해주세요</option>
              <option value="morning">오전 (9시-12시)</option>
              <option value="afternoon">오후 (12시-18시)</option>
              <option value="evening">저녁 (18시-21시)</option>
              <option value="anytime">언제든지</option>
            </select>
          </div>

          <div className="flex items-start gap-2">
            <input
              type="checkbox"
              id="agreePrivacy"
              checked={formData.agreePrivacy}
              onChange={(e) => setFormData({ ...formData, agreePrivacy: e.target.checked })}
              className="mt-1 w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              required
            />
            <label htmlFor="agreePrivacy" className="text-sm text-gray-600">
              개인정보 수집 및 이용에 동의합니다
            </label>
          </div>

          <button
            type="submit"
            disabled={!formData.agreePrivacy || isSubmitting}
            className="w-full py-3 bg-blue-600 text-white rounded-xl font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition flex items-center justify-center gap-2"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                신청 중...
              </>
            ) : (
              '무료 상담 신청하기'
            )}
          </button>
        </form>

        <div className="mt-6 pt-4 border-t">
          <h3 className="text-sm font-medium text-gray-800 mb-2">
            노무사 상담 시 도움받을 수 있는 것
          </h3>
          <ul className="text-sm text-gray-600 space-y-1">
            <li>✓ 정확한 법적 권리 확인</li>
            <li>✓ 증거 수집 방법 안내</li>
            <li>✓ 진정서/소송 대리</li>
            <li>✓ 회사와의 협상 지원</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
