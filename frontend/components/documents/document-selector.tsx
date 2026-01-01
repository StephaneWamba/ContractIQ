"use client";

import { useState, useEffect, useCallback } from "react";
import { api, Document } from "@/lib/api";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { Loader2, FileText } from "lucide-react";
import { toast } from "sonner";
import { useRouter } from "next/navigation";

interface DocumentSelectorProps {
  workspaceId: string;
  selectedDocumentId?: string;
  onDocumentSelect?: (documentId: string) => void;
}

export function DocumentSelector({
  workspaceId,
  selectedDocumentId,
  onDocumentSelect,
}: DocumentSelectorProps) {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  const fetchDocuments = useCallback(async () => {
    if (!workspaceId) {
      setDocuments([]);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const data = await api.getDocuments(workspaceId);
      setDocuments(data);
    } catch (error: any) {
      toast.error("Failed to load documents", {
        description: error.detail || "Please try again",
      });
    } finally {
      setLoading(false);
    }
  }, [workspaceId]);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const handleValueChange = (documentId: string) => {
    if (onDocumentSelect) {
      onDocumentSelect(documentId);
    } else {
      router.push(`/clauses?documentId=${documentId}`);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center gap-2">
        <Loader2 className="h-4 w-4 animate-spin" />
        <span className="text-sm text-muted-foreground">Loading documents...</span>
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <FileText className="h-4 w-4" />
        <span>No documents available</span>
      </div>
    );
  }

  return (
    <Select value={selectedDocumentId} onValueChange={handleValueChange}>
      <SelectTrigger className="w-[300px]">
        <SelectValue placeholder="Select a document" />
      </SelectTrigger>
      <SelectContent>
        {documents.map((document) => (
          <SelectItem key={document.id} value={document.id}>
            <div className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              <span>{document.name}</span>
            </div>
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}

