"use client";

import { Button } from "@/components/ui/button";
import { Download, FileText, Table } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface ExportButtonsProps {
  documentId: string;
  documentName: string;
}

export function ExportButtons({ documentId, documentName }: ExportButtonsProps) {
  const handleExportPDF = () => {
    const url = `${process.env.NEXT_PUBLIC_API_URL}/documents/${documentId}/export/pdf?include_risks=true`;
    window.open(url, "_blank");
  };

  const handleExportCSV = () => {
    const url = `${process.env.NEXT_PUBLIC_API_URL}/documents/${documentId}/export/csv`;
    const link = document.createElement("a");
    link.href = url;
    link.download = `${documentName}_clauses.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline">
          <Download className="h-4 w-4 mr-2" />
          Export
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={handleExportPDF}>
          <FileText className="h-4 w-4 mr-2" />
          Export as PDF Report
        </DropdownMenuItem>
        <DropdownMenuItem onClick={handleExportCSV}>
          <Table className="h-4 w-4 mr-2" />
          Export Clauses as CSV
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

