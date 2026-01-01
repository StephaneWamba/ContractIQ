"use client";

import { useState, useEffect } from "react";
import { api, Document } from "@/lib/api";
import { Button } from "@/components/ui/button";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Checkbox } from "@/components/ui/checkbox";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { FileText, X } from "lucide-react";
import { cn } from "@/lib/utils";

interface DocumentFilterProps {
  workspaceId: string;
  selectedDocumentIds: string[];
  onSelectionChange: (documentIds: string[]) => void;
}

export function DocumentFilter({
  workspaceId,
  selectedDocumentIds,
  onSelectionChange,
}: DocumentFilterProps) {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (!workspaceId) {
      setDocuments([]);
      setLoading(false);
      return;
    }

    const fetchDocuments = async () => {
      try {
        setLoading(true);
        const data = await api.getDocuments(workspaceId);
        setDocuments(data.filter((d) => d.status === "processed"));
      } catch (error) {
        console.error("Failed to load documents:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchDocuments();
  }, [workspaceId]);

  const handleToggle = (documentId: string) => {
    if (selectedDocumentIds.includes(documentId)) {
      onSelectionChange(selectedDocumentIds.filter((id) => id !== documentId));
    } else {
      onSelectionChange([...selectedDocumentIds, documentId]);
    }
  };

  const handleClearAll = () => {
    onSelectionChange([]);
  };

  const selectedDocuments = documents.filter((d) =>
    selectedDocumentIds.includes(d.id)
  );

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button variant="outline" size="sm" className="gap-2">
          <FileText className="h-4 w-4" />
          {selectedDocumentIds.length > 0
            ? `${selectedDocumentIds.length} document${selectedDocumentIds.length !== 1 ? "s" : ""}`
            : "All Documents"}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-80 p-0" align="start">
        <div className="p-4 border-b">
          <div className="flex items-center justify-between mb-2">
            <h4 className="font-semibold text-sm">Filter Documents</h4>
            {selectedDocumentIds.length > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleClearAll}
                className="h-6 text-xs"
              >
                Clear All
              </Button>
            )}
          </div>
          <p className="text-xs text-muted-foreground">
            Select documents to search. Leave empty to search all documents.
          </p>
        </div>

        {loading ? (
          <div className="p-4 text-center text-sm text-muted-foreground">
            Loading documents...
          </div>
        ) : documents.length === 0 ? (
          <div className="p-4 text-center text-sm text-muted-foreground">
            No processed documents found
          </div>
        ) : (
          <ScrollArea className="h-[300px]">
            <div className="p-2 space-y-1">
              {documents.map((document) => (
                <div
                  key={document.id}
                  className="flex items-center space-x-2 p-2 rounded hover:bg-accent cursor-pointer"
                  onClick={() => handleToggle(document.id)}
                >
                  <Checkbox
                    checked={selectedDocumentIds.includes(document.id)}
                    onCheckedChange={() => handleToggle(document.id)}
                  />
                  <label className="flex-1 text-sm cursor-pointer">
                    {document.name}
                  </label>
                </div>
              ))}
            </div>
          </ScrollArea>
        )}

        {selectedDocuments.length > 0 && (
          <div className="p-4 border-t">
            <div className="flex flex-wrap gap-2">
              {selectedDocuments.map((doc) => (
                <Badge
                  key={doc.id}
                  variant="secondary"
                  className="gap-1"
                >
                  {doc.name}
                  <button
                    onClick={() => handleToggle(doc.id)}
                    className="ml-1 hover:bg-secondary-foreground/20 rounded-full p-0.5"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </Badge>
              ))}
            </div>
          </div>
        )}
      </PopoverContent>
    </Popover>
  );
}

