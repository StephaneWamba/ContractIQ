"use client";

import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface RiskBadgeProps {
  riskScore?: number;
  riskFlags?: string[];
  className?: string;
}

export function RiskBadge({ riskScore, riskFlags, className }: RiskBadgeProps) {
  if (!riskScore && (!riskFlags || riskFlags.length === 0)) {
    return null;
  }

  const score = riskScore || 0;

  let variant: "default" | "secondary" | "destructive" | "outline" = "default";
  let label = "Low";
  let bgColor = "";

  // Risk classification based ONLY on score (LLM-determined, not heuristics)
  if (score >= 75) {
    variant = "destructive";
    label = "Critical";
    bgColor = "bg-[var(--risk-critical)] text-white";
  } else if (score >= 50) {
    variant = "destructive";
    label = "High";
    bgColor = "bg-[var(--risk-high)] text-white";
  } else if (score >= 25) {
    variant = "secondary";
    label = "Medium";
    bgColor = "bg-[var(--risk-medium)] text-white";
  } else {
    variant = "default";
    label = "Low";
    bgColor = "bg-[var(--risk-low)] text-white";
  }

  return (
    <Badge
      variant={variant}
      className={cn(
        "font-semibold",
        bgColor,
        className
      )}
    >
      {label}
      {score > 0 && (
        <span className="ml-1 opacity-90">({Math.round(score)})</span>
      )}
    </Badge>
  );
}

