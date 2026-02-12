'use client'

import { useState, useRef, DragEvent } from 'react'
import { useRouter } from 'next/navigation'
import { startChunkingJob } from '@/lib/api'
import type { ChunkingDocumentType } from '@/types'

const DOCUMENT_TYPES: { value: ChunkingDocumentType; label: string; ext: string; desc: string }[] = [
  { value: 'heading', label: 'Heading', ext: '.pdf', desc: 'Document with heading structure' },
  { value: 'plain', label: 'Plain', ext: '.pdf', desc: 'General document' },
  { value: 'slide', label: 'Slide', ext: '.pdf', desc: 'Slide / presentation' },
  { value: 'lifelog', label: 'Lifelog', ext: '.txt', desc: '5W1H-style daily log' },
  { value: 'excel', label: 'Excel', ext: '.xlsx', desc: 'Spreadsheet' },
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
        {/* Header — Parsing 페이지와 동일 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Chunking</h1>
          <p className="text-gray-600">
            Upload a document to split it into chunks.
          </p>
        </div>

        {/* Document Type Selection — Parsing Mode 선택과 동일 카드 스타일 */}
        <div className="mb-8">
          <label className="block text-sm font-semibold text-gray-700 mb-4">
            Document Type
          </label>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
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
                  relative p-6 rounded-xl border-2 transition-all duration-200 text-left
                  ${
                    documentType === dt.value
                      ? 'border-blue-500 bg-blue-50 shadow-lg shadow-blue-500/20'
                      : 'border-gray-200 bg-white hover:border-gray-300'
                  }
                `}
              >
                <div className="flex items-start gap-3">
                  <div
                    className={`
                      w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0
                      ${documentType === dt.value ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-600'}
                    `}
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="font-semibold text-gray-900">{dt.label}</div>
                    <div className="text-xs text-gray-500 mt-0.5">{dt.ext}</div>
                    <div className="text-xs text-gray-600 mt-1">{dt.desc}</div>
                  </div>
                </div>
                {documentType === dt.value && (
                  <div className="absolute top-3 right-3 w-5 h-5 rounded-full bg-blue-500 flex items-center justify-center">
                    <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                )}
              </button>
            ))}
          </div>
        </div>

        {/* Upload Section — Parsing과 동일 카드 + FileUploader 스타일 드롭존 */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => !uploading && fileInputRef.current?.click()}
            className={`
              relative border-2 border-dashed rounded-2xl p-16 text-center transition-all duration-300 overflow-hidden
              ${isDragging
                ? 'border-blue-500 bg-gradient-to-br from-blue-50 to-purple-50 scale-[1.02] shadow-xl shadow-blue-500/20'
                : 'border-gray-300 bg-gradient-to-br from-gray-50 to-gray-100 hover:border-blue-400 hover:shadow-lg'
              }
              ${uploading ? 'opacity-50 pointer-events-none' : 'cursor-pointer'}
            `}
          >
            {isDragging && (
              <div className="absolute inset-0 bg-gradient-to-r from-blue-400/10 via-purple-400/10 to-pink-400/10 animate-pulse" />
            )}

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

            <div className="relative z-10 pointer-events-none">
              {uploading ? (
                <div className="space-y-6">
                  <div className="relative mx-auto w-20 h-20">
                    <div className="absolute inset-0 border-4 border-blue-200 rounded-full" />
                    <div className="absolute inset-0 border-4 border-blue-500 rounded-full border-t-transparent animate-spin" />
                  </div>
                  <div>
                    <p className="text-lg font-semibold text-gray-700">Uploading...</p>
                    <p className="text-sm text-gray-500 mt-1">업로드 및 Chunking 요청 중...</p>
                  </div>
                </div>
              ) : file ? (
                <div className="space-y-4">
                  <div className="relative inline-block">
                    <div className="w-20 h-20 mx-auto bg-gradient-to-br from-blue-500 to-purple-500 rounded-2xl flex items-center justify-center shadow-lg">
                      <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                    <div className="absolute -top-2 -right-2 w-6 h-6 bg-green-500 rounded-full border-4 border-white flex items-center justify-center">
                      <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                  </div>
                  <div>
                    <p className="text-xl font-semibold text-gray-900 mb-1">{file.name}</p>
                    <p className="text-sm text-gray-500">{formatFileSize(file.size)}</p>
                  </div>
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation()
                      setFile(null)
                      if (fileInputRef.current) fileInputRef.current.value = ''
                    }}
                    className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors pointer-events-auto"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    Choose different file
                  </button>
                </div>
              ) : (
                <div className="space-y-6">
                  <div className="relative inline-block">
                    <div className="absolute inset-0 bg-gradient-to-r from-blue-400 to-purple-400 rounded-full blur-2xl opacity-30 animate-pulse" />
                    <div className="relative w-24 h-24 bg-gradient-to-br from-blue-500 to-purple-600 rounded-3xl flex items-center justify-center shadow-2xl transform transition-transform hover:scale-110">
                      <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                      </svg>
                    </div>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-gray-900 mb-2">
                      {isDragging ? 'Drop your file here' : 'Drag and drop your file'}
                    </p>
                    <p className="text-gray-600 mb-4">or click to browse from your computer</p>
                    <div className="inline-flex items-center gap-2 px-4 py-2 bg-gray-100 rounded-lg">
                      <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                      </svg>
                      <span className="text-sm font-medium text-gray-700">Browse Files</span>
                    </div>
                  </div>
                  <div className="pt-4 border-t border-gray-200">
                    <p className="text-xs text-gray-500">
                      Accepted: {allowedExt} for type {documentType}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          {file && !uploading && (
            <div className="mt-8 flex justify-end">
              <button
                onClick={handleUpload}
                disabled={!canProceed}
                className={`
                  group relative px-8 py-3 rounded-xl font-semibold text-white
                  transition-all duration-200 overflow-hidden
                  ${canProceed
                    ? 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-lg shadow-blue-500/30 hover:shadow-xl hover:shadow-blue-500/40 hover:scale-105 cursor-pointer'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  }
                `}
              >
                {canProceed && (
                  <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000" />
                )}
                <span className="relative flex items-center gap-2">
                  Chunking 시작
                  <svg
                    className={`w-5 h-5 transition-transform ${canProceed ? 'group-hover:translate-x-1' : ''}`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </span>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
