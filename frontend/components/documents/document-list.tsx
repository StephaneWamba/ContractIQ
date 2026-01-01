"use client";

import { useState, useEffect, useCallback } from "react";
import { api, Document } from "@/lib/api";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { StatusBadge } from "@/components/ui/status-badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import { RefreshCw, Trash2, FileText } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { cn } from "@/lib/utils";

interface DocumentListProps {
  workspaceId?: string;
  onDocumentClick?: (document: Document) => void;
}

export function DocumentList({
  workspaceId,
  onDocumentClick,
}: DocumentListProps) {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [polling, setPolling] = useState(false);

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
      
      // Check if any documents are processing
      const hasProcessing = data.some(
        (doc) => doc.status === "processing" || doc.status === "pending"
      );
      setPolling(hasProcessing);
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

  // Poll for status updates if any documents are processing
  useEffect(() => {
    if (!polling) return;

    const interval = setInterval(() => {
      fetchDocuments();
    }, 3000); // Poll every 3 seconds

    return () => clearInterval(interval);
  }, [polling, fetchDocuments]);

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this document?")) return;

    try {
      await api.deleteDocument(id);
      setDocuments((prev) => prev.filter((doc) => doc.id !== id));
      toast.success("Document deleted");
    } catch (error: any) {
      toast.error("Failed to delete document", {
        description: error.detail || "Please try again",
      });
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + " " + sizes[i];
  };

  if (loading) {
    return (
      <div className="space-y-2">
        {[1, 2, 3].map((i) => (
          <Skeleton key={i} className="h-16 w-full" />
        ))}
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <FileText className="h-12 w-12 text-muted-foreground mb-4" />
        <p className="text-sm font-medium mb-1">No documents yet</p>
        <p className="text-xs text-muted-foreground">
          Upload a contract to get started
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Documents</h2>
        <Button
          variant="outline"
          size="sm"
          onClick={() => fetchDocuments()}
          disabled={loading}
        >
          <RefreshCw
            className={cn("h-4 w-4 mr-2", loading && "animate-spin")}
          />
          Refresh
        </Button>
      </div>

      <div className="rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Pages</TableHead>
              <TableHead>Size</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {documents.map((document) => (
              <TableRow
                key={document.id}
                className="cursor-pointer hover:bg-muted/50"
                onClick={() => onDocumentClick?.(document)}
              >
                <TableCell className="font-medium">
                  {document.name}
                </TableCell>
                <TableCell>
                  <span className="text-xs text-muted-foreground">
                    {document.file_type}
                  </span>
                </TableCell>
                <TableCell>
                  <StatusBadge status={document.status} />
                </TableCell>
                <TableCell>
                  {document.page_count || "-"}
                </TableCell>
                <TableCell className="text-xs text-muted-foreground">
                  {formatFileSize(document.file_size)}
                </TableCell>
                <TableCell className="text-right">
                  <div className="flex items-center justify-end gap-2">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(document.id);
                      }}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}

