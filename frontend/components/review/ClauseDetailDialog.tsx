"use client";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { getRiskLevel, getRiskColor } from "@/lib/utils";
import type { Clause } from "@/lib/types";

interface ClauseDetailDialogProps {
  clause: Clause;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function ClauseDetailDialog({
  clause,
  open,
  onOpenChange,
}: ClauseDetailDialogProps) {
  const riskLevel = getRiskLevel(clause.risk_flags);
  const riskFlags = Array.isArray(clause.risk_flags)
    ? clause.risk_flags
    : clause.risk_flags
    ? [clause.risk_flags]
    : [];

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <DialogTitle>{clause.clause_type}</DialogTitle>
            {riskLevel && (
              <Badge variant="outline" className={getRiskColor(riskLevel)}>
                {riskLevel.toUpperCase()} RISK
              </Badge>
            )}
          </div>
        </DialogHeader>

        <div className="space-y-6 mt-4">
          <div>
            <p className="text-sm text-muted-foreground mb-1">Location</p>
            <p className="font-medium">
              Page {clause.page_number}
              {clause.section && ` • ${clause.section}`}
            </p>
          </div>

          {clause.confidence_score && (
            <div>
              <p className="text-sm text-muted-foreground mb-1">
                Confidence Score
              </p>
              <div className="flex items-center gap-2">
                <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary"
                    style={{ width: `${clause.confidence_score * 100}%` }}
                  />
                </div>
                <span className="text-sm font-medium">
                  {Math.round(clause.confidence_score * 100)}%
                </span>
              </div>
            </div>
          )}

          <div>
            <p className="text-sm text-muted-foreground mb-2">Extracted Text</p>
            <div className="p-4 bg-muted rounded-lg">
              <p className="text-sm whitespace-pre-wrap">
                {clause.extracted_text}
              </p>
            </div>
          </div>

          {riskFlags.length > 0 && (
            <div>
              <p className="text-sm text-muted-foreground mb-2">Risk Flags</p>
              <ul className="space-y-2">
                {riskFlags.map((flag, index) => (
                  <li
                    key={index}
                    className="flex items-start gap-2 text-sm p-2 bg-red-50 border border-red-200 rounded"
                  >
                    <span className="text-red-600 mt-0.5">⚠️</span>
                    <span>{flag}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="flex justify-end gap-2 pt-4 border-t">
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              Close
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}


