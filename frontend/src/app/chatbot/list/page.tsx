'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { pageindexListDocuments } from '@/lib/api'

export default function ChatbotListPage() {
  const [documents, setDocuments] = useState<
    Array<{ id: string; name: string; doc_count: number; created_at: string }>
  >([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    pageindexListDocuments()
      .then((res) => {
        if (!cancelled) setDocuments(res.documents ?? [])
      })
      .catch((e) => {
        if (!cancelled) setError(e instanceof Error ? e.message : 'Failed to load')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-600">Loading documents...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white rounded-xl shadow-sm border border-red-200 p-8 max-w-md text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <Link href="/chatbot" className="text-blue-600 hover:underline">
            Back to Chatbot
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-3xl mx-auto px-8 py-12">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Indexed documents</h1>
          <Link
            href="/chatbot"
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium"
          >
            Upload PDFs
          </Link>
        </div>

        {documents.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center text-gray-500">
            <p>No indexed documents yet.</p>
            <Link href="/chatbot" className="mt-4 inline-block text-blue-600 hover:underline">
              Upload PDFs to get started
            </Link>
          </div>
        ) : (
          <ul className="space-y-2">
            {documents.map((doc) => (
              <li key={doc.id}>
                <Link
                  href={`/chatbot/documents/${doc.id}`}
                  className="block bg-white rounded-xl shadow-sm border border-gray-200 p-4 hover:border-blue-400 hover:shadow transition-all"
                >
                  <div className="font-medium text-gray-900">{doc.name}</div>
                  <div className="text-sm text-gray-500 mt-1">
                    {doc.doc_count} file(s) · {new Date(doc.created_at).toLocaleString()}
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
