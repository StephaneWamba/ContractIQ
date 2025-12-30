"use client"

import { useEffect, useState } from "react"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { matchingApi, type MatchingResult } from "@/lib/api"
import { ChevronDown, ChevronUp } from "lucide-react"
import { ComparisonView } from "./comparison-view"

interface MatchingResultsProps {
  workspaceId: string
  refreshKey?: number
}

export function MatchingResults({ workspaceId, refreshKey }: MatchingResultsProps) {
  const [results, setResults] = useState<MatchingResult[]>([])
  const [loading, setLoading] = useState(true)
  const [expandedResultId, setExpandedResultId] = useState<string | null>(null)

  useEffect(() => {
    loadResults()
  }, [workspaceId, refreshKey])

  const loadResults = async () => {
    try {
      setLoading(true)
      const response = await matchingApi.getResults(workspaceId)
      setResults(response.data || [])
    } catch (error: any) {
      console.error("Failed to load matching results:", error)
      // Don't show error if it's just that there are no results yet
      if (error.response?.status !== 404) {
        console.error("Error details:", error.response?.data || error.message)
      }
      setResults([])
    } finally {
      setLoading(false)
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical":
        return "destructive"
      case "high":
        return "destructive"
      case "medium":
        return "warning"
      case "low":
        return "outline"
      default:
        return "outline"
    }
  }

  const getDiscrepancyIcon = (type: string) => {
    switch (type) {
      case "quantity_mismatch":
      case "price_change":
        return <AlertTriangle className="h-4 w-4" />
      case "missing_item":
      case "extra_item":
        return <XCircle className="h-4 w-4" />
      default:
        return <AlertTriangle className="h-4 w-4" />
    }
  }

  if (loading) {
    return <div className="text-center py-12 text-[#404040]">Loading results...</div>
  }

  if (results.length === 0 && !loading) {
    return (
      <Card className="border border-[#E5E5E5] bg-white">
        <div className="p-12 text-center">
          <p className="text-[#404040] mb-2">No matching results yet.</p>
          <p className="text-sm text-[#404040]">
            Click "Run Matching" to match your documents. Make sure you have uploaded at least a PO and Invoice.
          </p>
        </div>
      </Card>
    )
  }

  return (
    <div className="space-y-3">
      {results.map((result) => {
        const criticalCount = result.discrepancies.filter(
          (d) => d.severity === "critical" || d.severity === "high"
        ).length
        const totalDiff = parseFloat(result.total_difference)
        const isPerfect = result.discrepancies.length === 0 && totalDiff === 0

        return (
          <Card key={result.id} className="border border-[#E5E5E5] bg-white">
            <div className="p-4">
              {/* Header Row - Compact */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div>
                    <h3 className="text-sm font-semibold text-black">
                      {result.matched_by === "po_number" ? "PO Match" : "Vendor Match"}
                    </h3>
                    {result.match_confidence?.vendor_name && (
                      <p className="text-xs text-[#666] mt-0.5">
                        {result.match_confidence.vendor_name}
                      </p>
                    )}
                  </div>
                  <Badge
                    variant={
                      isPerfect
                        ? "success"
                        : criticalCount > 0
                        ? "destructive"
                        : result.discrepancies.length > 0
                        ? "warning"
                        : "outline"
                    }
                    className="text-xs"
                  >
                    {isPerfect
                      ? "Perfect"
                      : criticalCount > 0
                      ? `${criticalCount} Critical`
                      : result.discrepancies.length > 0
                      ? `${result.discrepancies.length} Issues`
                      : "Matched"}
                  </Badge>
                  {result.discrepancies.length > 0 && (
                    <Badge variant="outline" className="text-xs">
                      {result.discrepancies.length} discrepancies
                    </Badge>
                  )}
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-7 text-xs"
                  onClick={() =>
                    setExpandedResultId(expandedResultId === result.id ? null : result.id)
                  }
                >
                  {expandedResultId === result.id ? "Hide Details" : "View Details"}
                  {expandedResultId === result.id ? (
                    <ChevronUp className="ml-1 h-3 w-3" />
                  ) : (
                    <ChevronDown className="ml-1 h-3 w-3" />
                  )}
                </Button>
              </div>

              {/* Inline Summary - Key Info Visible */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
                <div className="bg-[#FAFAFA] rounded p-2">
                  <div className="text-xs text-[#404040] mb-0.5">PO Total</div>
                  <div className="text-sm font-semibold text-black">
                    ${parseFloat(result.total_po_amount).toFixed(2)}
                  </div>
                </div>
                <div className="bg-[#FAFAFA] rounded p-2">
                  <div className="text-xs text-[#404040] mb-0.5">Invoice Total</div>
                  <div className="text-sm font-semibold text-black">
                    ${parseFloat(result.total_invoice_amount).toFixed(2)}
                  </div>
                </div>
                <div className="bg-[#FAFAFA] rounded p-2">
                  <div className="text-xs text-[#404040] mb-0.5">Difference</div>
                  <div
                    className={`text-sm font-semibold ${
                      totalDiff === 0 ? "text-[#16A34A]" : "text-destructive"
                    }`}
                  >
                    {totalDiff === 0 ? "$0.00" : `$${Math.abs(totalDiff).toFixed(2)}`}
                  </div>
                </div>
                <div className="bg-[#FAFAFA] rounded p-2">
                  <div className="text-xs text-[#404040] mb-0.5">Confidence</div>
                  <div className="text-sm font-semibold text-black">
                    {result.match_confidence.overall.toFixed(0)}%
                  </div>
                </div>
              </div>

              {/* Documents Badges - Compact */}
              <div className="flex items-center gap-2 text-xs text-[#404040]">
                <span>Documents:</span>
                {result.po_document_id && (
                  <Badge variant="outline" className="text-xs border-[#E5E5E5] text-black">
                    PO
                  </Badge>
                )}
                {result.invoice_document_id && (
                  <Badge variant="outline" className="text-xs border-[#E5E5E5] text-black">
                    Invoice
                  </Badge>
                )}
                {result.delivery_note_document_id && (
                  <Badge variant="outline" className="text-xs border-[#E5E5E5] text-black">
                    DN
                  </Badge>
                )}
              </div>

              {/* Expanded Detailed View */}
              {expandedResultId === result.id && (
                <div className="border-t border-[#E5E5E5] pt-4 mt-4">
                  <ComparisonView result={result} />
                </div>
              )}
            </div>
          </Card>
        )
      })}
    </div>
  )
}

