'use client'

import { useParams, useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { pollPageIndexJobUntilComplete } from '@/lib/api'
import type { PageIndexJobResponse } from '@/types'

export default function ChatbotResultPage() {
  const params = useParams()
  const router = useRouter()
  const jobId = params.jobId as string
  const [status, setStatus] = useState<PageIndexJobResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!jobId) {
      setError('Missing job ID')
      setLoading(false)
      return
    }

    let cancelled = false

    const run = async () => {
      try {
        setLoading(true)
        setError(null)
        const final = await pollPageIndexJobUntilComplete(jobId, (s) => {
          if (!cancelled) setStatus(s)
        })

        if (cancelled) return

        if (final.status === 'failed') {
          setError(final.error || 'Indexing failed')
          setLoading(false)
          return
        }

        if (final.status === 'completed' && final.document_id) {
          router.replace(`/chatbot/documents/${final.document_id}`)
          return
        }

        setError('Completed but no document ID')
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Request failed')
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    run()
    return () => {
      cancelled = true
    }
  }, [jobId, router])

  if (loading && !error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="mx-auto w-16 h-16 border-4 border-blue-200 rounded-full border-t-blue-500 animate-spin mb-4" />
          <p className="text-gray-600">
            {status ? `Indexing... (${status.status})` : 'Loading...'}
          </p>
          {status?.message && (
            <p className="text-sm text-gray-500 mt-2">{status.message}</p>
          )}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white rounded-xl shadow-sm border border-red-200 p-8 max-w-md">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Error</h2>
          <p className="text-red-600 mb-6">{error}</p>
          <button
            onClick={() => router.push('/chatbot')}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Back to Chatbot
          </button>
        </div>
      </div>
    )
  }

  return null
}
