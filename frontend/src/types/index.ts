/**Type definitions for API responses and components.*/

export interface Document {
  id: string
  filename: string
  file_type: string
  page_count: number
  status: 'uploading' | 'processing' | 'completed' | 'failed'
  created_at: string
}

export interface Block {
  type: string
  text: string
  bbox?: {
    x: number
    y: number
    width: number
    height: number
  }
  metadata?: Record<string, any>
  /** Table/block HTML from parser (use for table layout) */
  content?: { html?: string; markdown?: string; text?: string }
}

export interface ParseResult {
  document_id: string
  blocks: Block[]
  metadata: Record<string, any>
}

export interface ParseRequest {
  mode: 'basic' | 'enhance'
  strategy?: string
  languages?: string[]
  render_html?: boolean
}

export type JobStatus = 'pending' | 'queued' | 'processing' | 'completed' | 'failed'

export interface Job {
  id: string
  document_id: string
  page_number: number
  mode: string
  status: JobStatus
  created_at: string
  started_at?: string
  completed_at?: string
  result?: ParseResult
  error?: string
}
