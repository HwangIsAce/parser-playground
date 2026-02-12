'use client'

import { useParams, useSearchParams, useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import {
  getDocument,
  getPageImageUrl,
  getDocumentXlsxSheets,
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
      <div className="max-w-7xl mx-auto px-8 py-12">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Chunking 결과</h1>
            <p className="text-gray-600">{document?.filename}</p>
          </div>
          <button
            onClick={() => router.push('/chunking')}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            New File
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 min-w-0">
            <div className="flex items-center gap-2 mb-4">
              <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <h2 className="text-xl font-semibold text-gray-900">Original Document</h2>
            </div>
            <div className="border border-gray-200 rounded-lg overflow-hidden bg-gray-50 min-h-[300px] max-h-[75vh] overflow-auto">
              {document && <DocumentViewer document={document} />}
              {!document && error && (
                <div className="text-gray-500 text-center py-12 p-6">문서를 불러올 수 없습니다.</div>
              )}
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 min-w-0">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                <h2 className="text-xl font-semibold text-gray-900">Chunking Result</h2>
              </div>
              {!loading && chunks.length > 0 && (
                <span className="text-sm text-gray-500">{chunks.length} chunk{chunks.length !== 1 ? 's' : ''}</span>
              )}
            </div>
            <div className="min-h-[300px] max-h-[75vh] overflow-auto min-w-0">
              {loading ? (
                <div className="flex items-center gap-3 text-gray-600 py-8">
                  <div className="relative w-6 h-6">
                    <div className="absolute inset-0 border-2 border-blue-200 rounded-full" />
                    <div className="absolute inset-0 border-2 border-blue-500 rounded-full border-t-transparent animate-spin" />
                  </div>
                  <span>Chunking 처리 중...</span>
                </div>
              ) : error ? (
                <div className="flex items-center gap-3 text-red-600 py-4">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>{error}</span>
                </div>
              ) : chunks.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <svg className="w-12 h-12 mx-auto mb-3 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                  </svg>
                  <p>청크가 없습니다.</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {chunks.map((c, idx) => (
                    <ChunkCard key={c.uuid || idx} chunk={c} index={idx} />
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function XlsxPreview({ documentId }: { documentId: string }) {
  const [sheets, setSheets] = useState<{ index: number; name: string }[]>([])
  const [sheetIndex, setSheetIndex] = useState(0)
  const [preview, setPreview] = useState<{ sheet_name: string; rows: string[][] } | null>(null)
  const [err, setErr] = useState<string | null>(null)
  const [loadingPreview, setLoadingPreview] = useState(false)

  useEffect(() => {
    getDocumentXlsxSheets(documentId)
      .then((r) => {
        setSheets(r.sheets || [])
        if ((r.sheets?.length ?? 0) > 0) setSheetIndex(0)
      })
      .catch((e) => setErr(e instanceof Error ? e.message : '시트 목록 로드 실패'))
  }, [documentId])

  useEffect(() => {
    if (sheets.length === 0) return
    setLoadingPreview(true)
    getDocumentPreview(documentId, sheetIndex)
      .then(setPreview)
      .catch((e) => setErr(e instanceof Error ? e.message : '미리보기 로드 실패'))
      .finally(() => setLoadingPreview(false))
  }, [documentId, sheetIndex, sheets.length])

  if (err && sheets.length === 0) {
    return (
      <div className="text-gray-500 text-center py-8 text-sm">
        미리보기를 불러올 수 없습니다. {err}
      </div>
    )
  }
  if (sheets.length === 0) {
    return (
      <div className="text-gray-500 text-center py-8">
        <span className="inline-block w-6 h-6 border-2 border-gray-300 border-t-gray-600 rounded-full animate-spin" />
        <p className="mt-2">시트 목록 로딩 중...</p>
      </div>
    )
  }

  const header = preview?.rows?.[0] ?? []
  const bodyRows = preview?.rows?.slice(1) ?? []
  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-1.5 border-b border-gray-200 pb-2">
        {sheets.map((s) => (
          <button
            key={s.index}
            type="button"
            onClick={() => setSheetIndex(s.index)}
            className={`px-3 py-1.5 rounded-t text-sm font-medium transition-colors ${
              sheetIndex === s.index
                ? 'bg-blue-100 text-blue-700 border border-b-0 border-blue-200 -mb-px'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200 border border-transparent'
            }`}
          >
            {s.name}
          </button>
        ))}
      </div>
      <div className="overflow-auto max-h-[65vh]">
        {loadingPreview ? (
          <div className="text-gray-500 text-center py-6 text-sm">시트 로딩 중...</div>
        ) : (
          <>
            <p className="text-xs text-gray-500 mb-2">시트: {preview?.sheet_name ?? sheets[sheetIndex]?.name}</p>
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
          </>
        )}
      </div>
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

/** Parse chunk text into rows/columns: split by tab or 2+ spaces. */
function parseChunkAsTable(text: string): string[][] | null {
  const lines = text.split('\n').map((s) => s.trim()).filter(Boolean)
  if (lines.length < 2) return null
  const rows: string[][] = []
  for (const line of lines) {
    const cells = line.includes('\t')
      ? line.split('\t').map((c) => c.trim())
      : line.split(/\s{2,}/).map((c) => c.trim())
    rows.push(cells)
  }
  const maxCols = Math.max(...rows.map((r) => r.length))
  if (maxCols < 2) return null
  return rows.map((r) => (r.length < maxCols ? [...r, ...Array(maxCols - r.length).fill('')] : r))
}

function ChunkCard({ chunk, index }: { chunk: ChunkItem; index: number }) {
  const [expanded, setExpanded] = useState(true)
  const pages = chunk.metadata?.doc_page || []
  const category = chunk.metadata?.category || []
  const pageStr = pages.length > 0 ? `P.${pages.join(', ')}` : ''
  const extra = (chunk.metadata as Record<string, unknown> | undefined)?.extra as { excel?: { sheet_name?: string } } | undefined
  const sheetLabel = extra?.excel?.sheet_name ? ` · ${extra.excel.sheet_name}` : ''

  const tableData = parseChunkAsTable(chunk.chunk)

  return (
    <div className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 hover:shadow-sm transition-all bg-white">
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center bg-blue-100 text-blue-600">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h7" />
          </svg>
        </div>
        <div className="flex-1 min-w-0">
          <button
            type="button"
            onClick={() => setExpanded((e) => !e)}
            className="w-full flex justify-between items-center gap-2 text-left hover:opacity-80 transition-opacity"
          >
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">chunk</span>
              <span className="text-sm font-medium text-gray-700">
                #{chunk.chunk_order + 1}
                {pageStr && ` · ${pageStr}`}
                {category.length > 0 && ` · ${category.join(' > ')}`}
                {sheetLabel}
              </span>
            </div>
            <span className="flex items-center gap-1 shrink-0 text-gray-400" aria-hidden>
              {chunk.score != null && (
                <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">{chunk.score.toFixed(2)}</span>
              )}
              {expanded ? (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
              ) : (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
              )}
            </span>
          </button>
          {expanded && (
            <div className="text-gray-800 text-sm overflow-x-auto mt-3">
          {tableData ? (
            <table className="w-full border-collapse text-sm tabular-nums">
              <thead>
                <tr>
                  {tableData[0].map((cell, i) => (
                    <th
                      key={i}
                      className="border border-gray-200 bg-gray-100 px-2 py-1.5 text-left font-medium whitespace-nowrap"
                    >
                      {cell}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {tableData.slice(1).map((row, ri) => (
                  <tr key={ri} className="border-b border-gray-100 last:border-0 hover:bg-gray-50/50">
                    {row.map((cell, ci) => (
                      <td
                        key={ci}
                        className="border border-gray-100 px-2 py-1.5 text-gray-800 break-words align-top"
                      >
                        {cell}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="whitespace-pre-wrap break-words">{chunk.chunk}</div>
          )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
