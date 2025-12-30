"use client"

import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { type MatchingResult, reportsApi } from "@/lib/api"
import { AlertTriangle, CheckCircle2, XCircle, ArrowRight, Download, FileText } from "lucide-react"
import { useState } from "react"

interface ComparisonViewProps {
  result: MatchingResult
}

export function ComparisonView({ result }: ComparisonViewProps) {
  const [downloading, setDownloading] = useState<string | null>(null)

  const handleDownload = async (format: 'pdf' | 'json' | 'csv') => {
    setDownloading(format)
    try {
      let response
      if (format === 'pdf') {
        response = await reportsApi.downloadPDF(result.id)
      } else if (format === 'json') {
        response = await reportsApi.downloadJSON(result.id)
      } else {
        response = await reportsApi.downloadCSV(result.id)
      }

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `reconciliation-report-${result.id.slice(0, 8)}.${format}`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error(`Failed to download ${format} report:`, error)
      alert(`Failed to download ${format.toUpperCase()} report. Please try again.`)
    } finally {
      setDownloading(null)
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical":
        return "destructive" // Red
      case "high":
        return "destructive" // Red
      case "medium":
        return "warning" // Orange/Yellow
      case "low":
        return "outline" // Gray
      default:
        return "outline"
    }
  }

  const getSeverityBgColor = (severity: string) => {
    switch (severity) {
      case "critical":
        return "bg-red-50 border-red-200"
      case "high":
        return "bg-red-50 border-red-200"
      case "medium":
        return "bg-orange-50 border-orange-200"
      case "low":
        return "bg-gray-50 border-gray-200"
      default:
        return "bg-gray-50 border-gray-200"
    }
  }

  const getSeverityTextColor = (severity: string) => {
    switch (severity) {
      case "critical":
        return "text-red-700"
      case "high":
        return "text-red-700"
      case "medium":
        return "text-orange-700"
      case "low":
        return "text-gray-700"
      default:
        return "text-gray-700"
    }
  }

  const formatValue = (value: any): string => {
    if (value === null || value === undefined) return "—"
    if (typeof value === "object") {
      // Extract key fields from object
      const parts: string[] = []
      if (value.quantity !== undefined) parts.push(`Qty: ${value.quantity}`)
      if (value.unit_price !== undefined) parts.push(`Price: $${value.unit_price.toFixed(2)}`)
      if (value.line_total !== undefined) parts.push(`Total: $${value.line_total.toFixed(2)}`)
      if (value.description !== undefined) parts.push(value.description)
      if (value.item_number !== undefined) parts.push(`Item #${value.item_number}`)
      return parts.length > 0 ? parts.join(", ") : JSON.stringify(value)
    }
    return String(value)
  }

  const renderValueTable = (poValue: any, invoiceValue: any, type: string) => {
    const isExtraItem = !poValue && invoiceValue
    const isMissingItem = poValue && !invoiceValue
    
    if (isExtraItem || isMissingItem) {
      const value = isExtraItem ? invoiceValue : poValue
      return (
        <div className="overflow-x-auto">
          <table className="w-full text-xs border-collapse">
            <thead>
              <tr className="bg-[#FAFAFA]">
                <th className="border border-[#E5E5E5] px-2 py-1 text-left font-medium text-black">Field</th>
                <th className="border border-[#E5E5E5] px-2 py-1 text-left font-medium text-black">
                  {isExtraItem ? "Invoice" : "PO"}
                </th>
              </tr>
            </thead>
            <tbody>
              {value.item_number && (
                <tr>
                  <td className="border border-[#E5E5E5] px-2 py-1 text-[#404040]">Item Number</td>
                  <td className="border border-[#E5E5E5] px-2 py-1 text-black font-medium">{value.item_number}</td>
                </tr>
              )}
              {value.description && (
                <tr>
                  <td className="border border-[#E5E5E5] px-2 py-1 text-[#404040]">Description</td>
                  <td className="border border-[#E5E5E5] px-2 py-1 text-black">{value.description}</td>
                </tr>
              )}
              {value.quantity !== undefined && (
                <tr>
                  <td className="border border-[#E5E5E5] px-2 py-1 text-[#404040]">Quantity</td>
                  <td className="border border-[#E5E5E5] px-2 py-1 text-black">{value.quantity}</td>
                </tr>
              )}
              {value.unit_price !== undefined && (
                <tr>
                  <td className="border border-[#E5E5E5] px-2 py-1 text-[#404040]">Unit Price</td>
                  <td className="border border-[#E5E5E5] px-2 py-1 text-black">${value.unit_price.toFixed(2)}</td>
                </tr>
              )}
              {value.line_total !== undefined && (
                <tr>
                  <td className="border border-[#E5E5E5] px-2 py-1 text-[#404040]">Line Total</td>
                  <td className="border border-[#E5E5E5] px-2 py-1 text-black font-medium">${value.line_total.toFixed(2)}</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )
    }

    // Both values exist - show comparison table
    return (
      <div className="overflow-x-auto">
        <table className="w-full text-xs border-collapse">
          <thead>
            <tr className="bg-[#FAFAFA]">
              <th className="border border-[#E5E5E5] px-2 py-1 text-left font-medium text-black">Field</th>
              <th className="border border-[#E5E5E5] px-2 py-1 text-left font-medium text-black">PO</th>
              <th className="border border-[#E5E5E5] px-2 py-1 text-left font-medium text-black">Invoice</th>
              <th className="border border-[#E5E5E5] px-2 py-1 text-left font-medium text-black">Difference</th>
            </tr>
          </thead>
          <tbody>
            {poValue.quantity !== undefined || invoiceValue.quantity !== undefined ? (
              <tr>
                <td className="border border-[#E5E5E5] px-2 py-1 text-[#404040]">Quantity</td>
                <td className="border border-[#E5E5E5] px-2 py-1 text-black">{poValue.quantity ?? "—"}</td>
                <td className="border border-[#E5E5E5] px-2 py-1 text-black">{invoiceValue.quantity ?? "—"}</td>
                <td className="border border-[#E5E5E5] px-2 py-1 text-black">
                  {poValue.quantity !== undefined && invoiceValue.quantity !== undefined
                    ? (invoiceValue.quantity - poValue.quantity).toFixed(1)
                    : "—"}
                </td>
              </tr>
            ) : null}
            {poValue.unit_price !== undefined || invoiceValue.unit_price !== undefined ? (
              <tr>
                <td className="border border-[#E5E5E5] px-2 py-1 text-[#404040]">Unit Price</td>
                <td className="border border-[#E5E5E5] px-2 py-1 text-black">
                  {poValue.unit_price !== undefined ? `$${poValue.unit_price.toFixed(2)}` : "—"}
                </td>
                <td className="border border-[#E5E5E5] px-2 py-1 text-black">
                  {invoiceValue.unit_price !== undefined ? `$${invoiceValue.unit_price.toFixed(2)}` : "—"}
                </td>
                <td className="border border-[#E5E5E5] px-2 py-1 text-black">
                  {poValue.unit_price !== undefined && invoiceValue.unit_price !== undefined
                    ? `$${(invoiceValue.unit_price - poValue.unit_price).toFixed(2)}`
                    : "—"}
                </td>
              </tr>
            ) : null}
            {poValue.line_total !== undefined || invoiceValue.line_total !== undefined ? (
              <tr>
                <td className="border border-[#E5E5E5] px-2 py-1 text-[#404040]">Line Total</td>
                <td className="border border-[#E5E5E5] px-2 py-1 text-black">
                  {poValue.line_total !== undefined ? `$${poValue.line_total.toFixed(2)}` : "—"}
                </td>
                <td className="border border-[#E5E5E5] px-2 py-1 text-black">
                  {invoiceValue.line_total !== undefined ? `$${invoiceValue.line_total.toFixed(2)}` : "—"}
                </td>
                <td className="border border-[#E5E5E5] px-2 py-1 text-black font-medium">
                  {poValue.line_total !== undefined && invoiceValue.line_total !== undefined
                    ? `$${(invoiceValue.line_total - poValue.line_total).toFixed(2)}`
                    : "—"}
                </td>
              </tr>
            ) : null}
            {poValue.description !== undefined || invoiceValue.description !== undefined ? (
              <tr>
                <td className="border border-[#E5E5E5] px-2 py-1 text-[#404040]">Description</td>
                <td className="border border-[#E5E5E5] px-2 py-1 text-black">{poValue.description ?? "—"}</td>
                <td className="border border-[#E5E5E5] px-2 py-1 text-black">{invoiceValue.description ?? "—"}</td>
                <td className="border border-[#E5E5E5] px-2 py-1 text-black">—</td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
    )
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

  return (
    <div className="space-y-3">
      {/* Export Actions - Compact */}
      <div className="flex items-center justify-between p-3 bg-[#FAFAFA] rounded border border-[#E5E5E5]">
        <div className="text-xs font-medium text-black">Export Report</div>
        <div className="flex gap-1.5">
          <Button
            variant="outline"
            size="sm"
            className="h-7 text-xs"
            onClick={() => handleDownload('pdf')}
            disabled={downloading !== null}
          >
            <FileText className="mr-1 h-3 w-3" />
            {downloading === 'pdf' ? '...' : 'PDF'}
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="h-7 text-xs"
            onClick={() => handleDownload('json')}
            disabled={downloading !== null}
          >
            <Download className="mr-1 h-3 w-3" />
            {downloading === 'json' ? '...' : 'JSON'}
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="h-7 text-xs"
            onClick={() => handleDownload('csv')}
            disabled={downloading !== null}
          >
            <Download className="mr-1 h-3 w-3" />
            {downloading === 'csv' ? '...' : 'CSV'}
          </Button>
        </div>
      </div>

      {/* Match Confidence - Compact */}
      <div className="grid grid-cols-3 gap-2 p-3 bg-[#FAFAFA] rounded border border-[#E5E5E5]">
        <div>
          <div className="text-xs text-[#404040] mb-0.5">PO Match</div>
          <Badge variant="outline" className="text-xs">
            {result.match_confidence.po_number_match.toFixed(0)}%
          </Badge>
        </div>
        <div>
          <div className="text-xs text-[#404040] mb-0.5">Vendor Match</div>
          <Badge variant="outline" className="text-xs">
            {result.match_confidence.vendor_name_match.toFixed(0)}%
          </Badge>
        </div>
        <div>
          <div className="text-xs text-[#404040] mb-0.5">Overall</div>
          <Badge
            variant={
              result.match_confidence.overall >= 90
                ? "success"
                : result.match_confidence.overall >= 70
                ? "warning"
                : "destructive"
            }
            className="text-xs"
          >
            {result.match_confidence.overall.toFixed(0)}%
          </Badge>
        </div>
      </div>

      {/* Discrepancies - Compact */}
      {result.discrepancies.length > 0 && (
        <div className="border border-[#E5E5E5] bg-white rounded">
          <div className="p-3 border-b border-[#E5E5E5] bg-[#FAFAFA]">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-black">
                Discrepancies ({result.discrepancies.length})
              </h3>
              <Badge variant="destructive" className="text-xs">
                {result.discrepancies.filter((d) => d.severity === "critical" || d.severity === "high")
                  .length}{" "}
                Critical
              </Badge>
            </div>
          </div>

          <div className="p-3 space-y-3">
              {result.discrepancies.map((disc, idx) => (
                <div
                  key={idx}
                  className={`border rounded p-3 ${getSeverityBgColor(disc.severity)}`}
                >
                  <div className="flex items-start gap-2 mb-2">
                    <div className={`mt-0.5 ${getSeverityTextColor(disc.severity)}`}>
                      {getDiscrepancyIcon(disc.type)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-1.5 mb-1.5 flex-wrap">
                        <Badge
                          variant={getSeverityColor(disc.severity) as any}
                          className="text-xs"
                        >
                          {disc.severity.toUpperCase()}
                        </Badge>
                        <span className={`text-xs font-medium ${getSeverityTextColor(disc.severity)}`}>
                          {disc.type.replace(/_/g, " ").toUpperCase()}
                        </span>
                      </div>
                      
                      {disc.item_number && (
                        <div className="text-xs font-semibold text-black mb-0.5">
                          Item #{disc.item_number}
                        </div>
                      )}
                      
                      {disc.description && (
                        <div className="text-sm font-medium text-black mb-1">{disc.description}</div>
                      )}
                      
                      <div className="text-xs text-[#404040] mb-2">{disc.message}</div>

                      {/* Value Comparison Table */}
                      {(disc.po_value || disc.invoice_value) && (
                        <div className="mt-2 pt-2 border-t border-[#E5E5E5]">
                          {renderValueTable(disc.po_value, disc.invoice_value, disc.type)}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Perfect Match Message - Compact */}
      {result.discrepancies.length === 0 && (
        <div className="border border-[#16A34A] bg-[#F0FDF4] rounded p-2.5 flex items-center gap-2">
          <CheckCircle2 className="h-4 w-4 text-[#16A34A] flex-shrink-0" />
          <div>
            <div className="text-xs font-medium text-black">Perfect Match!</div>
            <div className="text-xs text-[#404040]">
              All items match. No discrepancies found.
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

