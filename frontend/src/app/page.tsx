'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import FileUploader from '@/components/FileUploader'
import { Document } from '@/types'

export default function Home() {
  const router = useRouter()
  const [mode, setMode] = useState<'basic' | 'enhance'>('basic')

  const handleDocumentUploaded = (doc: Document) => {
    // Navigate to document view page with mode
    router.push(`/documents/${doc.id}?mode=${mode}`)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-8 py-12">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Document Parsing
          </h1>
          <p className="text-gray-600">
            Upload and parse documents with AI-powered OCR
          </p>
        </div>

        {/* Mode Selection - Enhanced */}
        <div className="mb-8">
          <label className="block text-sm font-semibold text-gray-700 mb-4">
            Parse Mode
          </label>
          <div className="grid grid-cols-2 gap-4">
            <button
              type="button"
              onClick={() => setMode('basic')}
              className={`
                relative p-6 rounded-xl border-2 transition-all duration-200
                ${
                  mode === 'basic'
                    ? 'border-blue-500 bg-blue-50 shadow-lg shadow-blue-500/20'
                    : 'border-gray-200 bg-white hover:border-gray-300'
                }
              `}
            >
              <div className="flex items-start gap-4">
                <div
                  className={`
                    w-12 h-12 rounded-lg flex items-center justify-center
                    ${
                      mode === 'basic'
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-100 text-gray-600'
                    }
                  `}
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <div className="flex-1 text-left">
                  <div className="font-semibold text-gray-900 mb-1">Basic</div>
                  <div className="text-sm text-gray-600">
                    Fast parsing mode
                  </div>
                </div>
                {mode === 'basic' && (
                  <div className="absolute top-3 right-3">
                    <div className="w-5 h-5 rounded-full bg-blue-500 flex items-center justify-center">
                      <svg
                        className="w-3 h-3 text-white"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M5 13l4 4L19 7"
                        />
                      </svg>
                    </div>
                  </div>
                )}
              </div>
            </button>

            <button
              type="button"
              onClick={() => setMode('enhance')}
              className={`
                relative p-6 rounded-xl border-2 transition-all duration-200
                ${
                  mode === 'enhance'
                    ? 'border-purple-500 bg-purple-50 shadow-lg shadow-purple-500/20'
                    : 'border-gray-200 bg-white hover:border-gray-300'
                }
              `}
            >
              <div className="flex items-start gap-4">
                <div
                  className={`
                    w-12 h-12 rounded-lg flex items-center justify-center
                    ${
                      mode === 'enhance'
                        ? 'bg-purple-500 text-white'
                        : 'bg-gray-100 text-gray-600'
                    }
                  `}
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
                <div className="flex-1 text-left">
                  <div className="font-semibold text-gray-900 mb-1">Enhance</div>
                  <div className="text-sm text-gray-600">
                    Advanced OCR mode
                  </div>
                </div>
                {mode === 'enhance' && (
                  <div className="absolute top-3 right-3">
                    <div className="w-5 h-5 rounded-full bg-purple-500 flex items-center justify-center">
                      <svg
                        className="w-3 h-3 text-white"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M5 13l4 4L19 7"
                        />
                      </svg>
                    </div>
                  </div>
                )}
              </div>
            </button>
          </div>
        </div>

        {/* Upload Section */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
          <FileUploader 
            mode={mode}
            onUploadComplete={handleDocumentUploaded} 
          />
        </div>
      </div>
    </div>
  )
}
