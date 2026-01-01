"use client";

import { useState, useEffect, useCallback, useMemo } from "react";
import { api, Clause } from "@/lib/api";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { RiskBadge } from "@/components/ui/risk-badge";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";
import { RefreshCw, AlertTriangle, CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ClauseExplanationPanel } from "./clause-explanation-panel";

interface ClauseTableProps {
  documentId: string;
}

export function ClauseTable({ documentId }: ClauseTableProps) {
  const [clauses, setClauses] = useState<Clause[]>([]);
  const [loading, setLoading] = useState(true);
  const [extracting, setExtracting] = useState(false);
  const [selectedClause, setSelectedClause] = useState<Clause | null>(null);
  const [hasAutoExtracted, setHasAutoExtracted] = useState(false);
  const [filters, setFilters] = useState({
    clauseType: "all",
    minRiskScore: "",
    hasRiskFlags: false,
  });

  const fetchClauses = useCallback(async () => {
    if (!documentId) return;

    try {
      setLoading(true);
      const data = await api.getClauses(documentId, {
        clause_type: filters.clauseType && filters.clauseType !== "all" ? filters.clauseType : undefined,
        min_risk_score: filters.minRiskScore
          ? Number(filters.minRiskScore)
          : undefined,
        has_risk_flags: filters.hasRiskFlags || undefined,
      });
      // Ensure data is always an array
      setClauses(Array.isArray(data) ? data : []);
    } catch (error: any) {
      toast.error("Failed to load clauses", {
        description: error.detail || "Please try again",
      });
    } finally {
      setLoading(false);
    }
  }, [documentId, filters]);

  useEffect(() => {
    fetchClauses();
  }, [fetchClauses]);

  const handleExtract = useCallback(async () => {
    try {
      setExtracting(true);
      const result = await api.extractClauses(documentId, false);
      const extractedClauses = Array.isArray(result.clauses) ? result.clauses : [];
      setClauses(extractedClauses);
      toast.success("Clauses extracted successfully", {
        description: `Found ${extractedClauses.length} clauses`,
      });
    } catch (error: any) {
      toast.error("Failed to extract clauses", {
        description: error.detail || "Please try again",
      });
    } finally {
      setExtracting(false);
    }
  }, [documentId]);

  // Auto-extract clauses when document is selected and no clauses exist
  useEffect(() => {
    if (documentId && !loading && clauses.length === 0 && !extracting && !hasAutoExtracted) {
      // Auto-extract clauses when document is first selected
      setHasAutoExtracted(true);
      handleExtract();
    }
  }, [documentId, loading, clauses.length, extracting, hasAutoExtracted, handleExtract]);

  // Reset auto-extract flag when document changes
  useEffect(() => {
    setHasAutoExtracted(false);
  }, [documentId]);

  const riskStats = useMemo(() => {
    // Ensure clauses is always an array
    const clausesArray = Array.isArray(clauses) ? clauses : [];
    const total = clausesArray.length;
    
    // Count clauses with risk flags (non-empty array)
    const withRisk = clausesArray.filter(
      (c) => c.risk_flags && Array.isArray(c.risk_flags) && c.risk_flags.length > 0
    ).length;
    
    // High risk: score >= 50 and < 75
    const highRisk = clausesArray.filter((c) => {
      const score = c.risk_score || 0;
      return score >= 50 && score < 75;
    }).length;
    
    // Critical risk: score >= 75
    const criticalRisk = clausesArray.filter((c) => {
      const score = c.risk_score || 0;
      return score >= 75;
    }).length;

    return { total, withRisk, highRisk, criticalRisk };
  }, [clauses]);

  if (loading) {
    return (
      <div className="space-y-2">
        {[1, 2, 3, 4, 5].map((i) => (
          <Skeleton key={i} className="h-20 w-full" />
        ))}
      </div>
    );
  }

  // Ensure clauses is always an array
  const clausesArray = Array.isArray(clauses) ? clauses : [];
  
  // Show loading state while extracting
  if (extracting) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <RefreshCw className="h-12 w-12 text-primary mb-4 animate-spin" />
        <p className="text-sm font-medium mb-1">Extracting clauses...</p>
        <p className="text-xs text-muted-foreground">
          This may take a moment
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">Extracted Clauses</h2>
          <p className="text-sm text-muted-foreground">
            {clausesArray.length} clause{clausesArray.length !== 1 ? "s" : ""} found
          </p>
        </div>
        <Button onClick={handleExtract} disabled={extracting}>
          {extracting && <RefreshCw className="mr-2 h-4 w-4 animate-spin" />}
          {clausesArray.length > 0 ? "Re-extract" : "Extract Clauses"}
        </Button>
      </div>

      {/* Risk Summary */}
      {riskStats.total > 0 && (
        <div className="grid grid-cols-4 gap-4">
          <div className="rounded-lg border p-4">
            <div className="text-2xl font-bold">{riskStats.total}</div>
            <div className="text-xs text-muted-foreground">Total Clauses</div>
          </div>
          <div className="rounded-lg border p-4">
            <div className="text-2xl font-bold text-[var(--risk-medium)]">
              {riskStats.withRisk}
            </div>
            <div className="text-xs text-muted-foreground">With Risk Flags</div>
          </div>
          <div className="rounded-lg border p-4">
            <div className="text-2xl font-bold text-[var(--risk-high)]">
              {riskStats.highRisk}
            </div>
            <div className="text-xs text-muted-foreground">High Risk</div>
          </div>
          <div className="rounded-lg border p-4">
            <div className="text-2xl font-bold text-[var(--risk-critical)]">
              {riskStats.criticalRisk}
            </div>
            <div className="text-xs text-muted-foreground">Critical Risk</div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="flex items-center gap-4">
        <Select
          value={filters.clauseType}
          onValueChange={(value) =>
            setFilters((prev) => ({ ...prev, clauseType: value }))
          }
        >
          <SelectTrigger className="w-[200px]">
            <SelectValue placeholder="All Clause Types" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            <SelectItem value="Termination">Termination</SelectItem>
            <SelectItem value="Payment">Payment</SelectItem>
            <SelectItem value="Liability">Liability</SelectItem>
            <SelectItem value="Indemnification">Indemnification</SelectItem>
            <SelectItem value="Intellectual Property">Intellectual Property</SelectItem>
            <SelectItem value="Confidentiality">Confidentiality</SelectItem>
            <SelectItem value="Dispute Resolution">Dispute Resolution</SelectItem>
          </SelectContent>
        </Select>

        <Input
          type="number"
          placeholder="Min Risk Score"
          value={filters.minRiskScore}
          onChange={(e) =>
            setFilters((prev) => ({ ...prev, minRiskScore: e.target.value }))
          }
          className="w-[150px]"
        />

        <Button
          variant={filters.hasRiskFlags ? "default" : "outline"}
          onClick={() =>
            setFilters((prev) => ({
              ...prev,
              hasRiskFlags: !prev.hasRiskFlags,
            }))
          }
        >
          {filters.hasRiskFlags ? (
            <CheckCircle2 className="mr-2 h-4 w-4" />
          ) : (
            <AlertTriangle className="mr-2 h-4 w-4" />
          )}
          Risk Only
        </Button>
      </div>

      {/* Table and Explanation Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-[1fr_400px] gap-4">
        {/* Table */}
        <div className="rounded-lg border">
          <ScrollArea className="h-[600px]">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Type</TableHead>
                  <TableHead>Text</TableHead>
                  <TableHead>Page</TableHead>
                  <TableHead>Section</TableHead>
                  <TableHead>Risk</TableHead>
                  <TableHead>Confidence</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {clausesArray.map((clause) => (
                  <TableRow
                    key={clause.id}
                    className={cn(
                      "cursor-pointer hover:bg-muted/50 transition-colors",
                      selectedClause?.id === clause.id && "bg-muted"
                    )}
                    onClick={() => setSelectedClause(clause)}
                  >
                    <TableCell>
                      <div className="space-y-1">
                        <Badge variant="outline">{clause.clause_type}</Badge>
                        {clause.clause_subtype && (
                          <div className="text-xs text-muted-foreground">
                            {clause.clause_subtype}
                          </div>
                        )}
                      </div>
                    </TableCell>
                    <TableCell className="max-w-md">
                      <p className="text-sm line-clamp-3">
                        {clause.extracted_text}
                      </p>
                    </TableCell>
                    <TableCell>{clause.page_number}</TableCell>
                    <TableCell className="text-xs text-muted-foreground">
                      {clause.section}
                    </TableCell>
                    <TableCell>
                      <RiskBadge
                        riskScore={clause.risk_score}
                        riskFlags={clause.risk_flags}
                      />
                      {clause.risk_reasoning && (
                        <p className="text-xs text-muted-foreground mt-1 max-w-xs line-clamp-2">
                          {clause.risk_reasoning}
                        </p>
                      )}
                    </TableCell>
                    <TableCell>
                      <div className="text-sm">
                        {Math.round((clause.confidence_score || 0) * 100)}%
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </ScrollArea>
        </div>

        {/* Explanation Panel */}
        <div className="h-[600px] hidden lg:block">
          {selectedClause ? (
            <ClauseExplanationPanel
              clause={selectedClause}
              onClose={() => setSelectedClause(null)}
            />
          ) : (
            <div className="h-full rounded-lg border bg-muted/30 flex items-center justify-center">
              <div className="text-center p-6">
                <AlertTriangle className="h-12 w-12 text-muted-foreground mx-auto mb-4 opacity-50" />
                <p className="text-sm font-medium text-muted-foreground mb-1">
                  No clause selected
                </p>
                <p className="text-xs text-muted-foreground">
                  Click on a clause row to view detailed risk explanation
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Mobile Explanation Panel (shown below table on small screens) */}
      {selectedClause && (
        <div className="lg:hidden">
          <ClauseExplanationPanel
            clause={selectedClause}
            onClose={() => setSelectedClause(null)}
          />
        </div>
      )}
    </div>
  );
}

