'use client'

import { useParams, useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import ResultViewer from '@/components/ResultViewer'
import { getDocument } from '@/lib/api'
import { Document, ParseResult } from '@/types'

export default function DocumentViewPage() {
  const params = useParams()
  const router = useRouter()
  const documentId = params.id as string

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
      <main style={{ padding: '2rem', maxWidth: '1400px', margin: '0 auto' }}>
        <p>Loading document...</p>
      </main>
    )
  }

  if (error || !document) {
    return (
      <main style={{ padding: '2rem', maxWidth: '1400px', margin: '0 auto' }}>
        <h1>Forge Playground</h1>
        <div style={{ color: 'red', marginTop: '1rem' }}>
          {error || 'Document not found'}
        </div>
        <button
          onClick={handleNewFile}
          style={{
            marginTop: '1rem',
            padding: '0.5rem 1rem',
            backgroundColor: '#0070f3',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          New File
        </button>
      </main>
    )
  }

  return (
    <main style={{ padding: '2rem', maxWidth: '1400px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1>Forge Playground</h1>
        <button
          onClick={handleNewFile}
          style={{
            padding: '0.5rem 1rem',
            backgroundColor: '#0070f3',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          New File
        </button>
      </div>

      <ResultViewer
        document={document}
        parseResult={parseResult}
        onParseComplete={handleParseComplete}
      />
    </main>
  )
}
