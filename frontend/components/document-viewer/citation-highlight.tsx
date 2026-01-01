"use client";

import { useEffect, useRef, useState } from "react";

interface CitationHighlightProps {
  coordinates: {
    x0: number;
    y0: number;
    x1: number;
    y1: number;
    page: number;
  };
  pageWidth: number;
}

export function CitationHighlight({
  coordinates,
  pageWidth,
}: CitationHighlightProps) {
  const highlightRef = useRef<HTMLDivElement>(null);
  const [position, setPosition] = useState<{
    left: number;
    top: number;
    width: number;
    height: number;
  } | null>(null);

  useEffect(() => {
    if (!highlightRef.current || !pageWidth || pageWidth === 0) {
      setPosition(null);
      return;
    }

    // Find the PDF page canvas element
    const pageElement = highlightRef.current.closest('.react-pdf__Page');
    if (!pageElement) {
      setPosition(null);
      return;
    }

    const canvas = pageElement.querySelector('canvas');
    if (!canvas) {
      setPosition(null);
      return;
    }

    const canvasRect = canvas.getBoundingClientRect();
    const canvasWidth = canvas.width;
    const canvasHeight = canvas.height;

    // PDF coordinates are in points (72 DPI)
    // Canvas dimensions are in pixels
    // Calculate scale factors
    const scaleX = canvasRect.width / canvasWidth;
    const scaleY = canvasRect.height / canvasHeight;

    // Convert PDF coordinates (points) to canvas coordinates (pixels)
    // Assuming standard PDF page size, we need to map coordinates
    // PyMuPDF coordinates are in points, canvas might be scaled
    const pdfPageWidth = 612; // Standard PDF width in points
    const pdfPageHeight = 792; // Standard PDF height in points

    // Calculate actual PDF page dimensions from canvas
    const pdfScaleX = canvasWidth / pdfPageWidth;
    const pdfScaleY = canvasHeight / pdfPageHeight;

    // Convert PDF coordinates to canvas pixel coordinates
    const x0 = coordinates.x0 * pdfScaleX;
    const y0 = coordinates.y0 * pdfScaleY;
    const x1 = coordinates.x1 * pdfScaleX;
    const y1 = coordinates.y1 * pdfScaleY;

    // Get canvas position relative to page element
    const pageRect = pageElement.getBoundingClientRect();
    const canvasRectRelative = canvas.getBoundingClientRect();
    const offsetX = canvasRectRelative.left - pageRect.left;
    const offsetY = canvasRectRelative.top - pageRect.top;

    // Position relative to page element
    setPosition({
      left: offsetX + (x0 * scaleX),
      top: offsetY + (y0 * scaleY),
      width: (x1 - x0) * scaleX,
      height: (y1 - y0) * scaleY,
    });
  }, [coordinates, pageWidth]);

  if (!coordinates || !position) return null;

  return (
    <div
      ref={highlightRef}
      className="absolute bg-yellow-400/40 border-2 border-yellow-500 rounded-sm pointer-events-none z-10"
      style={{
        left: `${position.left}px`,
        top: `${position.top}px`,
        width: `${position.width}px`,
        height: `${position.height}px`,
        mixBlendMode: "multiply",
      }}
      aria-label="Citation highlight"
    />
  );
}

