"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { MainLayout } from "@/components/layout/main-layout";
import { WorkspaceSelector } from "@/components/workspace/workspace-selector";
import { DocumentUpload } from "@/components/documents/document-upload";
import { DocumentList } from "@/components/documents/document-list";
import { Document } from "@/lib/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { FolderOpen } from "lucide-react";

// Force dynamic rendering to avoid static generation issues with useSearchParams
export const dynamic = 'force-dynamic';

function DocumentsContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const initialWorkspaceId = searchParams.get("workspaceId") || "";
  
  const [workspaceId, setWorkspaceId] = useState<string>(initialWorkspaceId);
  const [refreshKey, setRefreshKey] = useState(0);

  // Update workspace ID when URL param changes
  useEffect(() => {
    const paramWorkspaceId = searchParams.get("workspaceId");
    if (paramWorkspaceId && paramWorkspaceId !== workspaceId) {
      setWorkspaceId(paramWorkspaceId);
    }
  }, [searchParams, workspaceId]);

  const handleWorkspaceChange = (newWorkspaceId: string) => {
    setWorkspaceId(newWorkspaceId);
    router.push(`/documents?workspaceId=${newWorkspaceId}`);
  };

  const handleUploadComplete = (document: Document) => {
    setRefreshKey((prev) => prev + 1);
  };

  const handleDocumentClick = (document: Document) => {
    router.push(`/clauses?documentId=${document.id}`);
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Documents</h1>
            <p className="text-muted-foreground">
              Manage and view your contract documents
            </p>
          </div>
          <div className="flex items-center gap-4">
            <WorkspaceSelector
              value={workspaceId}
              onValueChange={handleWorkspaceChange}
            />
            {workspaceId && (
              <Button
                variant="outline"
                onClick={() => router.push("/")}
              >
                <FolderOpen className="h-4 w-4 mr-2" />
                Manage Workspaces
              </Button>
            )}
          </div>
        </div>

        {workspaceId ? (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Upload Document</CardTitle>
                <CardDescription>
                  Upload a contract to analyze clauses and extract insights
                </CardDescription>
              </CardHeader>
              <CardContent>
                <DocumentUpload
                  workspaceId={workspaceId}
                  onUploadComplete={handleUploadComplete}
                />
              </CardContent>
            </Card>

            <DocumentList
              key={refreshKey}
              workspaceId={workspaceId}
              onDocumentClick={handleDocumentClick}
            />
          </div>
        ) : (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12 text-center">
              <FolderOpen className="h-12 w-12 text-muted-foreground mb-4 opacity-50" />
              <p className="text-sm font-medium mb-1">No workspace selected</p>
              <p className="text-xs text-muted-foreground mb-4">
                Select a workspace from the dropdown above, or create a new one
              </p>
              <Button onClick={() => router.push("/")}>
                <FolderOpen className="h-4 w-4 mr-2" />
                Go to Workspaces
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </MainLayout>
  );
}

export default function DocumentsPage() {
  return (
    <Suspense fallback={
      <MainLayout>
        <div className="flex items-center justify-center py-12">
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </MainLayout>
    }>
      <DocumentsContent />
    </Suspense>
  );
}

