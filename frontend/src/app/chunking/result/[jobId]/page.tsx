'use client'

import { useParams, useSearchParams, useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import {
  getDocument,
  getPageImageUrl,
  getDocumentPreview,
  getChunkingStatus,
  getChunkingResult,
  pollChunkingUntilComplete,
} from '@/lib/api'
import type { Document, ChunkItem, ChunkingStatusResponse } from '@/types'

export default function ChunkingResultPage() {
  const params = useParams()
  const searchParams = useSearchParams()
  const router = useRouter()
  const jobId = params.jobId as string
  const documentId = searchParams.get('document_id') || ''

  const [document, setDocument] = useState<Document | null>(null)
  const [chunks, setChunks] = useState<ChunkItem[]>([])
  const [status, setStatus] = useState<ChunkingStatusResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const load = async () => {
      if (!jobId || !documentId) {
        setError('job_id 또는 document_id가 없습니다.')
        setLoading(false)
        return
      }

      try {
        setLoading(true)
        setError(null)

        // Load document for viewer
        const doc = await getDocument(documentId)
        setDocument(doc)

        // Poll until complete
        const finalStatus = await pollChunkingUntilComplete(jobId, (s) => setStatus(s))

        if (finalStatus.status === 'failed') {
          setError(finalStatus.error || 'Chunking 실패')
          setLoading(false)
          return
        }

        // Fetch result
        const result = await getChunkingResult(jobId)
        setChunks(result.chunks || [])
      } catch (err) {
        const msg = err instanceof Error ? err.message : 'Chunking 결과를 불러오지 못했습니다.'
        if (status?.status === 'failed') {
          setError(status.error || msg)
        } else {
          setError(msg)
        }
      } finally {
        setLoading(false)
      }
    }

    load()
  }, [jobId, documentId])

  if (loading && !document) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="mx-auto w-16 h-16 border-4 border-blue-200 rounded-full border-t-blue-500 animate-spin mb-4" />
          <p className="text-gray-600">
            {status ? `Chunking 중... (${status.status})` : '로딩 중...'}
          </p>
        </div>
      </div>
    )
  }

  if (error && !document) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white rounded-xl shadow-sm border border-red-200 p-8 max-w-md">
          <h2 className="text-xl font-bold text-gray-900 mb-4">오류</h2>
          <p className="text-red-600 mb-6">{error}</p>
          <button
            onClick={() => router.push('/chunking')}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Chunking 페이지로
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="px-8 py-6 border-b bg-white flex justify-between items-center">
        <h1 className="text-xl font-bold text-gray-900">
          Chunking 결과 {document?.filename && `· ${document.filename}`}
        </h1>
        <button
          onClick={() => router.push('/chunking')}
          className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 font-medium"
        >
          새 파일
        </button>
      </div>

      <div className="flex h-[calc(100vh-80px)]">
        {/* Left: Document viewer */}
        <div className="w-1/2 border-r bg-white overflow-auto p-6">
          {document && (
            <DocumentViewer document={document} />
          )}
          {!document && error && (
            <div className="text-gray-500 text-center py-12">
              문서를 불러올 수 없습니다.
            </div>
          )}
        </div>

        {/* Right: Chunks */}
        <div className="w-1/2 overflow-auto p-6">
          {loading ? (
            <div className="flex items-center gap-3 text-gray-600">
              <div className="w-5 h-5 border-2 border-blue-200 border-t-blue-500 rounded-full animate-spin" />
              <span>Chunking 처리 중...</span>
            </div>
          ) : error ? (
            <div className="text-red-600">{error}</div>
          ) : chunks.length === 0 ? (
            <div className="text-gray-500">청크가 없습니다.</div>
          ) : (
            <div className="space-y-4">
              <p className="text-sm font-medium text-gray-600">
                {chunks.length}개 청크
              </p>
              {chunks.map((c, idx) => (
                <ChunkCard key={c.uuid || idx} chunk={c} index={idx} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function XlsxPreview({ documentId }: { documentId: string }) {
  const [preview, setPreview] = useState<{ sheet_name: string; rows: string[][] } | null>(null)
  const [err, setErr] = useState<string | null>(null)

  useEffect(() => {
    getDocumentPreview(documentId)
      .then(setPreview)
      .catch((e) => setErr(e instanceof Error ? e.message : '미리보기 로드 실패'))
  }, [documentId])

  if (err) {
    return (
      <div className="text-gray-500 text-center py-8 text-sm">
        미리보기를 불러올 수 없습니다. {err}
      </div>
    )
  }
  if (!preview || preview.rows.length === 0) {
    return (
      <div className="text-gray-500 text-center py-8">
        <span className="inline-block w-6 h-6 border-2 border-gray-300 border-t-gray-600 rounded-full animate-spin" />
        <p className="mt-2">미리보기 로딩 중...</p>
      </div>
    )
  }

  const header = preview.rows[0] ?? []
  const bodyRows = preview.rows.slice(1)
  return (
    <div className="overflow-auto max-h-[70vh]">
      <p className="text-xs text-gray-500 mb-2">시트: {preview.sheet_name}</p>
      <table className="w-full border-collapse text-sm">
        <thead>
          <tr>
            {header.map((cell, i) => (
              <th
                key={i}
                className="border border-gray-300 bg-gray-100 px-2 py-1.5 text-left font-medium"
              >
                {cell}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {bodyRows.map((row, ri) => (
            <tr key={ri}>
              {row?.map((cell, ci) => (
                <td
                  key={ci}
                  className="border border-gray-200 px-2 py-1 text-gray-800"
                >
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function DocumentViewer({ document }: { document: Document }) {
  const [page, setPage] = useState(0)
  const pageCount = document.page_count || 1

  const imageUrl = getPageImageUrl(document.id, page)

  if (document.file_type?.toLowerCase() === 'txt') {
    return (
      <div className="text-gray-500 text-center py-12">
        .txt 파일은 페이지 미리보기를 지원하지 않습니다.
      </div>
    )
  }

  if (document.file_type?.toLowerCase() === 'xlsx') {
    return <XlsxPreview documentId={document.id} />
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <span className="text-sm text-gray-600">
          페이지 {page + 1} / {pageCount}
        </span>
        <div className="flex gap-2">
          <button
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={page <= 0}
            className="px-3 py-1 bg-gray-200 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-300"
          >
            이전
          </button>
          <button
            onClick={() => setPage((p) => Math.min(pageCount - 1, p + 1))}
            disabled={page >= pageCount - 1}
            className="px-3 py-1 bg-gray-200 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-300"
          >
            다음
          </button>
        </div>
      </div>
      <div className="bg-gray-100 rounded-lg overflow-hidden">
        <img
          src={imageUrl}
          alt={`Page ${page + 1}`}
          className="w-full h-auto max-h-[70vh] object-contain"
        />
      </div>
    </div>
  )
}

function ChunkCard({ chunk, index }: { chunk: ChunkItem; index: number }) {
  const [expanded, setExpanded] = useState(false)
  const pages = chunk.metadata?.doc_page || []
  const category = chunk.metadata?.category || []
  const pageStr = pages.length > 0 ? `P.${pages.join(', ')}` : ''
  const preview = chunk.chunk.slice(0, 200) + (chunk.chunk.length > 200 ? '...' : '')

  return (
    <div className="border border-gray-200 rounded-xl p-4 bg-white hover:border-gray-300 transition-colors">
      <div className="flex justify-between items-start gap-2 mb-2">
        <span className="text-xs font-medium text-gray-500">
          #{chunk.chunk_order + 1} {pageStr && `· ${pageStr}`}
          {category.length > 0 && ` · ${category.join(' > ')}`}
        </span>
        {chunk.score != null && (
          <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">
            {chunk.score.toFixed(2)}
          </span>
        )}
      </div>
      <div className="text-gray-800 text-sm">
        {expanded ? chunk.chunk : preview}
      </div>
      {chunk.chunk.length > 200 && (
        <button
          onClick={() => setExpanded(!expanded)}
          className="mt-2 text-xs text-blue-600 hover:text-blue-700"
        >
          {expanded ? '접기' : '펼치기'}
        </button>
      )}
    </div>
  )
}
