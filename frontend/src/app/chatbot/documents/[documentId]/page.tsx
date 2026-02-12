'use client'

import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'

/**
 * Placeholder until Phase 5 (chat + TOC layout).
 * Redirect target after indexing completes.
 */
export default function ChatbotDocumentPlaceholderPage() {
  const params = useParams()
  const documentId = params.documentId as string
  const router = useRouter()

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 max-w-md text-center">
        <h1 className="text-xl font-bold text-gray-900 mb-2">Document indexed</h1>
        <p className="text-gray-600 mb-4 text-sm font-mono break-all">
          {documentId}
        </p>
        <p className="text-gray-500 text-sm mb-6">
          Chat and TOC view will be available in the next phase.
        </p>
        <div className="flex gap-3 justify-center">
          <Link
            href="/chatbot"
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Upload more
          </Link>
          <button
            onClick={() => router.back()}
            className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Back
          </button>
        </div>
      </div>
    </div>
  )
}
