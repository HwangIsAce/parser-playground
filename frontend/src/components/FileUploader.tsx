'use client'

import { useState } from 'react'
import { uploadDocument } from '@/lib/api'
import { Document } from '@/types'

interface FileUploaderProps {
  onUploadComplete: (document: Document) => void
}

export default function FileUploader({ onUploadComplete }: FileUploaderProps) {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      setFile(selectedFile)
      setError(null)
    }
  }

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file')
      return
    }

    setUploading(true)
    setError(null)

    try {
      const document = await uploadDocument(file)
      onUploadComplete(document)
      setFile(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload file')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div style={{ marginBottom: '2rem' }}>
      <h2>Upload Document</h2>
      <div style={{ marginTop: '1rem' }}>
        <input
          type="file"
          onChange={handleFileChange}
          disabled={uploading}
          style={{ marginBottom: '1rem' }}
        />
        <br />
        <button
          onClick={handleUpload}
          disabled={uploading || !file}
          style={{
            padding: '0.5rem 1rem',
            backgroundColor: uploading ? '#ccc' : '#0070f3',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: uploading ? 'not-allowed' : 'pointer',
          }}
        >
          {uploading ? 'Uploading...' : 'Upload'}
        </button>
        {error && (
          <div style={{ color: 'red', marginTop: '0.5rem' }}>{error}</div>
        )}
      </div>
    </div>
  )
}
