"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { MainLayout } from "@/components/layout/main-layout";
import { ClauseTable } from "@/components/clauses/clause-table";
import { DocumentSelector } from "@/components/documents/document-selector";
import { WorkspaceSelector } from "@/components/workspace/workspace-selector";
import { api, Document } from "@/lib/api";
import { Skeleton } from "@/components/ui/skeleton";
import { FileText, Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

function ClausesContent() {
  const searchParams = useSearchParams();
  const documentId = searchParams.get("documentId") || "";
  const [workspaceId, setWorkspaceId] = useState<string>("");
  const [document, setDocument] = useState<Document | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (documentId) {
      api
        .getDocument(documentId)
        .then((doc) => {
          setDocument(doc);
          setWorkspaceId(doc.workspace_id);
        })
        .catch(console.error)
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [documentId]);

  const handleDocumentSelect = (selectedDocumentId: string) => {
    window.location.href = `/clauses?documentId=${selectedDocumentId}`;
  };

  if (!documentId) {
    return (
      <MainLayout>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold">Clause Extraction</h1>
              <p className="text-muted-foreground">
                Select a document to view extracted clauses
              </p>
            </div>
            <WorkspaceSelector
              value={workspaceId}
              onValueChange={setWorkspaceId}
            />
          </div>
          
          {workspaceId ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <FileText className="h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-muted-foreground mb-4">
                Please select a document to view clauses
              </p>
              <DocumentSelector
                workspaceId={workspaceId}
                onDocumentSelect={handleDocumentSelect}
              />
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <FileText className="h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-muted-foreground">
                Please select a workspace first
              </p>
            </div>
          )}
        </div>
      </MainLayout>
    );
  }

  if (loading) {
    return (
      <MainLayout>
        <div className="space-y-4">
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-96 w-full" />
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Clause Extraction</h1>
            {document && (
              <p className="text-muted-foreground">
                Analyzing: {document.name}
              </p>
            )}
          </div>
          <div className="flex items-center gap-4">
            {workspaceId && (
              <DocumentSelector
                workspaceId={workspaceId}
                selectedDocumentId={documentId}
                onDocumentSelect={handleDocumentSelect}
              />
            )}
            <WorkspaceSelector
              value={workspaceId}
              onValueChange={setWorkspaceId}
            />
            {documentId && (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" size="sm">
                    <Download className="h-4 w-4 mr-2" />
                    Export
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem
                    onClick={async () => {
                      try {
                        const blob = await api.exportClauses(documentId, "json");
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement("a");
                        a.href = url;
                        a.download = `clauses-${document?.name || documentId}-${Date.now()}.json`;
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                        URL.revokeObjectURL(url);
                        toast.success("Clauses exported as JSON");
                      } catch (error: any) {
                        toast.error("Failed to export clauses", {
                          description: error.detail || "Please try again",
                        });
                      }
                    }}
                  >
                    Export as JSON
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    onClick={async () => {
                      try {
                        const blob = await api.exportClauses(documentId, "csv");
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement("a");
                        a.href = url;
                        a.download = `clauses-${document?.name || documentId}-${Date.now()}.csv`;
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                        URL.revokeObjectURL(url);
                        toast.success("Clauses exported as CSV");
                      } catch (error: any) {
                        toast.error("Failed to export clauses", {
                          description: error.detail || "Please try again",
                        });
                      }
                    }}
                  >
                    Export as CSV
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    onClick={async () => {
                      try {
                        const blob = await api.downloadReviewChecklist(documentId);
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement("a");
                        a.href = url;
                        a.download = `review-checklist-${document?.name || documentId}-${Date.now()}.pdf`;
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                        URL.revokeObjectURL(url);
                        toast.success("Review checklist downloaded");
                      } catch (error: any) {
                        toast.error("Failed to download review checklist", {
                          description: error.detail || "Please try again",
                        });
                      }
                    }}
                  >
                    Download Review Checklist (PDF)
                  </DropdownMenuItem>
                  {document?.file_type === "PDF" && (
                    <DropdownMenuItem
                      onClick={async () => {
                        try {
                          const blob = await api.downloadHighlightedContract(documentId);
                          const url = URL.createObjectURL(blob);
                          const a = document.createElement("a");
                          a.href = url;
                          a.download = `highlighted-${document?.name || documentId}-${Date.now()}.pdf`;
                          document.body.appendChild(a);
                          a.click();
                          document.body.removeChild(a);
                          URL.revokeObjectURL(url);
                          toast.success("Highlighted contract downloaded");
                        } catch (error: any) {
                          toast.error("Failed to download highlighted contract", {
                            description: error.detail || "Please try again",
                          });
                        }
                      }}
                    >
                      Download Highlighted Contract (PDF)
                    </DropdownMenuItem>
                  )}
                </DropdownMenuContent>
              </DropdownMenu>
            )}
          </div>
        </div>

        <ClauseTable documentId={documentId} />
      </div>
    </MainLayout>
  );
}

export default function ClausesPage() {
  return (
    <Suspense fallback={
      <MainLayout>
        <div className="space-y-4">
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-96 w-full" />
        </div>
      </MainLayout>
    }>
      <ClausesContent />
    </Suspense>
  );
}

