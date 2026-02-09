'use client'

import { useState, useRef, DragEvent } from 'react'
import { useRouter } from 'next/navigation'
import { startChunkingJob } from '@/lib/api'
import type { ChunkingDocumentType } from '@/types'

const DOCUMENT_TYPES: { value: ChunkingDocumentType; label: string; ext: string; desc: string }[] = [
  { value: 'heading', label: 'Heading', ext: '.pdf', desc: '제목 구조가 있는 문서' },
  { value: 'plain', label: 'Plain', ext: '.pdf', desc: '일반 문서' },
  { value: 'slide', label: 'Slide', ext: '.pdf', desc: '슬라이드 문서' },
  { value: 'lifelog', label: 'Lifelog', ext: '.txt', desc: '5W1H 형식 일지' },
  { value: 'excel', label: 'Excel', ext: '.xlsx', desc: '스프레드시트' },
]

const TYPE_TO_EXT: Record<ChunkingDocumentType, string> = {
  heading: '.pdf',
  plain: '.pdf',
  slide: '.pdf',
  lifelog: '.txt',
  excel: '.xlsx',
}

export default function ChunkingPage() {
  const router = useRouter()
  const [documentType, setDocumentType] = useState<ChunkingDocumentType>('plain')
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const allowedExt = TYPE_TO_EXT[documentType]

  const validateFile = (f: File): boolean => {
    const ext = '.' + (f.name.split('.').pop()?.toLowerCase() || '')
    if (ext !== allowedExt) {
      setError(
        `${documentType}는 ${allowedExt} 파일만 지원합니다. (선택: ${ext})`
      )
      return false
    }
    return true
  }

  const handleFileSelect = (f: File) => {
    if (validateFile(f)) {
      setFile(f)
      setError(null)
    }
  }

  const handleUpload = async () => {
    if (!file) {
      setError('파일을 선택해주세요.')
      return
    }

    setUploading(true)
    setError(null)

    try {
      const res = await startChunkingJob(file, documentType)
      router.push(`/chunking/result/${res.job_id}?document_id=${res.document_id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Chunking 요청 실패')
    } finally {
      setUploading(false)
    }
  }

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragging(false)
    const droppedFile = e.dataTransfer.files?.[0]
    if (droppedFile) handleFileSelect(droppedFile)
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
  }

  const canProceed = file !== null && !uploading

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-8 py-12">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Chunking</h1>
          <p className="text-gray-600">
            문서를 업로드하여 청크 단위로 분할합니다. (RAG/임베딩용)
          </p>
        </div>

        {/* Document Type Selection */}
        <div className="mb-8">
          <label className="block text-sm font-semibold text-gray-700 mb-4">
            문서 유형
          </label>
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
            {DOCUMENT_TYPES.map((dt) => (
              <button
                key={dt.value}
                type="button"
                onClick={() => {
                  setDocumentType(dt.value)
                  setFile(null)
                  setError(null)
                  if (fileInputRef.current) fileInputRef.current.value = ''
                }}
                className={`
                  relative p-4 rounded-xl border-2 transition-all duration-200 text-left
                  ${
                    documentType === dt.value
                      ? 'border-blue-500 bg-blue-50 shadow-md'
                      : 'border-gray-200 bg-white hover:border-gray-300'
                  }
                `}
              >
                <div className="font-semibold text-gray-900">{dt.label}</div>
                <div className="text-xs text-gray-500 mt-0.5">{dt.ext}</div>
                <div className="text-xs text-gray-600 mt-1">{dt.desc}</div>
                {documentType === dt.value && (
                  <div className="absolute top-2 right-2 w-5 h-5 rounded-full bg-blue-500 flex items-center justify-center">
                    <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                )}
              </button>
            ))}
          </div>
          <p className="text-sm text-gray-500 mt-2">
            선택한 유형에 맞는 확장자({allowedExt})로 파일을 업로드해주세요.
          </p>
        </div>

        {/* File Drop Zone */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => !uploading && fileInputRef.current?.click()}
            className={`
              border-2 border-dashed rounded-2xl p-12 text-center transition-all cursor-pointer
              ${isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
              ${uploading ? 'opacity-50 pointer-events-none' : ''}
            `}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept={allowedExt}
              onChange={(e) => {
                const f = e.target.files?.[0]
                if (f) handleFileSelect(f)
              }}
              disabled={uploading}
              className="hidden"
            />
            {uploading ? (
              <div className="space-y-4">
                <div className="mx-auto w-16 h-16 border-4 border-blue-200 rounded-full border-t-blue-500 animate-spin" />
                <p className="text-lg font-medium text-gray-700">업로드 및 Chunking 요청 중...</p>
              </div>
            ) : file ? (
              <div className="space-y-4">
                <div className="w-16 h-16 mx-auto bg-green-100 rounded-xl flex items-center justify-center">
                  <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <p className="font-semibold text-gray-900">{file.name}</p>
                <p className="text-sm text-gray-500">{formatFileSize(file.size)}</p>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation()
                    setFile(null)
                    if (fileInputRef.current) fileInputRef.current.value = ''
                  }}
                  className="text-sm text-blue-600 hover:text-blue-700"
                >
                  다른 파일 선택
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="w-16 h-16 mx-auto bg-gray-100 rounded-xl flex items-center justify-center">
                  <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                </div>
                <p className="text-lg font-medium text-gray-700">
                  {isDragging ? '여기에 놓으세요' : '파일을 드래그하거나 클릭하여 선택'}
                </p>
                <p className="text-sm text-gray-500">{allowedExt} (문서 유형: {documentType})</p>
              </div>
            )}
          </div>

          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          {file && !uploading && (
            <div className="mt-6 flex justify-end">
              <button
                onClick={handleUpload}
                disabled={!canProceed}
                className="px-6 py-3 bg-blue-600 text-white font-medium rounded-xl hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                Chunking 시작
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
