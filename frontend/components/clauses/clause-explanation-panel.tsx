"use client";

import { Clause } from "@/lib/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { RiskBadge } from "@/components/ui/risk-badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { X, AlertTriangle, Info, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface ClauseExplanationPanelProps {
  clause: Clause | null;
  onClose: () => void;
}

const RISK_FLAG_DESCRIPTIONS: Record<string, string> = {
  unfavorable_termination: "One-sided termination rights that favor the other party",
  high_liability: "Unlimited or very high liability caps that expose you to significant financial risk",
  unfair_payment_terms: "Penalties, late fees, or unfavorable payment terms",
  weak_indemnification: "Limited indemnification protection that may not cover all scenarios",
  ip_risk: "Unfavorable intellectual property ownership or licensing terms",
  compliance_risk: "Missing required compliance clauses or weak compliance provisions",
  data_privacy_risk: "Weak data protection provisions that may violate regulations",
  excessive_penalties: "Excessive penalties or liquidated damages",
  one_sided_terms: "Terms that heavily favor one party over the other",
  unclear_language: "Ambiguous or unclear language that could lead to disputes",
  missing_protections: "Missing standard protections that are typically included in contracts",
};

export function ClauseExplanationPanel({
  clause,
  onClose,
}: ClauseExplanationPanelProps) {
  if (!clause) return null;

  const riskLevel =
    clause.risk_score >= 75
      ? "critical"
      : clause.risk_score >= 50
      ? "high"
      : clause.risk_score >= 25
      ? "medium"
      : "low";

  return (
    <Card className="h-full flex flex-col overflow-hidden">
      <CardHeader className="flex-shrink-0 border-b">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="flex items-center gap-2">
              <Info className="h-5 w-5 text-primary" />
              Risk Explanation
            </CardTitle>
            <CardDescription className="mt-1">
              Detailed analysis of clause risk factors
            </CardDescription>
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={onClose}
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>

      <CardContent className="flex-1 overflow-hidden flex flex-col p-0 min-h-0">
        <ScrollArea className="h-full w-full">
          <div className="p-6 space-y-6">
            {/* Clause Overview */}
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-semibold">Clause Overview</h3>
                <Badge variant="outline">{clause.clause_type}</Badge>
                {clause.clause_subtype && (
                  <Badge variant="secondary" className="text-xs">
                    {clause.clause_subtype}
                  </Badge>
                )}
              </div>
              <div className="text-sm text-muted-foreground">
                <p>
                  <span className="font-medium">Page:</span> {clause.page_number}
                </p>
                {clause.section && (
                  <p>
                    <span className="font-medium">Section:</span> {clause.section}
                  </p>
                )}
                {clause.confidence_score !== undefined && (
                  <p>
                    <span className="font-medium">Confidence:</span>{" "}
                    {Math.round(clause.confidence_score * 100)}%
                  </p>
                )}
              </div>
            </div>

            {/* Risk Score */}
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-destructive" />
                <h3 className="text-sm font-semibold">Risk Assessment</h3>
              </div>
              <div className="space-y-2">
                <div className="flex items-center gap-3">
                  <span className="text-sm font-medium">Risk Score:</span>
                  <RiskBadge
                    riskScore={clause.risk_score}
                    riskFlags={clause.risk_flags}
                  />
                </div>
                <div className="text-sm text-muted-foreground">
                  <p>
                    This clause has a{" "}
                    <span
                      className={cn(
                        "font-medium",
                        riskLevel === "critical" && "text-destructive",
                        riskLevel === "high" && "text-orange-600",
                        riskLevel === "medium" && "text-yellow-600",
                        riskLevel === "low" && "text-green-600"
                      )}
                    >
                      {riskLevel}
                    </span>{" "}
                    risk level (score: {clause.risk_score}/100).
                  </p>
                </div>
              </div>
            </div>

            {/* Risk Reasoning */}
            <div className="space-y-3">
              <h3 className="text-sm font-semibold">Risk Explanation</h3>
              <div className="rounded-lg bg-muted border overflow-hidden">
                {clause.risk_reasoning && clause.risk_reasoning.trim() ? (
                  <ScrollArea className="h-[200px]">
                    <div className="p-4">
                      <p className="text-sm whitespace-pre-wrap leading-relaxed">
                        {clause.risk_reasoning}
                      </p>
                    </div>
                  </ScrollArea>
                ) : (
                  <div className="h-[200px] p-4 flex items-center justify-center">
                    <p className="text-sm text-muted-foreground italic">
                      No detailed explanation available. The risk score is based on the identified risk flags and clause characteristics.
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Risk Flags */}
            {clause.risk_flags && clause.risk_flags.length > 0 && (
              <div className="space-y-3">
                <h3 className="text-sm font-semibold">Risk Flags</h3>
                <div className="space-y-2">
                  {clause.risk_flags.map((flag, index) => (
                    <div
                      key={index}
                      className="rounded-lg border border-destructive/20 bg-destructive/5 p-3"
                    >
                      <div className="flex items-start gap-2">
                        <AlertTriangle className="h-4 w-4 text-destructive mt-0.5 flex-shrink-0" />
                        <div className="flex-1">
                          <p className="text-sm font-medium capitalize">
                            {flag.replace(/_/g, " ")}
                          </p>
                          {RISK_FLAG_DESCRIPTIONS[flag] && (
                            <p className="text-xs text-muted-foreground mt-1">
                              {RISK_FLAG_DESCRIPTIONS[flag]}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Full Clause Text */}
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-muted-foreground" />
                <h3 className="text-sm font-semibold">Full Clause Text</h3>
              </div>
              <div className="rounded-lg border bg-muted/30 overflow-hidden">
                {clause.extracted_text && clause.extracted_text.trim() ? (
                  <ScrollArea className="h-[200px]">
                    <div className="p-4">
                      <p className="text-sm whitespace-pre-wrap leading-relaxed">
                        {clause.extracted_text}
                      </p>
                    </div>
                  </ScrollArea>
                ) : (
                  <div className="h-[200px] p-4 flex items-center justify-center">
                    <p className="text-sm text-muted-foreground italic">
                      Clause text not available
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Recommendations */}
            {clause.risk_score >= 50 && (
              <div className="space-y-3">
                <h3 className="text-sm font-semibold">Recommendations</h3>
                <div className="rounded-lg bg-blue-50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-800 p-4">
                  <ul className="text-sm space-y-2 list-disc list-inside">
                    {clause.risk_score >= 75 && (
                      <li>
                        <strong>Critical:</strong> Review this clause carefully and
                        consider negotiating more favorable terms.
                      </li>
                    )}
                    {clause.risk_flags?.includes("unfavorable_termination") && (
                      <li>
                        Consider requesting mutual termination rights or longer notice
                        periods.
                      </li>
                    )}
                    {clause.risk_flags?.includes("high_liability") && (
                      <li>
                        Negotiate for liability caps or exclusions for certain types
                        of damages.
                      </li>
                    )}
                    {clause.risk_flags?.includes("unfair_payment_terms") && (
                      <li>
                        Request more reasonable payment terms or penalty structures.
                      </li>
                    )}
                    {clause.risk_flags?.includes("weak_indemnification") && (
                      <li>
                        Strengthen indemnification provisions to better protect your
                        interests.
                      </li>
                    )}
                    {clause.risk_flags?.includes("unclear_language") && (
                      <li>
                        Request clarification or rewording to reduce ambiguity and
                        potential disputes.
                      </li>
                    )}
                    {!clause.risk_flags ||
                      (clause.risk_flags.length === 0 && (
                        <li>
                          While this clause has a moderate risk score, review it to
                          ensure it aligns with your business needs.
                        </li>
                      ))}
                  </ul>
                </div>
              </div>
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}

