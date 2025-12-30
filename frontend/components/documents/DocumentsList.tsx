"use client";

import { useDocuments } from "@/lib/api/hooks";
import { useWorkspaceContext } from "@/components/context/WorkspaceContext";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { FileText, Upload, Search } from "lucide-react";
import Link from "next/link";
import { formatDate, getStatusColor, cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Input } from "@/components/ui/input";
import { useState } from "react";
import { DocumentUpload } from "./DocumentUpload";

export function DocumentsList() {
  const { workspaceId } = useWorkspaceContext();
  const { data: documents, isLoading } = useDocuments(workspaceId || "");
  const [searchQuery, setSearchQuery] = useState("");
  const [isUploadOpen, setIsUploadOpen] = useState(false);

  const filteredDocuments = documents?.filter((doc) =>
    doc.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <Card key={i}>
            <CardContent className="p-6">
              <div className="flex items-center gap-4">
                <Skeleton className="h-12 w-12 rounded" />
                <div className="flex-1 space-y-2">
                  <Skeleton className="h-5 w-64" />
                  <Skeleton className="h-4 w-48" />
                </div>
                <Skeleton className="h-6 w-24" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search documents..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
        <Button onClick={() => setIsUploadOpen(true)}>
          <Upload className="h-4 w-4 mr-2" />
          Upload Document
        </Button>
      </div>

      {filteredDocuments?.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <FileText className="h-16 w-16 text-muted-foreground mb-4 opacity-50" />
            <h3 className="text-lg font-semibold mb-2">No documents found</h3>
            <p className="text-muted-foreground mb-4">
              {searchQuery
                ? "Try a different search query"
                : "Upload your first document to get started"}
            </p>
            {!searchQuery && (
              <Button onClick={() => setIsUploadOpen(true)}>
                <Upload className="h-4 w-4 mr-2" />
                Upload Document
              </Button>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {filteredDocuments?.map((document) => (
              <Card key={document.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-6">
                <Link href={`/review/${document.id}`}>
                  <div className="flex items-center gap-4">
                    <div className="flex-shrink-0">
                      <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center">
                        <FileText className="h-6 w-6 text-primary" />
                      </div>
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-lg truncate">
                        {document.name}
                      </h3>
                      <div className="flex items-center gap-4 mt-1 text-sm text-muted-foreground">
                        <span>{document.page_count || 0} pages</span>
                        <span>•</span>
                        <span>{formatDate(document.created_at)}</span>
                      </div>
                    </div>
                    <Badge
                      variant="outline"
                      className={cn(
                        "flex-shrink-0",
                        getStatusColor(document.status)
                      )}
                    >
                      {document.status}
                    </Badge>
                  </div>
                </Link>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <DocumentUpload
        open={isUploadOpen}
        onOpenChange={setIsUploadOpen}
        workspaceId={workspaceId || ""}
      />
    </div>
  );
}

