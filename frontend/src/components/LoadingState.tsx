'use client'

import { useState, useEffect } from 'react'
import { FileSearch, Brain, Scale, CheckCircle } from 'lucide-react'

const steps = [
  { icon: FileSearch, text: 'PDF 텍스트 추출 중...', duration: 2000 },
  { icon: Brain, text: '조항별 분석 중...', duration: 3000 },
  { icon: Scale, text: '판례 검색 중...', duration: 2500 },
  { icon: CheckCircle, text: '결과 정리 중...', duration: 1500 },
]

export function LoadingState() {
  const [currentStep, setCurrentStep] = useState(0)

  useEffect(() => {
    if (currentStep < steps.length - 1) {
      const timer = setTimeout(() => {
        setCurrentStep(prev => prev + 1)
      }, steps[currentStep].duration)
      return () => clearTimeout(timer)
    }
  }, [currentStep])

  const CurrentIcon = steps[currentStep].icon

  return (
    <div className="flex flex-col items-center justify-center py-20">
      <div className="relative">
        {/* Spinning ring */}
        <div className="w-24 h-24 border-4 border-primary-200 rounded-full animate-spin border-t-primary-600" />

        {/* Icon in center */}
        <div className="absolute inset-0 flex items-center justify-center">
          <CurrentIcon className="w-10 h-10 text-primary-600" />
        </div>
      </div>

      <p className="mt-8 text-xl font-medium text-gray-700">
        {steps[currentStep].text}
      </p>

      {/* Progress dots */}
      <div className="flex gap-2 mt-6">
        {steps.map((_, index) => (
          <div
            key={index}
            className={`w-2 h-2 rounded-full transition-all duration-300 ${
              index <= currentStep ? 'bg-primary-600' : 'bg-gray-300'
            }`}
          />
        ))}
      </div>

      <p className="mt-4 text-sm text-gray-500">
        잠시만 기다려주세요...
      </p>
    </div>
  )
}
