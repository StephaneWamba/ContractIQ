"use client"

import { useEffect, useState } from "react"
import { FileText, Download, Trash2, CheckCircle2, Clock, XCircle, Eye } from "lucide-react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { documentsApi, type Document } from "@/lib/api"
import { ExtractedDataView } from "./extracted-data-view"

interface DocumentListProps {
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

export function DocumentList({ workspaceId, onRefresh }: DocumentListProps) {
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [viewingDocumentId, setViewingDocumentId] = useState<string | null>(null)

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
        return <Badge variant="success">✓ Processed</Badge>
      case "PROCESSING":
        return <Badge variant="warning">⏳ Processing</Badge>
      case "FAILED":
        return <Badge variant="destructive">✗ Failed</Badge>
      default:
        return <Badge variant="outline">Uploaded</Badge>
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

  if (loading) {
    return <div className="text-center py-12 text-[#404040]">Loading documents...</div>
  }

  if (documents.length === 0) {
    return (
      <Card className="border border-[#E5E5E5] bg-white">
        <div className="p-12 text-center text-[#404040]">
          No documents uploaded yet. Upload documents to get started.
        </div>
      </Card>
    )
  }

  return (
    <div className="space-y-3">
      {documents.map((doc) => (
        <Card key={doc.id} className="border border-[#E5E5E5] bg-white">
          <div className="p-5">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-3">
                  <span className="text-xl">
                    {documentTypeIcons[doc.document_type as keyof typeof documentTypeIcons]}
                  </span>
                  <div>
                    <h3 className="text-sm font-semibold text-black">
                      {documentTypeLabels[doc.document_type as keyof typeof documentTypeLabels]}
                    </h3>
                    <p className="text-sm text-[#404040] mt-0.5">{doc.file_name}</p>
                  </div>
                </div>
                <div className="flex items-center gap-6 mt-4">
                  <div>
                    <span className="text-xs text-[#404040]">Status:</span>
                    <div className="mt-1.5">{getStatusBadge(doc.status)}</div>
                  </div>
                  {doc.page_count && (
                    <div>
                      <span className="text-xs text-[#404040]">Pages:</span>
                      <div className="mt-1.5 text-sm font-medium text-black">{doc.page_count}</div>
                    </div>
                  )}
                </div>
              </div>
              <div className="flex items-center gap-1.5">
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-8 text-black hover:bg-[#FAFAFA]"
                  onClick={() => setViewingDocumentId(viewingDocumentId === doc.id ? null : doc.id)}
                >
                  <Eye className="mr-1.5 h-3.5 w-3.5" />
                  {viewingDocumentId === doc.id ? "Hide" : "View"}
                </Button>
                <Button variant="ghost" size="icon" className="h-8 w-8 text-black hover:bg-[#FAFAFA]">
                  <Download className="h-3.5 w-3.5" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => handleDelete(doc.id)}
                  className="h-8 w-8 text-[#404040] hover:text-destructive hover:bg-[#FAFAFA]"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </Button>
              </div>
            </div>
          </div>
          
          {viewingDocumentId === doc.id && doc.status === "PROCESSED" && (
            <div className="border-t border-[#E5E5E5] p-5 bg-[#FAFAFA]">
              <ExtractedDataView documentId={doc.id} />
            </div>
          )}
        </Card>
      ))}
    </div>
  )
}

