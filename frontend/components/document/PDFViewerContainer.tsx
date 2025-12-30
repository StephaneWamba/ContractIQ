"use client";

import { useState } from "react";
import { PDFViewer } from "./PDFViewer";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { X } from "lucide-react";

interface PDFViewerContainerProps {
  documentId: string;
  documentName: string;
  onClose?: () => void;
  highlights?: Array<{
    page: number;
    coordinates?: {
      x: number;
      y: number;
      width: number;
      height: number;
    };
  }>;
}

export function PDFViewerContainer({
  documentId,
  documentName,
  onClose,
  highlights = [],
}: PDFViewerContainerProps) {
  const [activeTab, setActiveTab] = useState<"viewer" | "review">("viewer");
  const pdfUrl = `${process.env.NEXT_PUBLIC_API_URL}/documents/${documentId}/file`;

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between p-4 border-b">
        <div className="flex items-center gap-4">
          <h2 className="text-lg font-semibold">{documentName}</h2>
          <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as "viewer" | "review")}>
            <TabsList>
              <TabsTrigger value="viewer">PDF Viewer</TabsTrigger>
              <TabsTrigger value="review">Review</TabsTrigger>
            </TabsList>
          </Tabs>
        </div>
        {onClose && (
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        )}
      </div>
      <div className="flex-1 overflow-hidden">
        {activeTab === "viewer" && (
          <PDFViewer file={pdfUrl} highlights={highlights} />
        )}
        {activeTab === "review" && (
          <div className="h-full p-4">
            <p className="text-muted-foreground">
              Review interface will be shown here. You can switch between PDF viewer and review tabs.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}


