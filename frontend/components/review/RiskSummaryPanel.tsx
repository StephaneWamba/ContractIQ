"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { AlertTriangle, AlertCircle, AlertCircleIcon as Info, CheckCircle2 } from "lucide-react";
import { useMemo } from "react";
import type { Clause } from "@/lib/types";

interface RiskSummaryPanelProps {
  clauses: Clause[];
}

export function RiskSummaryPanel({ clauses }: RiskSummaryPanelProps) {
  const riskSummary = useMemo(() => {
    let critical = 0;
    let high = 0;
    let medium = 0;
    let low = 0;

    clauses.forEach((clause) => {
      const riskFlags = clause.risk_flags;
      if (!riskFlags || riskFlags.length === 0) {
        low++;
        return;
      }

      const flagsStr = Array.isArray(riskFlags) ? riskFlags.join(" ") : riskFlags;
      const flagsLower = flagsStr.toLowerCase();

      if (flagsLower.includes("critical")) {
        critical++;
      } else if (flagsLower.includes("high")) {
        high++;
      } else if (flagsLower.includes("medium")) {
        medium++;
      } else {
        low++;
      }
    });

    return { critical, high, medium, low };
  }, [clauses]);

  const total = clauses.length;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Risk Summary</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-3">
          <RiskItem
            label="Critical"
            count={riskSummary.critical}
            total={total}
            icon={AlertTriangle}
            color="text-red-600 bg-red-50 border-red-200"
          />
          <RiskItem
            label="High"
            count={riskSummary.high}
            total={total}
            icon={AlertCircle}
            color="text-orange-600 bg-orange-50 border-orange-200"
          />
          <RiskItem
            label="Medium"
            count={riskSummary.medium}
            total={total}
            icon={Info}
            color="text-yellow-600 bg-yellow-50 border-yellow-200"
          />
          <RiskItem
            label="Low"
            count={riskSummary.low}
            total={total}
            icon={CheckCircle2}
            color="text-green-600 bg-green-50 border-green-200"
          />
        </div>
        <div className="pt-4 border-t">
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium">Total Clauses</span>
            <span className="text-lg font-bold">{total}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function RiskItem({
  label,
  count,
  total,
  icon: Icon,
  color,
}: {
  label: string;
  count: number;
  total: number;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
}) {
  const percentage = total > 0 ? Math.round((count / total) * 100) : 0;

  return (
    <div className="flex items-center justify-between p-2 rounded-lg border">
      <div className="flex items-center gap-3">
        <Icon className={`h-5 w-5 ${color.split(" ")[0]}`} />
        <span className="text-sm font-medium">{label}</span>
      </div>
      <div className="flex items-center gap-2">
        <span className="text-sm font-bold">{count}</span>
        {count > 0 && (
          <span className="text-xs text-muted-foreground">({percentage}%)</span>
        )}
      </div>
    </div>
  );
}


