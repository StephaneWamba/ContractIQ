"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Eye, AlertTriangle, AlertCircle, Info, CheckCircle2 } from "lucide-react";
import { ClauseDetailDialog } from "./ClauseDetailDialog";
import { useState, useMemo } from "react";
import { getRiskLevel, getRiskColor, truncate } from "@/lib/utils";
import type { Clause } from "@/lib/types";

interface RisksTabProps {
  clauses: Clause[];
  isLoading: boolean;
}

export function RisksTab({ clauses, isLoading }: RisksTabProps) {
  const [selectedClause, setSelectedClause] = useState<Clause | null>(null);

  const groupedRisks = useMemo(() => {
    const groups: Record<string, Clause[]> = {
      critical: [],
      high: [],
      medium: [],
      low: [],
    };

    clauses.forEach((clause) => {
      const riskLevel = getRiskLevel(clause.risk_flags) || "low";
      groups[riskLevel].push(clause);
    });

    return groups;
  }, [clauses]);

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <Card key={i}>
            <CardHeader>
              <Skeleton className="h-6 w-32" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-20 w-full" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  const riskSections = [
    {
      level: "critical" as const,
      label: "Critical Risks",
      icon: AlertTriangle,
      clauses: groupedRisks.critical,
    },
    {
      level: "high" as const,
      label: "High Risks",
      icon: AlertCircle,
      clauses: groupedRisks.high,
    },
    {
      level: "medium" as const,
      label: "Medium Risks",
      icon: Info,
      clauses: groupedRisks.medium,
    },
    {
      level: "low" as const,
      label: "Low Risks",
      icon: CheckCircle2,
      clauses: groupedRisks.low,
    },
  ];

  return (
    <div className="space-y-6">
      {riskSections.map((section) => (
        <Card key={section.level}>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <section.icon
                  className={`h-5 w-5 ${getRiskColor(section.level).split(" ")[0]}`}
                />
                <CardTitle>{section.label}</CardTitle>
                <Badge variant="outline">{section.clauses.length}</Badge>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {section.clauses.length === 0 ? (
              <p className="text-muted-foreground text-sm">
                No {section.label.toLowerCase()} found
              </p>
            ) : (
              <div className="space-y-3">
                {section.clauses.map((clause) => (
                  <div
                    key={clause.id}
                    className="flex items-start justify-between p-4 border rounded-lg hover:bg-accent transition-colors"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="font-medium text-sm">
                          {clause.clause_type}
                        </span>
                        <Badge
                          variant="outline"
                          className={getRiskColor(section.level)}
                        >
                          {section.level.toUpperCase()}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {truncate(clause.extracted_text, 150)}
                      </p>
                      <p className="text-xs text-muted-foreground mt-2">
                        Page {clause.page_number}
                        {clause.section && ` • ${clause.section}`}
                      </p>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setSelectedClause(clause)}
                    >
                      <Eye className="h-4 w-4 mr-2" />
                      View
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      ))}

      {selectedClause && (
        <ClauseDetailDialog
          clause={selectedClause}
          open={!!selectedClause}
          onOpenChange={(open) => !open && setSelectedClause(null)}
        />
      )}
    </div>
  );
}


