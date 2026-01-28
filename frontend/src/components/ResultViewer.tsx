'use client'

import { useState, useEffect } from 'react'
import { parseDocument, getPageImageUrl } from '@/lib/api'
import { Document, ParseResult } from '@/types'

type TabType = 'blocks' | 'json' | 'html' | 'markdown'

interface ResultViewerProps {
  document: Document
  mode: 'basic' | 'enhance'
  parseResult: ParseResult | null
  onParseComplete: (result: ParseResult) => void
}

export default function ResultViewer({
  document,
  mode,
  parseResult,
  onParseComplete,
}: ResultViewerProps) {
  const [parsing, setParsing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<TabType>('blocks')

  useEffect(() => {
    // Auto-parse when document and mode are available
    if (document && mode && !parseResult && !parsing) {
      handleParse()
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }
  }, [document?.id, mode])

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

  const getBlockIcon = (type: string) => {
    switch (type) {
      case 'text':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h7" />
          </svg>
        )
      case 'table':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
        )
      case 'image':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        )
      default:
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
          </svg>
        )
    }
  }

  const convertToHtml = (result: ParseResult): string => {
    const htmlParts = ['<div class="parse-result">']
    for (const block of result.blocks) {
      if (block.type === 'text') {
        htmlParts.push(`<p>${escapeHtml(block.text)}</p>`)
      } else if (block.type === 'table') {
        htmlParts.push(`<table><tr><td>${escapeHtml(block.text)}</td></tr></table>`)
      } else {
        htmlParts.push(`<div class="${block.type}">${escapeHtml(block.text)}</div>`)
      }
    }
    htmlParts.push('</div>')
    return htmlParts.join('\n')
  }

  const convertToMarkdown = (result: ParseResult): string => {
    const markdownParts: string[] = []
    for (const block of result.blocks) {
      if (block.type === 'text') {
        markdownParts.push(block.text)
      } else if (block.type === 'table') {
        markdownParts.push(`\n${block.text}\n`)
      } else {
        markdownParts.push(`**${block.type}**: ${block.text}`)
      }
    }
    return markdownParts.join('\n\n')
  }

  const escapeHtml = (text: string): string => {
    const map: Record<string, string> = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#039;',
    }
    return text.replace(/[&<>"']/g, (m) => map[m])
  }

  const renderTabContent = () => {
    if (!parseResult) {
      return (
        <div className="text-center py-12 text-gray-500">
          <div className="relative mx-auto w-16 h-16 mb-4">
            <div className="absolute inset-0 border-4 border-gray-200 rounded-full"></div>
            <div className="absolute inset-0 border-4 border-blue-500 rounded-full border-t-transparent animate-spin"></div>
          </div>
          <p>Waiting for parse result...</p>
        </div>
      )
    }

    if (parseResult.blocks.length === 0) {
      return (
        <div className="text-center py-12 text-gray-500">
          <svg className="w-12 h-12 mx-auto mb-3 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p>No blocks found in parse result</p>
        </div>
      )
    }

    switch (activeTab) {
      case 'blocks':
        return (
          <div className="space-y-3">
            {parseResult.blocks.map((block, idx) => (
              <div
                key={idx}
                className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 hover:shadow-sm transition-all bg-white"
              >
                <div className="flex items-start gap-3">
                  <div className={`
                    flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center
                    ${
                      block.type === 'text' ? 'bg-blue-100 text-blue-600' :
                      block.type === 'table' ? 'bg-purple-100 text-purple-600' :
                      block.type === 'image' ? 'bg-green-100 text-green-600' :
                      'bg-gray-100 text-gray-600'
                    }
                  `}>
                    {getBlockIcon(block.type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
                        {block.type}
                      </span>
                      {block.bbox && (
                        <span className="text-xs text-gray-400">
                          ({Math.round(block.bbox.x)}, {Math.round(block.bbox.y)})
                        </span>
                      )}
                    </div>
                    <p className="text-gray-900 whitespace-pre-wrap break-words">
                      {block.text}
                    </p>
                    {block.metadata && Object.keys(block.metadata).length > 0 && (
                      <div className="mt-2 pt-2 border-t border-gray-100">
                        <details className="text-xs">
                          <summary className="text-gray-500 cursor-pointer hover:text-gray-700">
                            Metadata
                          </summary>
                          <pre className="mt-2 text-gray-600 overflow-x-auto">
                            {JSON.stringify(block.metadata, null, 2)}
                          </pre>
                        </details>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )
      case 'json':
        return (
          <div className="bg-gray-50 rounded-lg p-4 overflow-auto">
            <pre className="text-sm text-gray-800 whitespace-pre-wrap">
              {JSON.stringify(parseResult, null, 2)}
            </pre>
          </div>
        )
      case 'html':
        return (
          <div className="bg-gray-50 rounded-lg p-4 overflow-auto">
            <pre className="text-sm text-gray-800 whitespace-pre-wrap">
              {convertToHtml(parseResult)}
            </pre>
          </div>
        )
      case 'markdown':
        return (
          <div className="bg-gray-50 rounded-lg p-4 overflow-auto">
            <pre className="text-sm text-gray-800 whitespace-pre-wrap">
              {convertToMarkdown(parseResult)}
            </pre>
          </div>
        )
    }
  }

  return (
    <div className="space-y-6">
      {/* Status Bar */}
      {(parsing || error) && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          {parsing && (
            <div className="space-y-2">
              <div className="flex items-center gap-3">
                <div className="relative w-6 h-6">
                  <div className="absolute inset-0 border-2 border-blue-200 rounded-full"></div>
                  <div className="absolute inset-0 border-2 border-blue-500 rounded-full border-t-transparent animate-spin"></div>
                </div>
                <span className="text-gray-700 font-medium">
                  Parsing with {mode} mode...
                </span>
              </div>
              <p className="text-sm text-gray-500 ml-9">
                This may take up to 5 minutes. Please wait...
              </p>
            </div>
          )}
          {error && (
            <div className="flex items-center gap-3 text-red-600">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>{error}</span>
            </div>
          )}
        </div>
      )}

      {/* Main Content: Side by Side */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Original Document */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center gap-2 mb-4">
            <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h2 className="text-xl font-semibold text-gray-900">Original Document</h2>
          </div>
          <div className="border border-gray-200 rounded-lg overflow-hidden bg-gray-50">
            <img
              src={imageUrl}
              alt={document.filename}
              className="w-full h-auto"
            />
          </div>
        </div>

        {/* Right: Parsed Result with Tabs */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
              <h2 className="text-xl font-semibold text-gray-900">Parsed Result</h2>
            </div>
            {parseResult && (
              <span className="text-sm text-gray-500">
                {parseResult.blocks.length} block{parseResult.blocks.length !== 1 ? 's' : ''}
              </span>
            )}
          </div>

          {/* Tabs */}
          <div className="border-b border-gray-200 mb-4">
            <nav className="flex space-x-1" aria-label="Tabs">
              {(['blocks', 'json', 'html', 'markdown'] as TabType[]).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`
                    px-4 py-2 text-sm font-medium rounded-t-lg transition-colors
                    ${
                      activeTab === tab
                        ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                        : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                    }
                  `}
                >
                  {tab.charAt(0).toUpperCase() + tab.slice(1)}
                </button>
              ))}
            </nav>
          </div>

          {/* Tab Content */}
          <div className="max-h-[600px] overflow-y-auto">
            {renderTabContent()}
          </div>
        </div>
      </div>
    </div>
  )
}
