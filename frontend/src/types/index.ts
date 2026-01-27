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
