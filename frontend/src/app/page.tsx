'use client'

import { useRouter } from 'next/navigation'
import FileUploader from '@/components/FileUploader'
import { Document } from '@/types'

export default function Home() {
  const router = useRouter()

  const handleDocumentUploaded = (doc: Document) => {
    // Navigate to document view page
    router.push(`/documents/${doc.id}`)
  }

  return (
    <main style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      <h1 style={{ marginBottom: '2rem' }}>Forge Playground</h1>
      
      <FileUploader onUploadComplete={handleDocumentUploaded} />
    </main>
  )
}
