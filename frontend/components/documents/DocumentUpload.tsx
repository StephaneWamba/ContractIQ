"use client";

import { useState, useCallback } from "react";
import { useUploadDocument } from "@/lib/api/hooks";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Upload, X, FileText } from "lucide-react";
import { cn } from "@/lib/utils";
import { formatFileSize } from "@/lib/utils";

interface DocumentUploadProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  workspaceId: string;
}

export function DocumentUpload({
  open,
  onOpenChange,
  workspaceId,
}: DocumentUploadProps) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const uploadDocument = useUploadDocument();

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const file = e.dataTransfer.files?.[0];
    if (file && (file.type === "application/pdf" || file.name.endsWith(".docx"))) {
      setSelectedFile(file);
    }
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile || !workspaceId) return;

    try {
      await uploadDocument.mutateAsync({
        workspaceId,
        file: selectedFile,
      });
      setSelectedFile(null);
      onOpenChange(false);
    } catch (error) {
      console.error("Upload failed:", error);
    }
  };

  const handleClose = () => {
    setSelectedFile(null);
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Upload Document</DialogTitle>
          <DialogDescription>
            Upload a PDF or DOCX file to analyze. Maximum file size: 50MB
          </DialogDescription>
        </DialogHeader>

        <div
          className={cn(
            "relative mt-4 border-2 border-dashed rounded-lg p-8 text-center transition-colors",
            dragActive
              ? "border-primary bg-primary/5"
              : "border-muted-foreground/25",
            selectedFile && "border-primary bg-primary/5"
          )}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            type="file"
            id="file-upload"
            className="hidden"
            accept=".pdf,.docx"
            onChange={handleFileSelect}
          />

          {selectedFile ? (
            <div className="space-y-4">
              <div className="flex items-center justify-center gap-3">
                <FileText className="h-10 w-10 text-primary" />
                <div className="text-left">
                  <p className="font-medium">{selectedFile.name}</p>
                  <p className="text-sm text-muted-foreground">
                    {formatFileSize(selectedFile.size)}
                  </p>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setSelectedFile(null)}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <Upload className="h-12 w-12 mx-auto text-muted-foreground" />
              <div>
                <label htmlFor="file-upload">
                  <Button variant="outline" asChild>
                    <span>Choose file</span>
                  </Button>
                </label>
                <p className="mt-2 text-sm text-muted-foreground">
                  or drag and drop
                </p>
              </div>
              <p className="text-xs text-muted-foreground">
                PDF, DOCX up to 50MB
              </p>
            </div>
          )}
        </div>

        <div className="flex justify-end gap-2 mt-6">
          <Button variant="outline" onClick={handleClose}>
            Cancel
          </Button>
          <Button
            onClick={handleUpload}
            disabled={!selectedFile || uploadDocument.isPending}
          >
            {uploadDocument.isPending ? "Uploading..." : "Upload"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}


