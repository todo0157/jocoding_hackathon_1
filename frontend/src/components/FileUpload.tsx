'use client'

import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText } from 'lucide-react'

interface FileUploadProps {
  onUpload: (file: File) => void
}

export function FileUpload({ onUpload }: FileUploadProps) {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      onUpload(acceptedFiles[0])
    }
  }, [onUpload])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024, // 10MB
  })

  return (
    <div
      {...getRootProps()}
      className={`
        border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer
        transition-all duration-300 ease-in-out
        ${isDragActive
          ? 'border-primary-500 bg-primary-50 scale-105'
          : 'border-gray-300 bg-white hover:border-primary-400 hover:bg-gray-50'
        }
      `}
    >
      <input {...getInputProps()} />

      <div className="flex flex-col items-center gap-4">
        {isDragActive ? (
          <>
            <FileText className="w-16 h-16 text-primary-500 animate-bounce" />
            <p className="text-xl font-medium text-primary-600">
              여기에 놓으세요!
            </p>
          </>
        ) : (
          <>
            <Upload className="w-16 h-16 text-gray-400" />
            <div>
              <p className="text-xl font-medium text-gray-700">
                계약서 PDF를 드래그하거나 클릭하여 업로드
              </p>
              <p className="text-gray-500 mt-2">
                PDF 파일만 지원 (최대 10MB)
              </p>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
