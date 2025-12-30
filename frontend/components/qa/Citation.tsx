"use client";

import { Badge } from "@/components/ui/badge";
import { FileText } from "lucide-react";
import { cn, truncate } from "@/lib/utils";
import type { Citation as CitationType } from "@/lib/types";

interface CitationProps {
  citation: CitationType;
}

export function Citation({ citation }: CitationProps) {
  return (
    <div className="flex items-start gap-2 p-2 rounded-lg border bg-muted/50 hover:bg-muted transition-colors cursor-pointer">
      <FileText className="h-4 w-4 text-muted-foreground mt-0.5 flex-shrink-0" />
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <Badge variant="outline" className="text-xs">
            [{citation.index}]
          </Badge>
          <span className="font-medium text-sm truncate">
            {citation.document_name}
          </span>
        </div>
        <p className="text-xs text-muted-foreground">
          Page {citation.page} • {citation.section}
        </p>
        <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
          {truncate(citation.excerpt, 100)}
        </p>
      </div>
    </div>
  );
}


