/**
 * API Client for ContractIQ Backend
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002/api/v1";

class ApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    public data?: any
  ) {
    super(`API Error: ${status} ${statusText}`);
    this.name = "ApiError";
  }
}

export async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_URL}${endpoint}`;
  
  // Get auth token from localStorage if available
  const token = typeof window !== "undefined" ? localStorage.getItem("auth_token") : null;
  
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...options?.headers,
  };
  
  if (token && !headers["Authorization"]) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  
  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new ApiError(
      response.status,
      response.statusText,
      errorData
    );
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return null as T;
  }

  return response.json();
}

// Workspaces
export const workspacesApi = {
  list: () => fetchApi<any[]>("/workspaces"),
  get: (id: string) => fetchApi<any>(`/workspaces/${id}`),
  create: (data: { name: string; description?: string }) =>
    fetchApi<any>("/workspaces", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  update: (id: string, data: { name?: string; description?: string }) =>
    fetchApi<any>(`/workspaces/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
  delete: (id: string) =>
    fetchApi<void>(`/workspaces/${id}`, { method: "DELETE" }),
};

// Documents
export const documentsApi = {
  list: (workspaceId: string) =>
    fetchApi<any[]>(`/documents/workspace/${workspaceId}`),
  get: (id: string) => fetchApi<any>(`/documents/${id}`),
  upload: async (workspaceId: string, file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    
    const response = await fetch(
      `${API_URL}/documents?workspace_id=${workspaceId}`,
      {
        method: "POST",
        body: formData,
      }
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new ApiError(response.status, response.statusText, errorData);
    }

    return response.json();
  },
  delete: (id: string) =>
    fetchApi<void>(`/documents/${id}`, { method: "DELETE" }),
};

// Clauses
export const clausesApi = {
  list: (documentId: string) =>
    fetchApi<any[]>(`/clauses/document/${documentId}`),
  get: (id: string) => fetchApi<any>(`/clauses/${id}`),
  extract: (documentId: string) =>
    fetchApi<any>(`/clauses/extract`, {
      method: "POST",
      body: JSON.stringify({ document_id: documentId }),
    }),
};

// Conversations & Q&A
export const conversationsApi = {
  list: (workspaceId: string) =>
    fetchApi<any[]>(`/workspaces/${workspaceId}/conversations`),
  get: (id: string) => fetchApi<any>(`/conversations/${id}`),
  create: (data: { workspace_id: string; title?: string }) =>
    fetchApi<any>("/conversations", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  getMessages: (conversationId: string) =>
    fetchApi<any[]>(`/conversations/${conversationId}/messages`),
  askQuestion: (workspaceId: string, question: string, options?: {
    filter_document_id?: string;
    n_results?: number;
  }) =>
    fetchApi<any>("/ask", {
      method: "POST",
      body: JSON.stringify({
        workspace_id: workspaceId,
        question,
        ...options,
      }),
    }),
  askFollowUp: (conversationId: string, question: string, options?: {
    filter_document_id?: string;
    n_results?: number;
  }) =>
    fetchApi<any>(`/conversations/${conversationId}/ask`, {
      method: "POST",
      body: JSON.stringify({
        question,
        ...options,
      }),
    }),
};

