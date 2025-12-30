"use client";

import { useState } from "react";
import { useDocument, useClauses } from "@/lib/api/hooks";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { FileText, Eye } from "lucide-react";
import { OverviewTab } from "./OverviewTab";
import { ClausesTab } from "./ClausesTab";
import { RisksTab } from "./RisksTab";
import { RiskSummaryPanel } from "./RiskSummaryPanel";
import { ExportButtons } from "./ExportButtons";
import { PDFViewerContainer } from "@/components/document/PDFViewerContainer";

interface DocumentReviewProps {
  documentId: string;
}

export function DocumentReview({ documentId }: DocumentReviewProps) {
  const [showPDFViewer, setShowPDFViewer] = useState(false);
  const { data: document, isLoading: documentLoading } = useDocument(documentId);
  const { data: clauses, isLoading: clausesLoading } = useClauses(documentId);

  if (documentLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }

  if (!document) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <p className="text-muted-foreground">Document not found</p>
        </CardContent>
      </Card>
    );
  }

  if (showPDFViewer) {
    return (
      <div className="h-[calc(100vh-12rem)] border rounded-lg">
        <PDFViewerContainer
          documentId={document.id}
          documentName={document.name}
          onClose={() => setShowPDFViewer(false)}
        />
      </div>
    );
  }

  return (
    <div className="flex gap-6">
      <div className="flex-1">
        <div className="mb-6 flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold">{document.name}</h1>
            <p className="text-muted-foreground mt-2">
              {document.page_count || 0} pages • Processed{" "}
              {new Date(document.updated_at).toLocaleDateString()}
            </p>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={() => setShowPDFViewer(true)}
            >
              <Eye className="h-4 w-4 mr-2" />
              View PDF
            </Button>
            <ExportButtons documentId={document.id} documentName={document.name} />
          </div>
        </div>

        <Tabs defaultValue="overview" className="w-full">
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="clauses">Clauses</TabsTrigger>
            <TabsTrigger value="risks">Risks</TabsTrigger>
          </TabsList>
          <TabsContent value="overview" className="mt-6">
            <OverviewTab document={document} clauses={clauses || []} />
          </TabsContent>
          <TabsContent value="clauses" className="mt-6">
            <ClausesTab
              clauses={clauses || []}
              isLoading={clausesLoading}
              documentId={documentId}
            />
          </TabsContent>
          <TabsContent value="risks" className="mt-6">
            <RisksTab clauses={clauses || []} isLoading={clausesLoading} />
          </TabsContent>
        </Tabs>
      </div>

      <div className="w-80">
        <div className="sticky top-24">
          <RiskSummaryPanel clauses={clauses || []} />
        </div>
      </div>
    </div>
  );
}

