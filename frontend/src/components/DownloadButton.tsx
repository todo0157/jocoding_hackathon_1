'use client'

import { useState } from 'react'
import { Download, FileCheck, Loader2 } from 'lucide-react'
import { downloadSafeContract } from '@/lib/api'

interface DownloadButtonProps {
  analysisResult: any
}

export function DownloadButton({ analysisResult }: DownloadButtonProps) {
  const [isDownloading, setIsDownloading] = useState(false)
  const [downloadComplete, setDownloadComplete] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // 수정된 조항이 있는지 확인
  const hasModifications = analysisResult.clauses.some(
    (clause: any) => clause.alternative && clause.analysis?.risk_score >= 7
  )

  const handleDownload = async () => {
    setIsDownloading(true)
    setError(null)

    try {
      await downloadSafeContract(analysisResult)
      setDownloadComplete(true)
      setTimeout(() => setDownloadComplete(false), 3000)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setIsDownloading(false)
    }
  }

  if (!hasModifications) {
    return null
  }

  return (
    <div className="space-y-2">
      <button
        onClick={handleDownload}
        disabled={isDownloading}
        className={`
          flex items-center justify-center gap-2 px-6 py-3
          rounded-xl font-semibold transition
          ${isDownloading
            ? 'bg-gray-300 cursor-not-allowed'
            : downloadComplete
              ? 'bg-green-500 text-white'
              : 'bg-primary-600 text-white hover:bg-primary-700'
          }
        `}
      >
        {isDownloading ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            생성 중...
          </>
        ) : downloadComplete ? (
          <>
            <FileCheck className="w-5 h-5" />
            다운로드 완료!
          </>
        ) : (
          <>
            <Download className="w-5 h-5" />
            수정된 계약서 다운로드
          </>
        )}
      </button>

      {error && (
        <p className="text-red-500 text-sm text-center">{error}</p>
      )}
    </div>
  )
}
