/**
 * TanStack Query hooks for API calls
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import * as api from "./client";
import type { Workspace, Document, Clause, Conversation, QuestionResponse } from "../types";

// Workspaces
export function useWorkspaces() {
  return useQuery<Workspace[]>({
    queryKey: ["workspaces"],
    queryFn: () => api.workspacesApi.list(),
    retry: 2, // Limit retries to avoid infinite loops
    retryDelay: 1000, // Wait 1s between retries
  });
}

export function useWorkspace(id: string) {
  return useQuery<Workspace>({
    queryKey: ["workspaces", id],
    queryFn: () => api.workspacesApi.get(id),
    enabled: !!id,
  });
}

export function useCreateWorkspace() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { name: string; description?: string }) =>
      api.workspacesApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["workspaces"] });
    },
  });
}

// Documents
export function useDocuments(workspaceId: string) {
  return useQuery<Document[]>({
    queryKey: ["documents", workspaceId],
    queryFn: () => api.documentsApi.list(workspaceId),
    enabled: !!workspaceId,
  });
}

export function useDocument(id: string) {
  return useQuery<Document>({
    queryKey: ["documents", id],
    queryFn: () => api.documentsApi.get(id),
    enabled: !!id,
  });
}

export function useUploadDocument() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ workspaceId, file }: { workspaceId: string; file: File }) =>
      api.documentsApi.upload(workspaceId, file),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: ["documents", variables.workspaceId],
      });
    },
  });
}

export function useDeleteDocument() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.documentsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
    },
  });
}

// Clauses
export function useClauses(documentId: string) {
  return useQuery<Clause[]>({
    queryKey: ["clauses", documentId],
    queryFn: () => api.clausesApi.list(documentId),
    enabled: !!documentId,
  });
}

export function useExtractClauses() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (documentId: string) =>
      api.clausesApi.extract(documentId),
    onSuccess: (_, documentId) => {
      queryClient.invalidateQueries({
        queryKey: ["clauses", documentId],
      });
    },
  });
}

// Conversations
export function useConversations(workspaceId: string) {
  return useQuery<Conversation[]>({
    queryKey: ["conversations", workspaceId],
    queryFn: () => api.conversationsApi.list(workspaceId),
    enabled: !!workspaceId,
  });
}

export function useConversation(id: string) {
  return useQuery<Conversation>({
    queryKey: ["conversations", id],
    queryFn: () => api.conversationsApi.get(id),
    enabled: !!id,
  });
}

export function useCreateConversation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { workspace_id: string; title?: string }) =>
      api.conversationsApi.create(data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: ["conversations", variables.workspace_id],
      });
    },
  });
}

export function useAskQuestion() {
  return useMutation({
    mutationFn: ({
      workspaceId,
      question,
      options,
    }: {
      workspaceId: string;
      question: string;
      options?: { filter_document_id?: string; n_results?: number };
    }) => api.conversationsApi.askQuestion(workspaceId, question, options),
  });
}

export function useConversationMessages(conversationId: string) {
  return useQuery({
    queryKey: ["conversations", conversationId, "messages"],
    queryFn: () => api.conversationsApi.getMessages(conversationId),
    enabled: !!conversationId,
  });
}

export function useAskFollowUp() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      conversationId,
      question,
      options,
    }: {
      conversationId: string;
      question: string;
      options?: { filter_document_id?: string; n_results?: number };
    }) =>
      api.conversationsApi.askFollowUp(conversationId, question, options),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: ["conversations", variables.conversationId, "messages"],
      });
      queryClient.invalidateQueries({
        queryKey: ["conversations", variables.conversationId],
      });
    },
  });
}

