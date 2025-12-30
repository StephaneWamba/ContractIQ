"use client";

import { useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Search, Eye } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { ClauseDetailDialog } from "./ClauseDetailDialog";
import { getRiskLevel, getRiskColor, truncate } from "@/lib/utils";
import type { Clause } from "@/lib/types";

interface ClausesTabProps {
  clauses: Clause[];
  isLoading: boolean;
  documentId: string;
}

export function ClausesTab({
  clauses,
  isLoading,
  documentId,
}: ClausesTabProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedClause, setSelectedClause] = useState<Clause | null>(null);
  const [typeFilter, setTypeFilter] = useState<string>("all");

  const clauseTypes = Array.from(new Set(clauses.map((c) => c.clause_type)));

  const filteredClauses = clauses.filter((clause) => {
    const matchesSearch =
      clause.extracted_text.toLowerCase().includes(searchQuery.toLowerCase()) ||
      clause.clause_type.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = typeFilter === "all" || clause.clause_type === typeFilter;
    return matchesSearch && matchesType;
  });

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search clauses..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className="h-10 rounded-md border border-input bg-background px-3 text-sm"
        >
          <option value="all">All Types</option>
          {clauseTypes.map((type) => (
            <option key={type} value={type}>
              {type}
            </option>
          ))}
        </select>
      </div>

      <div className="border rounded-lg">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Type</TableHead>
              <TableHead>Text</TableHead>
              <TableHead>Page</TableHead>
              <TableHead>Section</TableHead>
              <TableHead>Risk</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredClauses.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="text-center py-8 text-muted-foreground">
                  No clauses found
                </TableCell>
              </TableRow>
            ) : (
              filteredClauses.map((clause) => {
                const riskLevel = getRiskLevel(clause.risk_flags);
                return (
                  <TableRow key={clause.id}>
                    <TableCell className="font-medium">
                      {clause.clause_type}
                    </TableCell>
                    <TableCell className="max-w-md">
                      {truncate(clause.extracted_text, 100)}
                    </TableCell>
                    <TableCell>{clause.page_number}</TableCell>
                    <TableCell>{clause.section || "-"}</TableCell>
                    <TableCell>
                      {riskLevel && (
                        <Badge
                          variant="outline"
                          className={getRiskColor(riskLevel)}
                        >
                          {riskLevel.toUpperCase()}
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setSelectedClause(clause)}
                      >
                        <Eye className="h-4 w-4 mr-2" />
                        View
                      </Button>
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </div>

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


