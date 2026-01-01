/**
 * API Client for ContractIQ Backend
 * 
 * Provides type-safe API methods with error handling and performance optimizations
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002/api/v1';

export interface ApiError {
  detail: string;
  status: number;
}

export interface User {
  id: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  created_at: string;
}

export interface Token {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface UserProfile {
  user: User;
  token: Token;
}

class ApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
    // Load token from localStorage on initialization
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('auth_token');
    }
  }

  setToken(token: string | null) {
    this.token = token;
    if (typeof window !== 'undefined') {
      if (token) {
        localStorage.setItem('auth_token', token);
      } else {
        localStorage.removeItem('auth_token');
      }
    }
  }

  getToken(): string | null {
    return this.token;
  }

  isAuthenticated(): boolean {
    return !!this.token;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const headers: HeadersInit = {
      ...options.headers,
    };

    // Only set Content-Type for JSON requests (not for FormData)
    if (!(options.body instanceof FormData) && !headers['Content-Type']) {
      headers['Content-Type'] = 'application/json';
    }

    // Add auth token if available
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }
    
    const config: RequestInit = {
      ...options,
      headers,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        // Try to parse error response as JSON first
        let errorDetail = 'Unknown error';
        try {
          const errorText = await response.text();
          try {
            const errorJson = JSON.parse(errorText);
            errorDetail = errorJson.detail || errorJson.message || errorText;
          } catch {
            errorDetail = errorText || `HTTP ${response.status}`;
          }
        } catch {
          errorDetail = `HTTP ${response.status}`;
        }
        
        const error: ApiError = {
          detail: errorDetail,
          status: response.status,
        };
        throw error;
      }

      // Handle 204 No Content
      if (response.status === 204) {
        return null as T;
      }

      return await response.json();
    } catch (error) {
      if (error instanceof TypeError) {
        throw {
          detail: 'Network error. Please check your connection.',
          status: 0,
        } as ApiError;
      }
      throw error;
    }
  }

  // Authentication APIs
  async register(email: string, password: string, fullName?: string): Promise<UserProfile> {
    const response = await this.request<UserProfile>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, full_name: fullName }),
    });
    if (response.token) {
      this.setToken(response.token.access_token);
    }
    return response;
  }

  async login(email: string, password: string): Promise<UserProfile> {
    const response = await this.request<UserProfile>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    if (response.token) {
      this.setToken(response.token.access_token);
    }
    return response;
  }

  async getCurrentUser(): Promise<User> {
    return this.request<User>('/auth/me');
  }

  async refreshToken(): Promise<Token> {
    const response = await this.request<Token>('/auth/refresh', {
      method: 'POST',
    });
    if (response.access_token) {
      this.setToken(response.access_token);
    }
    return response;
  }

  logout() {
    this.setToken(null);
  }

  // Workspace APIs
  async getWorkspaces() {
    return this.request<Workspace[]>('/workspaces/');
  }

  async getWorkspace(id: string) {
    return this.request<Workspace>(`/workspaces/${id}`);
  }

  async createWorkspace(data: { name: string; description?: string; is_temporary?: boolean }) {
    return this.request<Workspace>('/workspaces/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async deleteWorkspace(id: string) {
    return this.request<void>(`/workspaces/${id}`, {
      method: 'DELETE',
    });
  }

  // Document APIs
  async getDocuments(workspaceId?: string) {
    const params = workspaceId ? `?workspace_id=${workspaceId}` : '';
    return this.request<Document[]>(`/documents/${params}`);
  }

  async getDocument(id: string) {
    return this.request<Document>(`/documents/${id}`);
  }

  getDocumentFileUrl(id: string): string {
    // Include token in URL as query parameter for PDF viewer compatibility
    // The backend will extract it from Authorization header or query param
    const token = this.token ? `?token=${encodeURIComponent(this.token)}` : '';
    return `${this.baseUrl}/documents/${id}/file${token}`;
  }
  
  // Alternative: Get document file with proper auth headers (for fetch-based requests)
  async getDocumentFile(id: string): Promise<Blob> {
    const response = await fetch(`${this.baseUrl}/documents/${id}/file`, {
      headers: this.token ? {
        'Authorization': `Bearer ${this.token}`
      } : {}
    });
    
    if (!response.ok) {
      throw {
        detail: await response.text().catch(() => 'Failed to fetch document'),
        status: response.status,
      } as ApiError;
    }
    
    return await response.blob();
  }

  async uploadDocument(
    workspaceId: string,
    file: File,
    onProgress?: (progress: number) => void
  ): Promise<Document> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('workspace_id', workspaceId);

    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();

      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable && onProgress) {
          const progress = (e.loaded / e.total) * 100;
          onProgress(progress);
        }
      });

      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const response = JSON.parse(xhr.responseText);
            resolve(response);
          } catch (e) {
            reject({ detail: 'Invalid response', status: xhr.status });
          }
        } else {
          reject({ detail: xhr.responseText || 'Upload failed', status: xhr.status });
        }
      });

      xhr.addEventListener('error', () => {
        reject({ detail: 'Network error', status: 0 });
      });

      // Backend has both /documents/ and /documents/upload endpoints
      const url = `${this.baseUrl}/documents/upload`;
      xhr.open('POST', url);
      
      // Add Authorization header if token is available
      if (this.token) {
        xhr.setRequestHeader('Authorization', `Bearer ${this.token}`);
      }
      
      xhr.send(formData);
    });
  }

  async deleteDocument(id: string) {
    return this.request<void>(`/documents/${id}`, {
      method: 'DELETE',
    });
  }

  // Clause APIs
  async extractClauses(documentId: string, forceReExtract = false) {
    return this.request<{ clauses: Clause[] }>(
      `/documents/${documentId}/extract-clauses`,
      {
        method: 'POST',
        body: JSON.stringify({ force_re_extract: forceReExtract }),
      }
    );
  }

  async getClauses(
    documentId: string,
    filters?: {
      clause_type?: string;
      min_risk_score?: number;
      max_risk_score?: number;
      has_risk_flags?: boolean;
    }
  ) {
    const params = new URLSearchParams();
    if (filters?.clause_type) params.append('clause_type', filters.clause_type);
    if (filters?.min_risk_score !== undefined)
      params.append('min_risk_score', filters.min_risk_score.toString());
    if (filters?.max_risk_score !== undefined)
      params.append('max_risk_score', filters.max_risk_score.toString());
    if (filters?.has_risk_flags !== undefined)
      params.append('has_risk_flags', filters.has_risk_flags.toString());

    const query = params.toString();
    const response = await this.request<{ total: number; clauses: Clause[] }>(
      `/documents/${documentId}/clauses${query ? `?${query}` : ''}`
    );
    return response.clauses;
  }

  async getClause(id: string) {
    return this.request<Clause>(`/clauses/${id}`);
  }

  async deleteClause(id: string) {
    return this.request<void>(`/clauses/${id}`, {
      method: 'DELETE',
    });
  }

  // Conversation APIs
  async getConversations(workspaceId: string) {
    const response = await this.request<{ total: number; conversations: Conversation[] }>(
      `/workspaces/${workspaceId}/conversations`
    );
    return response.conversations;
  }

  async createConversation(workspaceId: string, title: string) {
    return this.request<Conversation>(`/workspaces/${workspaceId}/conversations`, {
      method: 'POST',
      body: JSON.stringify({ title }),
    });
  }

  async getConversation(id: string) {
    return this.request<Conversation>(`/conversations/${id}`);
  }

  async updateConversation(conversationId: string, title: string) {
    return this.request<Conversation>(`/conversations/${conversationId}`, {
      method: 'PATCH',
      body: JSON.stringify({ title }),
    });
  }

  async askQuestion(
    conversationId: string,
    question: string,
    documentIds?: string[]
  ): Promise<{ answer: string; citations: Citation[] }> {
    return this.request(`/conversations/${conversationId}/ask`, {
      method: 'POST',
      body: JSON.stringify({ question, document_ids: documentIds }),
    });
  }

  // Export methods
  async downloadEvidencePack(conversationId: string, messageId: string): Promise<Blob> {
    const response = await fetch(
      `${this.baseUrl}/conversations/${conversationId}/messages/${messageId}/evidence-pack`,
      {
        headers: this.token ? {
          'Authorization': `Bearer ${this.token}`
        } : {}
      }
    );
    
    if (!response.ok) {
      throw {
        detail: await response.text().catch(() => 'Failed to download evidence pack'),
        status: response.status,
      } as ApiError;
    }
    
    return await response.blob();
  }

  async exportClauses(documentId: string, format: 'json' | 'csv' = 'json'): Promise<Blob> {
    const response = await fetch(
      `${this.baseUrl}/documents/${documentId}/clauses/export?format=${format}`,
      {
        headers: this.token ? {
          'Authorization': `Bearer ${this.token}`
        } : {}
      }
    );
    
    if (!response.ok) {
      throw {
        detail: await response.text().catch(() => 'Failed to export clauses'),
        status: response.status,
      } as ApiError;
    }
    
    return await response.blob();
  }

  async downloadReviewChecklist(documentId: string): Promise<Blob> {
    const response = await fetch(
      `${this.baseUrl}/documents/${documentId}/review-checklist`,
      {
        headers: this.token ? {
          'Authorization': `Bearer ${this.token}`
        } : {}
      }
    );
    
    if (!response.ok) {
      throw {
        detail: await response.text().catch(() => 'Failed to download review checklist'),
        status: response.status,
      } as ApiError;
    }
    
    return await response.blob();
  }

  async downloadHighlightedContract(documentId: string): Promise<Blob> {
    const response = await fetch(
      `${this.baseUrl}/documents/${documentId}/highlighted-contract`,
      {
        headers: this.token ? {
          'Authorization': `Bearer ${this.token}`
        } : {}
      }
    );
    
    if (!response.ok) {
      throw {
        detail: await response.text().catch(() => 'Failed to download highlighted contract'),
        status: response.status,
      } as ApiError;
    }
    
    return await response.blob();
  }

  async downloadConversationEvidencePack(conversationId: string): Promise<Blob> {
    const response = await fetch(
      `${this.baseUrl}/conversations/${conversationId}/evidence-pack`,
      {
        headers: this.token ? {
          'Authorization': `Bearer ${this.token}`
        } : {}
      }
    );
    
    if (!response.ok) {
      throw {
        detail: await response.text().catch(() => 'Failed to download conversation evidence pack'),
        status: response.status,
      } as ApiError;
    }
    
    return await response.blob();
  }

  async deleteConversation(id: string) {
    return this.request<void>(`/conversations/${id}`, {
      method: 'DELETE',
    });
  }
}

// Type definitions
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
  file_type: 'PDF' | 'DOCX';
  status: 'pending' | 'processing' | 'processed' | 'failed';
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
  section: string;
  confidence_score: number;
  risk_score?: number;
  risk_flags?: string[];
  risk_reasoning?: string;
  clause_subtype?: string;
  created_at: string;
}

export interface Conversation {
  id: string;
  workspace_id: string;
  title: string | null;
  created_at: string;
  updated_at: string;
  messages?: any[]; // Optional, not always included
}

export interface Citation {
  document_id: string;
  document_name: string;
  page_number: number;
  section_name: string;
  text_excerpt: string;
  similarity_score: number;
  chunk_id?: string;
  coordinates?: {
    x0: number;
    y0: number;
    x1: number;
    y1: number;
    page: number;
  };
}

// Export singleton instance
export const api = new ApiClient();

