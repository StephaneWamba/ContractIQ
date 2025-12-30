"use client"

import { useEffect, useState } from "react"
import { Download, Trash2, Eye, ChevronDown, ChevronUp } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { documentsApi, type Document } from "@/lib/api"
import { ExtractedDataView } from "./extracted-data-view"

interface DocumentTableProps {
  workspaceId: string
  onRefresh?: () => void
}

const documentTypeIcons = {
  purchase_order: "📋",
  invoice: "🧾",
  delivery_note: "📦",
}

const documentTypeLabels = {
  purchase_order: "Purchase Order",
  invoice: "Invoice",
  delivery_note: "Delivery Note",
}

export function DocumentTable({ workspaceId, onRefresh }: DocumentTableProps) {
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set())

  useEffect(() => {
    loadDocuments()
  }, [workspaceId])

  // Only poll when there are documents that are still processing
  useEffect(() => {
    const hasProcessing = documents.some(doc => doc.status === "PROCESSING" || doc.status === "UPLOADED")
    if (!hasProcessing) return

    // Poll every 5 seconds only if there are processing documents
    const interval = setInterval(() => {
      loadDocuments()
    }, 5000)
    return () => clearInterval(interval)
  }, [documents, workspaceId])

  const loadDocuments = async () => {
    try {
      setLoading(true)
      const response = await documentsApi.list(workspaceId)
      setDocuments(response.data)
    } catch (error) {
      console.error("Failed to load documents:", error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "PROCESSED":
        return <Badge variant="success" className="text-xs">Processed</Badge>
      case "PROCESSING":
        return <Badge variant="warning" className="text-xs">Processing</Badge>
      case "FAILED":
        return <Badge variant="destructive" className="text-xs">Failed</Badge>
      default:
        return <Badge variant="outline" className="text-xs">Uploaded</Badge>
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this document?")) return
    try {
      await documentsApi.delete(id)
      loadDocuments()
      onRefresh?.()
    } catch (error) {
      console.error("Failed to delete document:", error)
    }
  }

  const toggleRow = (docId: string) => {
    const newExpanded = new Set(expandedRows)
    if (newExpanded.has(docId)) {
      newExpanded.delete(docId)
    } else {
      newExpanded.add(docId)
    }
    setExpandedRows(newExpanded)
  }

  if (loading && documents.length === 0) {
    return <div className="text-center py-12 text-[#404040]">Loading documents...</div>
  }

  if (documents.length === 0) {
    return (
      <div className="border border-[#E5E5E5] bg-white rounded-md">
        <div className="p-12 text-center text-[#404040]">
          No documents uploaded yet. Upload documents to get started.
        </div>
      </div>
    )
  }

  return (
    <div className="border border-[#E5E5E5] bg-white rounded-md overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr className="border-b border-[#E5E5E5] bg-[#FAFAFA]">
              <th className="text-left p-2 text-xs font-medium text-[#404040] w-8"></th>
              <th className="text-left p-2 text-xs font-medium text-[#404040]">Type</th>
              <th className="text-left p-2 text-xs font-medium text-[#404040]">File Name</th>
              <th className="text-center p-2 text-xs font-medium text-[#404040]">Status</th>
              <th className="text-center p-2 text-xs font-medium text-[#404040]">Pages</th>
              <th className="text-right p-2 text-xs font-medium text-[#404040]">Actions</th>
            </tr>
          </thead>
          <tbody>
            {documents.map((doc) => {
              const isExpanded = expandedRows.has(doc.id)
              return (
                <>
                  <tr
                    key={doc.id}
                    className="border-b border-[#E5E5E5] hover:bg-[#FAFAFA] transition-colors"
                  >
                    <td className="p-2">
                      {doc.status === "PROCESSED" && (
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-5 w-5"
                          onClick={() => toggleRow(doc.id)}
                        >
                          {isExpanded ? (
                            <ChevronUp className="h-3 w-3" />
                          ) : (
                            <ChevronDown className="h-3 w-3" />
                          )}
                        </Button>
                      )}
                    </td>
                    <td className="p-2">
                      <div className="flex items-center gap-1.5">
                        <span className="text-sm">
                          {documentTypeIcons[doc.document_type as keyof typeof documentTypeIcons]}
                        </span>
                        <span className="text-xs text-black">
                          {documentTypeLabels[doc.document_type as keyof typeof documentTypeLabels]}
                        </span>
                      </div>
                    </td>
                    <td className="p-2">
                      <span className="text-xs text-black truncate block max-w-xs">{doc.file_name}</span>
                    </td>
                    <td className="p-2 text-center">
                      {getStatusBadge(doc.status)}
                    </td>
                    <td className="p-2 text-center">
                      <span className="text-xs text-black">{doc.page_count || "-"}</span>
                    </td>
                    <td className="p-2">
                      <div className="flex items-center justify-end gap-0.5">
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-6 w-6"
                          onClick={() => toggleRow(doc.id)}
                          disabled={doc.status !== "PROCESSED"}
                        >
                          <Eye className="h-3 w-3" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-6 w-6"
                        >
                          <Download className="h-3 w-3" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleDelete(doc.id)}
                          className="h-6 w-6 text-[#404040] hover:text-destructive"
                        >
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                  {isExpanded && doc.status === "PROCESSED" && (
                    <tr>
                      <td colSpan={6} className="p-0 bg-[#FAFAFA]">
                        <div className="p-3">
                          <ExtractedDataView documentId={doc.id} />
                        </div>
                      </td>
                    </tr>
                  )}
                </>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}

