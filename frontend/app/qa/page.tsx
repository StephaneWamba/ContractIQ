"use client";

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import dynamic from "next/dynamic";
import { MainLayout } from "@/components/layout/main-layout";
import { WorkspaceSelector } from "@/components/workspace/workspace-selector";
import { ChatInterface } from "@/components/qa/chat-interface";
import { ConversationSidebar } from "@/components/qa/conversation-sidebar";
import { DocumentFilter } from "@/components/qa/document-filter";
import { api, Document, Citation } from "@/lib/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import { Suspense } from "react";

// Dynamically import PDF viewer to avoid SSR issues with pdfjs-dist
const PDFViewer = dynamic(
  () => import("@/components/document-viewer/pdf-viewer").then((mod) => ({ default: mod.PDFViewer })),
  {
    ssr: false,
    loading: () => (
      <div className="flex flex-col items-center justify-center h-full text-center p-12">
        <Skeleton className="h-12 w-12 rounded-full mb-4" />
        <Skeleton className="h-4 w-48 mb-2" />
        <Skeleton className="h-4 w-32" />
      </div>
    ),
  }
);

function QAContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialConversationId = searchParams.get("conversationId") || undefined;
  
  const [workspaceId, setWorkspaceId] = useState<string>("");
  const [conversationId, setConversationId] = useState<string | undefined>(initialConversationId);
  const [selectedCitation, setSelectedCitation] = useState<Citation | null>(null);
  const [document, setDocument] = useState<Document | null>(null);
  const [documentUrl, setDocumentUrl] = useState<string>("");
  const [selectedDocumentIds, setSelectedDocumentIds] = useState<string[]>([]);
  const [blobUrl, setBlobUrl] = useState<string | null>(null);

  useEffect(() => {
    if (selectedCitation) {
      // Load document for citation
      loadDocumentForCitation(selectedCitation.document_id);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedCitation]);

  // Cleanup blob URLs on unmount or when document changes
  useEffect(() => {
    return () => {
      if (blobUrl) {
        URL.revokeObjectURL(blobUrl);
      }
    };
  }, [blobUrl]);

  const loadDocumentForCitation = async (documentId: string) => {
    try {
      // Cleanup previous blob URL
      if (blobUrl) {
        URL.revokeObjectURL(blobUrl);
        setBlobUrl(null);
      }

      const doc = await api.getDocument(documentId);
      setDocument(doc);
      // Fetch PDF as blob to create blob URL (prevents download, works better with iframe)
      try {
        const blob = await api.getDocumentFile(documentId);
        const newBlobUrl = URL.createObjectURL(blob);
        setBlobUrl(newBlobUrl);
        setDocumentUrl(newBlobUrl);
      } catch (blobError) {
        // Fallback to direct URL if blob fetch fails
        console.warn("Blob fetch failed, using direct URL:", blobError);
        const url = api.getDocumentFileUrl(documentId);
        setDocumentUrl(url);
      }
    } catch (error: any) {
      console.error("Failed to load document:", error);
      toast.error("Failed to load document", {
        description: error.detail || "Please try again",
      });
    }
  };

  const handleCitationClick = (citation: Citation) => {
    setSelectedCitation(citation);
  };

  const handleConversationSelect = (id: string) => {
    setConversationId(id);
    router.push(`/qa?conversationId=${id}`);
  };

  const handleNewConversation = () => {
    setConversationId(undefined);
    router.push("/qa");
  };

  return (
    <MainLayout>
      <div className="space-y-6 h-[calc(100vh-8rem)]">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Q&A</h1>
            <p className="text-muted-foreground">
              Ask questions about your contracts using AI
            </p>
          </div>
          <WorkspaceSelector
            value={workspaceId}
            onValueChange={setWorkspaceId}
          />
        </div>

        {workspaceId ? (
          <div className="flex h-[calc(100vh-12rem)] gap-4">
            {/* Conversation History Sidebar (like old sidebar, fully collapsible) */}
            <ConversationSidebar
              workspaceId={workspaceId}
              selectedConversationId={conversationId}
              onConversationSelect={handleConversationSelect}
              onNewConversation={handleNewConversation}
            />
            
            {/* Main Content Area */}
            <div className="flex-1 grid grid-cols-2 gap-4 min-w-0">

            {/* Chat Interface */}
            <Card className="flex flex-col h-full overflow-hidden">
              <CardHeader className="flex-shrink-0">
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Chat</CardTitle>
                    <CardDescription>
                      Ask questions about your contracts
                    </CardDescription>
                  </div>
                  <DocumentFilter
                    workspaceId={workspaceId}
                    selectedDocumentIds={selectedDocumentIds}
                    onSelectionChange={setSelectedDocumentIds}
                  />
                </div>
              </CardHeader>
              <CardContent className="flex-1 overflow-hidden flex flex-col min-h-0">
                <ChatInterface
                  workspaceId={workspaceId}
                  conversationId={conversationId}
                  onCitationClick={handleCitationClick}
                  selectedDocumentIds={selectedDocumentIds.length > 0 ? selectedDocumentIds : undefined}
                  onConversationCreated={(id) => {
                    setConversationId(id);
                    router.push(`/qa?conversationId=${id}`);
                  }}
                  onMessageAdded={() => {
                    // Trigger sidebar refresh when new message is added
                    // This will be handled by the sidebar's useEffect
                  }}
                />
              </CardContent>
            </Card>

            {/* Document Viewer */}
            <Card className="flex flex-col h-full overflow-hidden">
              <CardHeader className="flex-shrink-0">
                <CardTitle>Document Viewer</CardTitle>
                <CardDescription>
                  View documents and citations
                </CardDescription>
              </CardHeader>
              <CardContent className="flex-1 overflow-hidden flex flex-col min-h-0">
                {document ? (
                  <div className="h-full w-full">
                    <PDFViewer
                      documentUrl={documentUrl}
                      documentName={document.name}
                      citation={selectedCitation || undefined}
                    />
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center h-full text-center p-12">
                    <p className="text-muted-foreground">
                      Click on a citation to view the document
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
            </div>
          </div>
        ) : (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <p className="text-muted-foreground text-center">
                Please select or create a workspace to start asking questions
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </MainLayout>
  );
}

export default function QAPage() {
  return (
    <Suspense
      fallback={
        <MainLayout>
          <div className="space-y-4">
            <Skeleton className="h-8 w-64" />
            <Skeleton className="h-96 w-full" />
          </div>
        </MainLayout>
      }
    >
      <QAContent />
    </Suspense>
  );
}
