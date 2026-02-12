'use client'

import { useState, useRef, DragEvent } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { pageindexUploadDocuments } from '@/lib/api'

const PDF_ACCEPT = '.pdf'

export default function ChatbotPage() {
  const router = useRouter()
  const [files, setFiles] = useState<File[]>([])
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const addFiles = (newFiles: FileList | File[]) => {
    const list = Array.from(newFiles)
    const pdfs = list.filter((f) => f.name.toLowerCase().endsWith('.pdf'))
    if (pdfs.length !== list.length) {
      setError('PDF files only. Non-PDF files were ignored.')
    } else if (list.length > 0) {
      setError(null)
    }
    setFiles((prev) => {
      const byName = new Map(prev.map((f) => [f.name, f]))
      pdfs.forEach((f) => byName.set(f.name, f))
      return Array.from(byName.values())
    })
  }

  const removeFile = (name: string) => {
    setFiles((prev) => prev.filter((f) => f.name !== name))
    setError(null)
  }

  const handleUpload = async () => {
    if (files.length === 0) {
      setError('Select at least one PDF file.')
      return
    }

    setUploading(true)
    setError(null)

    try {
      const res = await pageindexUploadDocuments(files)
      router.push(`/chatbot/result/${res.job_id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
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
    const dropped = e.dataTransfer.files
    if (dropped?.length) addFiles(dropped)
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
  }

  const canProceed = files.length > 0 && !uploading

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-8 py-12">
        <div className="mb-8 flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Chatbot</h1>
            <p className="text-gray-600">
              Upload one or more PDFs to index and chat with your documents.
            </p>
          </div>
          <Link
            href="/chatbot/list"
            className="px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors"
          >
            View indexed documents
          </Link>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => !uploading && fileInputRef.current?.click()}
            className={`
              relative border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300
              ${
                isDragging
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-300 bg-gray-50 hover:border-blue-400'
              }
              ${uploading ? 'opacity-50 pointer-events-none' : 'cursor-pointer'}
            `}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept={PDF_ACCEPT}
              multiple
              onChange={(e) => {
                const selected = e.target.files
                if (selected?.length) addFiles(selected)
              }}
              disabled={uploading}
              className="hidden"
            />

            {uploading ? (
              <div className="space-y-4">
                <div className="mx-auto w-16 h-16 border-4 border-blue-200 rounded-full border-t-blue-500 animate-spin" />
                <p className="text-lg font-semibold text-gray-700">Uploading & indexing...</p>
              </div>
            ) : files.length > 0 ? (
              <div className="space-y-4 text-left">
                <p className="text-lg font-semibold text-gray-900">
                  {files.length} PDF file(s) selected
                </p>
                <ul className="space-y-2 max-h-48 overflow-y-auto">
                  {files.map((f) => (
                    <li
                      key={f.name}
                      className="flex items-center justify-between py-2 px-3 bg-gray-100 rounded-lg"
                    >
                      <span className="text-sm font-medium text-gray-800 truncate flex-1">
                        {f.name}
                      </span>
                      <span className="text-xs text-gray-500 ml-2 flex-shrink-0">
                        {formatFileSize(f.size)}
                      </span>
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation()
                          removeFile(f.name)
                        }}
                        className="ml-2 p-1 text-red-600 hover:bg-red-50 rounded"
                        aria-label={`Remove ${f.name}`}
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </li>
                  ))}
                </ul>
                <p className="text-sm text-gray-500">Drop more PDFs or click to add</p>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="w-20 h-20 mx-auto bg-gradient-to-br from-blue-500 to-purple-500 rounded-2xl flex items-center justify-center">
                  <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                </div>
                <div>
                  <p className="text-xl font-bold text-gray-900">
                    {isDragging ? 'Drop PDFs here' : 'Drag and drop PDF files'}
                  </p>
                  <p className="text-gray-600 mt-1">or click to browse (multiple allowed)</p>
                </div>
                <p className="text-xs text-gray-500">PDF only</p>
              </div>
            )}
          </div>

          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          {files.length > 0 && !uploading && (
            <div className="mt-8 flex justify-end">
              <button
                onClick={handleUpload}
                disabled={!canProceed}
                className={`
                  px-8 py-3 rounded-xl font-semibold text-white
                  ${canProceed
                    ? 'bg-blue-600 hover:bg-blue-700'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  }
                `}
              >
                Upload & index
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
