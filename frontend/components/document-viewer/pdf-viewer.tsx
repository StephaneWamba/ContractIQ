"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Download, FileText, ChevronLeft, ChevronRight } from "lucide-react";
import { Citation } from "@/lib/api";

interface PDFViewerProps {
  documentUrl: string;
  documentName: string;
  citation?: Citation;
  onPageChange?: (page: number) => void;
}

export function PDFViewer({
  documentUrl,
  documentName,
  citation,
  onPageChange,
}: PDFViewerProps) {
  const [pageNumber, setPageNumber] = useState<number>(1);
  const [error, setError] = useState<string | null>(null);
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  // Update page number when citation changes
  useEffect(() => {
    if (citation) {
      setPageNumber(citation.page_number);
      setError(null);
    }
  }, [citation]);

  const goToPrevPage = () => {
    setPageNumber((prev) => Math.max(1, prev - 1));
  };

  const goToNextPage = () => {
    setPageNumber((prev) => prev + 1);
  };

  const handlePageInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const page = parseInt(e.target.value);
    if (page >= 1) {
      setPageNumber(page);
    }
  };

  const handleDownload = () => {
    window.open(documentUrl, "_blank");
  };

  useEffect(() => {
    onPageChange?.(pageNumber);
  }, [pageNumber, onPageChange]);

  // Build iframe URL with page parameter
  const iframeUrl = `${documentUrl}#page=${pageNumber}`;

  if (!isClient) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center p-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mb-2"></div>
        <p className="text-muted-foreground">Loading PDF viewer...</p>
      </div>
    );
  }

  if (!documentUrl) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center p-12">
        <FileText className="h-12 w-12 text-muted-foreground mb-4" />
        <p className="text-muted-foreground">No document selected</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Toolbar */}
      <div className="flex items-center justify-between border-b p-2 bg-muted/50 flex-shrink-0">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium">{documentName}</span>
          <span className="text-xs text-muted-foreground">
            Page {pageNumber}
          </span>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={goToPrevPage}
            disabled={pageNumber <= 1}
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>

          <div className="flex items-center gap-1">
            <Input
              type="number"
              min={1}
              value={pageNumber}
              onChange={handlePageInput}
              className="w-16 h-8 text-center text-xs"
            />
          </div>

          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={goToNextPage}
          >
            <ChevronRight className="h-4 w-4" />
          </Button>

          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={handleDownload}
          >
            <Download className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* PDF Viewer - Using iframe */}
      <div className="flex-1 overflow-hidden bg-gray-100 min-h-0">
        {error ? (
          <div className="flex flex-col items-center justify-center h-full text-center p-12">
            <p className="text-sm font-medium text-destructive mb-2">Error loading PDF</p>
            <p className="text-xs text-muted-foreground mb-4">{error}</p>
            <a 
              href={documentUrl} 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-primary underline hover:no-underline text-sm"
            >
              Open in new tab
            </a>
          </div>
        ) : (
          <iframe
            src={iframeUrl}
            className="w-full h-full border-0"
            title={`PDF Viewer: ${documentName}`}
            onError={() => {
              setError("Failed to load PDF in iframe");
            }}
          />
        )}
      </div>

    </div>
  );
}
