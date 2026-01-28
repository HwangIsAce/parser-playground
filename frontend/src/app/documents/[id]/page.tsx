'use client'

import { useParams, useRouter, useSearchParams } from 'next/navigation'
import { useEffect, useState } from 'react'
import ResultViewer from '@/components/ResultViewer'
import { getDocument } from '@/lib/api'
import { Document, ParseResult } from '@/types'

export default function DocumentViewPage() {
  const params = useParams()
  const router = useRouter()
  const searchParams = useSearchParams()
  const documentId = params.id as string
  const mode = (searchParams.get('mode') as 'basic' | 'enhance') || 'basic'

  const [document, setDocument] = useState<Document | null>(null)
  const [parseResult, setParseResult] = useState<ParseResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadDocument = async () => {
      try {
        setLoading(true)
        const doc = await getDocument(documentId)
        setDocument(doc)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load document')
      } finally {
        setLoading(false)
      }
    }

    if (documentId) {
      loadDocument()
    }
  }, [documentId])

  const handleParseComplete = (result: ParseResult) => {
    setParseResult(result)
  }

  const handleNewFile = () => {
    router.push('/')
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-8 py-12">
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="relative mx-auto w-16 h-16 mb-4">
                <div className="absolute inset-0 border-4 border-blue-200 rounded-full"></div>
                <div className="absolute inset-0 border-4 border-blue-500 rounded-full border-t-transparent animate-spin"></div>
              </div>
              <p className="text-gray-600">Loading document...</p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (error || !document) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-8 py-12">
          <div className="bg-white rounded-xl shadow-sm border border-red-200 p-8">
            <h1 className="text-2xl font-bold text-gray-900 mb-4">Error</h1>
            <div className="text-red-600 mb-6">
              {error || 'Document not found'}
            </div>
            <button
              onClick={handleNewFile}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              New File
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-8 py-12">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Document Parsing
            </h1>
            <p className="text-gray-600">{document.filename}</p>
          </div>
          <button
            onClick={handleNewFile}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            New File
          </button>
        </div>

        {/* Result Viewer */}
        <ResultViewer
          document={document}
          mode={mode}
          parseResult={parseResult}
          onParseComplete={handleParseComplete}
        />
      </div>
    </div>
  )
}
