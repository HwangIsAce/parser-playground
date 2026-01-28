'use client'

import { useState } from 'react'
import { parseDocument, getPageImageUrl } from '@/lib/api'
import { Document, ParseResult } from '@/types'

interface ResultViewerProps {
  document: Document
  parseResult: ParseResult | null
  onParseComplete: (result: ParseResult) => void
}

export default function ResultViewer({
  document,
  parseResult,
  onParseComplete,
}: ResultViewerProps) {
  const [mode, setMode] = useState<'basic' | 'enhance'>('basic')
  const [parsing, setParsing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleParse = async () => {
    setParsing(true)
    setError(null)

    try {
      const result = await parseDocument(document.id, 0, { mode })
      onParseComplete(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to parse document')
    } finally {
      setParsing(false)
    }
  }

  const imageUrl = getPageImageUrl(document.id, 0)

  return (
    <div style={{ marginTop: '2rem' }}>
      <h2>Document Viewer</h2>
      
      <div style={{ marginTop: '1rem', marginBottom: '1rem' }}>
        <label>
          Parse Mode:
          <select
            value={mode}
            onChange={(e) => setMode(e.target.value as 'basic' | 'enhance')}
            disabled={parsing}
            style={{ marginLeft: '0.5rem', padding: '0.25rem' }}
          >
            <option value="basic">Basic</option>
            <option value="enhance">Enhance</option>
          </select>
        </label>
        <button
          onClick={handleParse}
          disabled={parsing}
          style={{
            marginLeft: '1rem',
            padding: '0.5rem 1rem',
            backgroundColor: parsing ? '#ccc' : '#0070f3',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: parsing ? 'not-allowed' : 'pointer',
          }}
        >
          {parsing ? 'Parsing...' : 'Parse'}
        </button>
        {error && (
          <div style={{ color: 'red', marginTop: '0.5rem' }}>{error}</div>
        )}
      </div>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '2rem',
          marginTop: '2rem',
        }}
      >
        <div>
          <h3>Original Document</h3>
          <div
            style={{
              border: '1px solid #ddd',
              borderRadius: '4px',
              padding: '1rem',
              marginTop: '1rem',
            }}
          >
            <img
              src={imageUrl}
              alt={document.filename}
              style={{ maxWidth: '100%', height: 'auto' }}
            />
          </div>
        </div>

        <div>
          <h3>Parsed Result</h3>
          <div
            style={{
              border: '1px solid #ddd',
              borderRadius: '4px',
              padding: '1rem',
              marginTop: '1rem',
              minHeight: '200px',
            }}
          >
            {parseResult ? (
              <div>
                <p>Document ID: {parseResult.document_id}</p>
                <p>Blocks: {parseResult.blocks.length}</p>
                <div style={{ marginTop: '1rem' }}>
                  {parseResult.blocks.map((block, idx) => (
                    <div
                      key={idx}
                      style={{
                        marginBottom: '0.5rem',
                        padding: '0.5rem',
                        backgroundColor: '#f5f5f5',
                        borderRadius: '4px',
                      }}
                    >
                      <strong>{block.type}:</strong> {block.text}
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <p style={{ color: '#999' }}>No parse result yet. Click Parse to start.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
