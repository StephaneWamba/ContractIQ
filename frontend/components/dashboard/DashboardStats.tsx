"use client";

import { useDocuments } from "@/lib/api/hooks";
import { useWorkspaceContext } from "@/components/context/WorkspaceContext";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { FileText, CheckCircle2, AlertTriangle, MessageSquare } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { useMemo } from "react";

export function DashboardStats() {
  const { workspaceId } = useWorkspaceContext();
  const { data: documents, isLoading } = useDocuments(workspaceId || "");

  const stats = useMemo(() => {
    if (!documents) return null;

    const total = documents.length;
    const processed = documents.filter((d) => d.status === "PROCESSED").length;
    const processing = documents.filter((d) => d.status === "PROCESSING").length;
    const failed = documents.filter((d) => d.status === "FAILED").length;

    return { total, processed, processing, failed };
  }, [documents]);

  if (isLoading || !stats) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <Card key={i}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-4 w-4" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-8 w-16" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total Documents</CardTitle>
          <FileText className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.total}</div>
          <p className="text-xs text-muted-foreground">All documents</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Processed</CardTitle>
          <CheckCircle2 className="h-4 w-4 text-green-600" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.processed}</div>
          <p className="text-xs text-muted-foreground">Ready for review</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Processing</CardTitle>
          <AlertTriangle className="h-4 w-4 text-yellow-600" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.processing}</div>
          <p className="text-xs text-muted-foreground">In progress</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Conversations</CardTitle>
          <MessageSquare className="h-4 w-4 text-blue-600" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">-</div>
          <p className="text-xs text-muted-foreground">Q&A sessions</p>
        </CardContent>
      </Card>
    </div>
  );
}

