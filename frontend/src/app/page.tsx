'use client'

import { useState } from 'react'
import FileUploader from '@/components/FileUploader'
import ResultViewer from '@/components/ResultViewer'
import { Document, ParseResult } from '@/types'

export default function Home() {
  const [document, setDocument] = useState<Document | null>(null)
  const [parseResult, setParseResult] = useState<ParseResult | null>(null)

  const handleDocumentUploaded = (doc: Document) => {
    setDocument(doc)
    setParseResult(null)
  }

  const handleParseComplete = (result: ParseResult) => {
    setParseResult(result)
  }

  return (
    <main style={{ padding: '2rem', maxWidth: '1400px', margin: '0 auto' }}>
      <h1 style={{ marginBottom: '2rem' }}>Forge Playground</h1>
      
      <FileUploader onUploadComplete={handleDocumentUploaded} />
      
      {document && (
        <ResultViewer
          document={document}
          parseResult={parseResult}
          onParseComplete={handleParseComplete}
        />
      )}
    </main>
  )
}
