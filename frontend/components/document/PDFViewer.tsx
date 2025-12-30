"use client";

import { useState } from "react";
import { Document, Page, pdfjs } from "react-pdf";
import { ChevronLeft, ChevronRight, ZoomIn, ZoomOut } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import "react-pdf/dist/esm/Page/AnnotationLayer.css";
import "react-pdf/dist/esm/Page/TextLayer.css";

// Set up PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

interface PDFViewerProps {
  file: string | File | Blob;
  highlights?: Array<{
    page: number;
    coordinates?: {
      x: number;
      y: number;
      width: number;
      height: number;
    };
  }>;
  onPageChange?: (page: number) => void;
}

export function PDFViewer({ file, highlights = [], onPageChange }: PDFViewerProps) {
  const [numPages, setNumPages] = useState<number | null>(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [scale, setScale] = useState(1.0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  function onDocumentLoadSuccess({ numPages }: { numPages: number }) {
    setNumPages(numPages);
    setLoading(false);
    setError(null);
  }

  function onDocumentLoadError(error: Error) {
    setError(`Failed to load PDF: ${error.message}`);
    setLoading(false);
  }

  const goToPrevPage = () => {
    const newPage = Math.max(1, pageNumber - 1);
    setPageNumber(newPage);
    onPageChange?.(newPage);
  };

  const goToNextPage = () => {
    if (numPages) {
      const newPage = Math.min(numPages, pageNumber + 1);
      setPageNumber(newPage);
      onPageChange?.(newPage);
    }
  };

  const zoomIn = () => setScale((prev) => Math.min(3.0, prev + 0.2));
  const zoomOut = () => setScale((prev) => Math.max(0.5, prev - 0.2));

  if (error) {
    return (
      <div className="flex items-center justify-center h-full p-8 border rounded-lg bg-muted">
        <p className="text-destructive">{error}</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Toolbar */}
      <div className="flex items-center justify-between p-4 border-b bg-background">
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={goToPrevPage}
            disabled={pageNumber <= 1}
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <span className="text-sm">
            Page {pageNumber} of {numPages || "..."}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={goToNextPage}
            disabled={!numPages || pageNumber >= numPages}
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={zoomOut}>
            <ZoomOut className="h-4 w-4" />
          </Button>
          <span className="text-sm w-16 text-center">{Math.round(scale * 100)}%</span>
          <Button variant="outline" size="sm" onClick={zoomIn}>
            <ZoomIn className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* PDF Viewer */}
      <div className="flex-1 overflow-auto bg-gray-100 p-4 flex justify-center">
        {loading && (
          <div className="flex items-center justify-center h-full">
            <Skeleton className="w-[612px] h-[792px]" />
          </div>
        )}
        <Document
          file={file}
          onLoadSuccess={onDocumentLoadSuccess}
          onLoadError={onDocumentLoadError}
          loading={null}
          className="flex justify-center"
        >
          <div className="relative">
            <Page
              pageNumber={pageNumber}
              scale={scale}
              renderTextLayer={true}
              renderAnnotationLayer={true}
              className="shadow-lg"
            />
            {/* Highlight overlays */}
            {highlights
              .filter((h) => h.page === pageNumber)
              .map((highlight, idx) => {
                if (!highlight.coordinates) return null;
                const { x, y, width, height } = highlight.coordinates;
                return (
                  <div
                    key={idx}
                    className="absolute bg-yellow-400 bg-opacity-40 border-2 border-yellow-500"
                    style={{
                      left: `${x}px`,
                      top: `${y}px`,
                      width: `${width}px`,
                      height: `${height}px`,
                    }}
                  />
                );
              })}
          </div>
        </Document>
      </div>
    </div>
  );
}


