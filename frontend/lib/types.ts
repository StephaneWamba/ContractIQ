/**
 * TypeScript types for ContractIQ Frontend
 * These should match the backend API response types
 */

export interface Workspace {
  id: string;
  name: string;
  description?: string;
  is_temporary: boolean;
  created_at: string;
  updated_at: string;
}

export interface Document {
  id: string;
  workspace_id: string;
  name: string;
  original_filename: string;
  file_path: string;
  file_type: "PDF" | "DOCX";
  status: "UPLOADED" | "PROCESSING" | "PROCESSED" | "FAILED";
  page_count?: number;
  file_size: number;
  created_at: string;
  updated_at: string;
}

export interface Clause {
  id: string;
  document_id: string;
  clause_type: string;
  extracted_text: string;
  page_number: number;
  section?: string;
  confidence_score?: number;
  risk_flags?: string[] | null;
  coordinates?: {
    x: number;
    y: number;
    width: number;
    height: number;
  } | null;
  created_at: string;
}

export type RiskLevel = "critical" | "high" | "medium" | "low";

export interface RiskSummary {
  critical: number;
  high: number;
  medium: number;
  low: number;
}

export interface Citation {
  index: number;
  document_name: string;
  page: number;
  section: string;
  excerpt: string;
  score?: number;
  clause_type?: string;
}

export interface Source {
  document_name: string;
  page: number;
  section: string;
}

export interface QuestionResponse {
  answer: string;
  citations: Citation[];
  sources: Source[];
  retrieval_results_count?: number;
}

export interface Conversation {
  id: string;
  workspace_id: string;
  title?: string;
  created_at: string;
  updated_at: string;
}

export interface ConversationMessage {
  id: string;
  conversation_id: string;
  role: "user" | "assistant";
  content: string;
  citations?: Citation[] | null;
  created_at: string;
}


