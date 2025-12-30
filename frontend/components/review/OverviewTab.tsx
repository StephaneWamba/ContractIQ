"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Document, Clause } from "@/lib/types";
import { formatDate, formatFileSize } from "@/lib/utils";

interface OverviewTabProps {
  document: Document;
  clauses: Clause[];
}

export function OverviewTab({ document, clauses }: OverviewTabProps) {
  const clauseTypes = new Set(clauses.map((c) => c.clause_type));

  return (
    <div className="grid gap-6 md:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>Document Information</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <p className="text-sm text-muted-foreground">File Name</p>
            <p className="font-medium">{document.original_filename}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">File Size</p>
            <p className="font-medium">{formatFileSize(document.file_size)}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Pages</p>
            <p className="font-medium">{document.page_count || 0}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Uploaded</p>
            <p className="font-medium">{formatDate(document.created_at)}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Last Updated</p>
            <p className="font-medium">{formatDate(document.updated_at)}</p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Extraction Summary</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <p className="text-sm text-muted-foreground">Total Clauses</p>
            <p className="text-2xl font-bold">{clauses.length}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground mb-2">
              Clause Types Found
            </p>
            <div className="flex flex-wrap gap-2">
              {Array.from(clauseTypes).map((type) => (
                <span
                  key={type}
                  className="px-2 py-1 text-xs rounded-md bg-primary/10 text-primary font-medium"
                >
                  {type}
                </span>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}


