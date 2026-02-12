'use client'

import { useParams, useRouter } from 'next/navigation'
import { useCallback, useEffect, useRef, useState } from 'react'
import Link from 'next/link'
import { pageindexGetToc, pageindexQuery } from '@/lib/api'
import type {
  PageIndexRetrievedNode,
  PageIndexTocNode,
  PageIndexTocResponse,
} from '@/types'

function tocNodeKey(docId: string, nodeId: string): string {
  return `${docId}:${nodeId}`
}

function TocTree({
  nodes,
  highlightSet,
  depth = 0,
}: {
  nodes: PageIndexTocNode[]
  highlightSet: Set<string>
  depth?: number
}) {
  return (
    <ul className={depth > 0 ? 'ml-4 border-l border-gray-200 pl-3' : 'space-y-1'}>
      {nodes.map((node) => {
        const key = tocNodeKey(node.doc_id, node.node_id)
        const highlighted = highlightSet.has(key)
        return (
          <li key={key} className="py-0.5">
            <div
              data-doc-id={node.doc_id}
              data-node-id={node.node_id}
              className={`
                rounded px-2 py-1 text-sm
                ${highlighted
                  ? 'bg-amber-100 border-l-2 border-amber-500 font-medium'
                  : 'text-gray-700 hover:bg-gray-100'
                }
              `}
            >
              <span className="text-gray-500 font-mono mr-2">{node.structure}</span>
              {node.title}
            </div>
            {(node.nodes?.length ?? 0) > 0 && (
              <TocTree nodes={node.nodes ?? []} highlightSet={highlightSet} depth={depth + 1} />
            )}
          </li>
        )
      })}
    </ul>
  )
}

export default function ChatbotDocumentPage() {
  const params = useParams()
  const router = useRouter()
  const documentId = params.documentId as string

  const [toc, setToc] = useState<PageIndexTocResponse | null>(null)
  const [tocError, setTocError] = useState<string | null>(null)
  const [messages, setMessages] = useState<
    Array<{
      role: 'user' | 'assistant'
      content: string
      retrieved_nodes?: PageIndexRetrievedNode[]
    }>
  >([])
  const [input, setInput] = useState('')
  const [queryLoading, setQueryLoading] = useState(false)
  const [queryError, setQueryError] = useState<string | null>(null)

  // Highlight only the latest answer's retrieved_nodes
  const [highlightedNodes, setHighlightedNodes] = useState<PageIndexRetrievedNode[]>([])
  const highlightSet = new Set(highlightedNodes.map((n) => tocNodeKey(n.doc_id, n.node_id)))
  const tocScrollRef = useRef<HTMLDivElement>(null)

  // Scroll TOC so first highlighted node is in the vertical center of the right panel
  useEffect(() => {
    if (highlightedNodes.length === 0 || !tocScrollRef.current) return
    const first = highlightedNodes[0]
    const el = tocScrollRef.current.querySelector(
      `[data-doc-id="${first.doc_id}"][data-node-id="${first.node_id}"]`
    )
    if (el) {
      el.scrollIntoView({ block: 'center', behavior: 'smooth' })
    }
  }, [highlightedNodes])

  const loadToc = useCallback(async () => {
    if (!documentId) return
    try {
      setTocError(null)
      const data = await pageindexGetToc(documentId)
      setToc(data)
    } catch (e) {
      setTocError(e instanceof Error ? e.message : 'Failed to load TOC')
    }
  }, [documentId])

  useEffect(() => {
    loadToc()
  }, [loadToc])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const q = input.trim()
    if (!q || !documentId) return

    setQueryError(null)
    setInput('')
    setMessages((prev) => [...prev, { role: 'user', content: q }])
    setQueryLoading(true)

    try {
      const res = await pageindexQuery(documentId, q)
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: res.answer,
          retrieved_nodes: res.retrieved_nodes,
        },
      ])
      setHighlightedNodes(res.retrieved_nodes ?? [])
    } catch (e) {
      setQueryError(e instanceof Error ? e.message : 'Query failed')
      setMessages((prev) => prev.slice(0, -1))
    } finally {
      setQueryLoading(false)
    }
  }

  if (!documentId) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-600">Invalid document</p>
      </div>
    )
  }

  return (
    <div className="h-screen flex flex-col overflow-hidden bg-gray-50">
      <header className="flex-shrink-0 border-b border-gray-200 bg-white px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link
            href="/chatbot"
            className="text-sm font-medium text-blue-600 hover:text-blue-700"
          >
            ← Chatbot
          </Link>
          <span className="text-sm text-gray-500 font-mono truncate max-w-[200px]">
            {documentId}
          </span>
        </div>
      </header>

      <div className="flex-1 flex flex-col lg:flex-row min-h-0 overflow-hidden">
        {/* Left: Chat — messages scroll, input fixed at bottom of viewport */}
        <div className="flex-1 flex flex-col min-w-0 min-h-0 border-r border-gray-200 bg-white">
          <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-0">
            {messages.length === 0 && !queryLoading && (
              <p className="text-gray-500 text-sm">Ask a question about this document.</p>
            )}
            {messages.map((m, i) => (
              <div
                key={i}
                className={
                  m.role === 'user'
                    ? 'flex justify-end'
                    : 'flex justify-start'
                }
              >
                <div
                  className={
                    m.role === 'user'
                      ? 'max-w-[85%] rounded-2xl bg-blue-600 text-white px-4 py-2'
                      : 'max-w-[85%] rounded-2xl bg-gray-100 text-gray-900 px-4 py-2'
                  }
                >
                  <p className="text-sm whitespace-pre-wrap">{m.content}</p>
                </div>
              </div>
            ))}
            {queryLoading && (
              <div className="flex justify-start">
                <div className="rounded-2xl bg-gray-100 px-4 py-2">
                  <span className="text-sm text-gray-500">Thinking...</span>
                </div>
              </div>
            )}
          </div>
          {queryError && (
            <div className="flex-shrink-0 px-4 py-2 bg-red-50 border-t border-red-100">
              <p className="text-sm text-red-600">{queryError}</p>
            </div>
          )}
          <form onSubmit={handleSubmit} className="flex-shrink-0 p-4 border-t border-gray-200 bg-white">
            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask a question..."
                className="flex-1 rounded-xl border border-gray-300 px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={queryLoading}
              />
              <button
                type="submit"
                disabled={queryLoading || !input.trim()}
                className="px-4 py-2 bg-blue-600 text-white rounded-xl text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed hover:bg-blue-700"
              >
                Send
              </button>
            </div>
          </form>
        </div>

        {/* Right: TOC — scroll so highlighted node is in vertical center */}
        <aside className="w-full lg:w-80 flex-shrink-0 flex flex-col min-h-0 bg-gray-50 border-t lg:border-t-0 lg:border-l border-gray-200">
          <div className="flex-shrink-0 p-3 border-b border-gray-200 bg-white">
            <h2 className="text-sm font-semibold text-gray-900">Table of contents</h2>
            {highlightedNodes.length > 0 && (
              <p className="text-xs text-amber-700 mt-1">
                Highlighted: sections used for the last answer
              </p>
            )}
          </div>
          <div ref={tocScrollRef} className="flex-1 overflow-y-auto p-3 min-h-0">
            {tocError && (
              <p className="text-sm text-red-600">{tocError}</p>
            )}
            {toc && !tocError && (
              <div className="space-y-4">
                {toc.doc_structures.map((doc) => (
                  <div key={doc.doc_id}>
                    <p className="text-xs font-medium text-gray-500 mb-2 truncate" title={doc.doc_name}>
                      {doc.doc_name}
                    </p>
                    <TocTree nodes={doc.structure} highlightSet={highlightSet} />
                  </div>
                ))}
              </div>
            )}
          </div>
        </aside>
      </div>
    </div>
  )
}
