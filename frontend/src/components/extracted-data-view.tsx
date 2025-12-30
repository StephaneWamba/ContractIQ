"use client"

import { useEffect, useState } from "react"
import { Badge } from "@/components/ui/badge"
import { documentsApi, type ExtractedData } from "@/lib/api"
import { FileText, Calendar, DollarSign, Building2, Hash } from "lucide-react"

interface ExtractedDataViewProps {
  documentId: string
}

export function ExtractedDataView({ documentId }: ExtractedDataViewProps) {
  const [data, setData] = useState<ExtractedData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadExtractedData()
  }, [documentId])

  const loadExtractedData = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await documentsApi.getExtracted(documentId)
      setData(response.data)
    } catch (err: any) {
      console.error("Failed to load extracted data:", err)
      setError(err.response?.data?.detail || "Failed to load extracted data")
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="border border-[#E5E5E5] bg-white rounded">
        <div className="p-4 text-center text-xs text-[#404040]">Loading extracted data...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="border border-[#E5E5E5] bg-white rounded">
        <div className="p-4 text-center text-xs text-destructive">{error}</div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="border border-[#E5E5E5] bg-white rounded">
        <div className="p-4 text-center text-xs text-[#404040]">No extracted data available</div>
      </div>
    )
  }

  const getConfidenceColor = (score: number) => {
    if (score >= 0.9) return "success"
    if (score >= 0.7) return "warning"
    return "destructive"
  }

  return (
    <div className="space-y-4">
      {/* Header Fields - Compact */}
      <div className="border border-[#E5E5E5] bg-white rounded">
        <div className="p-3">
          <h3 className="text-sm font-semibold text-black mb-3">Extracted Information</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
            {data.po_number && (
              <div className="flex items-start gap-3">
                <Hash className="h-4 w-4 mt-0.5 text-[#404040]" />
                <div className="flex-1">
                  <div className="text-xs text-[#404040] mb-0.5">PO Number</div>
                  <div className="text-sm font-medium text-black">{data.po_number}</div>
                </div>
              </div>
            )}

            {data.invoice_number && (
              <div className="flex items-start gap-3">
                <Hash className="h-4 w-4 mt-0.5 text-[#404040]" />
                <div className="flex-1">
                  <div className="text-xs text-[#404040] mb-0.5">Invoice Number</div>
                  <div className="text-sm font-medium text-black">{data.invoice_number}</div>
                </div>
              </div>
            )}

            {data.delivery_note_number && (
              <div className="flex items-start gap-3">
                <Hash className="h-4 w-4 mt-0.5 text-[#404040]" />
                <div className="flex-1">
                  <div className="text-xs text-[#404040] mb-0.5">Delivery Note Number</div>
                  <div className="text-sm font-medium text-black">{data.delivery_note_number}</div>
                </div>
              </div>
            )}

            {data.vendor_name && (
              <div className="flex items-start gap-3">
                <Building2 className="h-4 w-4 mt-0.5 text-[#404040]" />
                <div className="flex-1">
                  <div className="text-xs text-[#404040] mb-0.5">Vendor Name</div>
                  <div className="text-sm font-medium text-black">{data.vendor_name}</div>
                </div>
              </div>
            )}

            {data.date && (
              <div className="flex items-start gap-3">
                <Calendar className="h-4 w-4 mt-0.5 text-[#404040]" />
                <div className="flex-1">
                  <div className="text-xs text-[#404040] mb-0.5">Date</div>
                  <div className="text-sm font-medium text-black">{data.date}</div>
                </div>
              </div>
            )}

            {data.total_amount !== null && (
              <div className="flex items-start gap-3">
                <DollarSign className="h-4 w-4 mt-0.5 text-[#404040]" />
                <div className="flex-1">
                  <div className="text-xs text-[#404040] mb-0.5">Total Amount</div>
                  <div className="text-sm font-medium text-black">
                    {data.currency_code ? `${data.currency_code} ` : "$"}
                    {data.total_amount.toFixed(2)}
                  </div>
                </div>
              </div>
            )}

            {data.subtotal !== null && (
              <div className="flex items-start gap-3">
                <DollarSign className="h-4 w-4 mt-0.5 text-[#404040]" />
                <div className="flex-1">
                  <div className="text-xs text-[#404040] mb-0.5">Subtotal</div>
                  <div className="text-sm font-medium text-black">
                    {data.currency_code ? `${data.currency_code} ` : "$"}
                    {data.subtotal.toFixed(2)}
                  </div>
                </div>
              </div>
            )}

            {data.tax_amount !== null && (
              <div className="flex items-start gap-3">
                <DollarSign className="h-4 w-4 mt-0.5 text-[#404040]" />
                <div className="flex-1">
                  <div className="text-xs text-[#404040] mb-0.5">
                    Tax {data.tax_rate !== null ? `(${data.tax_rate.toFixed(2)}%)` : ""}
                  </div>
                  <div className="text-sm font-medium text-black">
                    {data.currency_code ? `${data.currency_code} ` : "$"}
                    {data.tax_amount.toFixed(2)}
                  </div>
                </div>
              </div>
            )}

            {data.due_date && (
              <div className="flex items-start gap-3">
                <Calendar className="h-4 w-4 mt-0.5 text-[#404040]" />
                <div className="flex-1">
                  <div className="text-xs text-[#404040] mb-0.5">Due Date</div>
                  <div className="text-sm font-medium text-black">{data.due_date}</div>
                </div>
              </div>
            )}

            {data.currency_code && (
              <div className="flex items-start gap-3">
                <DollarSign className="h-4 w-4 mt-0.5 text-[#404040]" />
                <div className="flex-1">
                  <div className="text-xs text-[#404040] mb-0.5">Currency</div>
                  <div className="text-sm font-medium text-black">{data.currency_code}</div>
                </div>
              </div>
            )}

            {data.vendor_address && (
              <div className="flex items-start gap-3 md:col-span-2">
                <Building2 className="h-4 w-4 mt-0.5 text-[#404040]" />
                <div className="flex-1">
                  <div className="text-xs text-[#404040] mb-0.5">Vendor Address</div>
                  <div className="text-sm text-black whitespace-pre-line">{data.vendor_address}</div>
                </div>
              </div>
            )}
          </div>

          {/* Extraction Metadata */}
          <div className="mt-3 pt-3 border-t border-[#E5E5E5] md:col-span-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-[#404040]">Extraction Model:</span>
              <span className="text-black font-medium">{data.extraction_model}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Line Items - Compact */}
      {data.line_items && data.line_items.length > 0 && (
        <div className="border border-[#E5E5E5] bg-white rounded">
          <div className="p-3">
            <h3 className="text-sm font-semibold text-black mb-3">Line Items</h3>
            
            <div className="overflow-x-auto">
              <table className="w-full border-collapse text-xs">
                <thead>
                  <tr className="border-b border-[#E5E5E5] bg-[#FAFAFA]">
                    <th className="text-left p-2 text-xs font-medium text-[#404040]">Item #</th>
                    <th className="text-left p-2 text-xs font-medium text-[#404040]">Description</th>
                    <th className="text-right p-2 text-xs font-medium text-[#404040]">Qty</th>
                    <th className="text-right p-2 text-xs font-medium text-[#404040]">Price</th>
                    <th className="text-right p-2 text-xs font-medium text-[#404040]">Total</th>
                  </tr>
                </thead>
                <tbody>
                  {data.line_items.map((item, idx) => (
                    <tr key={idx} className="border-b border-[#E5E5E5]">
                      <td className="p-2 text-xs text-black">{item.item_number || "-"}</td>
                      <td className="p-2 text-xs text-black">{item.description || "-"}</td>
                      <td className="p-2 text-xs text-black text-right">
                        {item.quantity !== null ? item.quantity.toFixed(2) : "-"}
                      </td>
                      <td className="p-2 text-xs text-black text-right">
                        {item.unit_price !== null ? `$${item.unit_price.toFixed(2)}` : "-"}
                      </td>
                      <td className="p-2 text-xs font-medium text-black text-right">
                        {item.line_total !== null ? `$${item.line_total.toFixed(2)}` : "-"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Confidence Scores - Compact */}
      {data.confidence_scores && Object.keys(data.confidence_scores).length > 0 && (
        <div className="border border-[#E5E5E5] bg-white rounded">
          <div className="p-3">
            <h3 className="text-sm font-semibold text-black mb-3">Extraction Confidence</h3>
            
            <div className="space-y-1.5">
              {Object.entries(data.confidence_scores).map(([field, score]) => (
                <div key={field} className="flex items-center justify-between">
                  <span className="text-sm text-[#404040] capitalize">
                    {field.replace(/_/g, " ")}
                  </span>
                  <div className="flex items-center gap-2">
                    <div className="w-32 h-2 bg-[#E5E5E5] rounded-full overflow-hidden">
                      <div
                        className={`h-full ${
                          score >= 0.9
                            ? "bg-[#16A34A]"
                            : score >= 0.7
                            ? "bg-[#D97706]"
                            : "bg-destructive"
                        }`}
                        style={{ width: `${score * 100}%` }}
                      />
                    </div>
                    <Badge
                      variant={getConfidenceColor(score) as any}
                      className="text-xs w-12 justify-center"
                    >
                      {(score * 100).toFixed(0)}%
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

