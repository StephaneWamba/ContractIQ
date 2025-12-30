"use client";

import { useDocuments } from "@/lib/api/hooks";
import { useWorkspaceContext } from "@/components/context/WorkspaceContext";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { FileText, ArrowRight } from "lucide-react";
import Link from "next/link";
import { formatDate, getStatusColor, cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

export function RecentDocuments() {
  const { workspaceId } = useWorkspaceContext();
  const { data: documents, isLoading } = useDocuments(workspaceId || "");

  const recentDocuments = documents?.slice(0, 5) || [];

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Recent Documents</CardTitle>
            <CardDescription>Your recently uploaded contracts</CardDescription>
          </div>
          <Button variant="outline" asChild>
            <Link href="/documents">
              View All
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="flex items-center gap-4">
                <Skeleton className="h-10 w-10 rounded" />
                <div className="flex-1 space-y-2">
                  <Skeleton className="h-4 w-48" />
                  <Skeleton className="h-3 w-32" />
                </div>
                <Skeleton className="h-6 w-20" />
              </div>
            ))}
          </div>
        ) : recentDocuments.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>No documents yet</p>
            <Button variant="outline" className="mt-4" asChild>
              <Link href="/documents">Upload your first document</Link>
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            {recentDocuments.map((document) => (
              <Link
                key={document.id}
                href={`/review/${document.id}`}
                className="flex items-center gap-4 p-3 rounded-lg hover:bg-accent transition-colors"
              >
                <div className="flex-shrink-0">
                  <div className="h-10 w-10 rounded bg-primary/10 flex items-center justify-center">
                    <FileText className="h-5 w-5 text-primary" />
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium truncate">{document.name}</p>
                  <p className="text-sm text-muted-foreground">
                    {document.page_count || 0} pages • {formatDate(document.created_at)}
                  </p>
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
              </Link>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

