'use client'

import { useState } from 'react'
import { FileText, FileCheck, Loader2 } from 'lucide-react'
import { downloadAnalysisReport } from '@/lib/api'

interface ReportDownloadButtonProps {
  analysisResult: any
}

export function ReportDownloadButton({ analysisResult }: ReportDownloadButtonProps) {
  const [isDownloading, setIsDownloading] = useState(false)
  const [downloadComplete, setDownloadComplete] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleDownload = async () => {
    setIsDownloading(true)
    setError(null)

    try {
      await downloadAnalysisReport(analysisResult)
      setDownloadComplete(true)
      setTimeout(() => setDownloadComplete(false), 3000)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setIsDownloading(false)
    }
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
              : 'bg-purple-600 text-white hover:bg-purple-700'
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
            <FileText className="w-5 h-5" />
            분석 리포트 다운로드
          </>
        )}
      </button>

      {error && (
        <p className="text-red-500 text-sm text-center">{error}</p>
      )}
    </div>
  )
}
