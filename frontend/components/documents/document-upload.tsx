"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { api, Document } from "@/lib/api";
import { toast } from "sonner";
import { Upload, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface DocumentUploadProps {
  workspaceId: string;
  onUploadComplete?: (document: Document) => void;
}

export function DocumentUpload({
  workspaceId,
  onUploadComplete,
}: DocumentUploadProps) {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [dragActive, setDragActive] = useState(false);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      if (!workspaceId) {
        toast.error("Please select a workspace first");
        return;
      }

      const file = acceptedFiles[0];
      if (!file) return;

      // Validate file type
      const validTypes = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      ];
      if (!validTypes.includes(file.type)) {
        toast.error("Invalid file type", {
          description: "Please upload a PDF or DOCX file",
        });
        return;
      }

      // Validate file size (max 50MB)
      const maxSize = 50 * 1024 * 1024;
      if (file.size > maxSize) {
        toast.error("File too large", {
          description: "Maximum file size is 50MB",
        });
        return;
      }

      try {
        setUploading(true);
        setProgress(0);

        const document = await api.uploadDocument(
          workspaceId,
          file,
          (progress) => setProgress(progress)
        );

        toast.success("Document uploaded successfully", {
          description: `Processing ${file.name}...`,
        });

        onUploadComplete?.(document);
        setProgress(0);
      } catch (error: any) {
        toast.error("Upload failed", {
          description: error.detail || "Please try again",
        });
      } finally {
        setUploading(false);
        setProgress(0);
      }
    },
    [workspaceId, onUploadComplete]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [
        ".docx",
      ],
    },
    maxFiles: 1,
    disabled: uploading || !workspaceId,
  });

  return (
    <div
      {...getRootProps()}
      className={cn(
        "relative rounded-lg border-2 border-dashed transition-colors",
        isDragActive || dragActive
          ? "border-primary bg-primary/5"
          : "border-border hover:border-primary/50",
        uploading && "opacity-50 cursor-not-allowed"
      )}
      onDragEnter={() => setDragActive(true)}
      onDragLeave={() => setDragActive(false)}
    >
      <input {...getInputProps()} />
      <div className="flex flex-col items-center justify-center p-12 text-center">
        {uploading ? (
          <>
            <Loader2 className="h-12 w-12 animate-spin text-primary mb-4" />
            <p className="text-sm font-medium mb-2">Uploading...</p>
            <Progress value={progress} className="w-full max-w-xs" />
            <p className="text-xs text-muted-foreground mt-2">
              {Math.round(progress)}%
            </p>
          </>
        ) : (
          <>
            <div className="rounded-full bg-primary/10 p-4 mb-4">
              <Upload className="h-8 w-8 text-primary" />
            </div>
            <p className="text-sm font-medium mb-1">
              {isDragActive
                ? "Drop your file here"
                : "Drag & drop your contract here"}
            </p>
            <p className="text-xs text-muted-foreground mb-4">
              or click to browse
            </p>
            <p className="text-xs text-muted-foreground">
              PDF or DOCX up to 50MB
            </p>
          </>
        )}
      </div>
    </div>
  );
}

