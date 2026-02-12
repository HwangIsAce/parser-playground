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

// Chunking (Peter-parser) types
export type ChunkingDocumentType = 'heading' | 'plain' | 'slide' | 'lifelog' | 'excel'

export interface ChunkImageItem {
  uuid?: string
  file?: string
  image_path?: string
  image_title?: string
  image_context?: string
  image_type?: string
  image_keywords?: string[]
  potential_questions?: string[]
  page?: string
}

export interface ChunkMetadata {
  proj_title?: string
  doc_title?: string
  process_title?: string
  doc_unit?: string
  doc_page?: number[]
  category?: string[]
  images?: ChunkImageItem[]
}

export interface ChunkItem {
  uuid: string
  doc_title: string
  chunk: string
  chunk_order: number
  metadata?: ChunkMetadata
  score?: number | null
}

export interface ChunkResult {
  chunks: ChunkItem[]
}

export interface ChunkingParseResponse {
  job_id: string
  status: string
  document_id: string
}

export interface ChunkingStatusResponse {
  job_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  error?: string | null
  created_at: string
}

// PageIndex (Chatbot) types
export type PageIndexJobStatus = 'processing' | 'completed' | 'failed'

export interface PageIndexJobResponse {
  job_id: string
  status: PageIndexJobStatus
  document_id: string | null
  error: string | null
  progress: number
  message: string
}

export interface PageIndexDocumentSummary {
  id: string
  name: string
  doc_count: number
  created_at: string
}

export interface PageIndexTocNode {
  node_id: string
  structure: string
  title: string
  start_index: number
  end_index: number
  doc_id: string
  nodes: PageIndexTocNode[]
}

export interface PageIndexTocDoc {
  doc_id: string
  doc_name: string
  structure: PageIndexTocNode[]
}

export interface PageIndexTocResponse {
  doc_structures: PageIndexTocDoc[]
}

export interface PageIndexRetrievedNode {
  doc_id: string
  node_id: string
  structure: string
  title: string
}

export interface PageIndexQueryResponse {
  answer: string
  retrieved_nodes: PageIndexRetrievedNode[]
}
