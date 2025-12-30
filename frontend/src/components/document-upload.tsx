"use client"

import { useState, useCallback, useRef } from "react"
import { Upload, File, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { documentsApi } from "@/lib/api"

interface DocumentUploadProps {
  workspaceId: string
  onUploadComplete: () => void
}

export function DocumentUpload({ workspaceId, onUploadComplete }: DocumentUploadProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const [documentType, setDocumentType] = useState<'purchase_order' | 'invoice' | 'delivery_note'>('invoice')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const files = Array.from(e.dataTransfer.files)
    setSelectedFiles(files)
  }, [])

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setSelectedFiles(Array.from(e.target.files))
    }
  }

  const detectDocumentType = (filename: string): 'purchase_order' | 'invoice' | 'delivery_note' => {
    const lower = filename.toLowerCase()
    // Check for PO patterns first
    if (lower.includes('po-') || lower.includes('purchase-order') || lower.includes('purchase_order') || 
        lower.startsWith('po') || lower.includes(' purchase order')) {
      return 'purchase_order'
    }
    // Check for Delivery Note patterns
    if (lower.includes('delivery-note') || lower.includes('delivery_note') || lower.includes('dn-') ||
        lower.startsWith('delivery') || lower.includes(' delivery note')) {
      return 'delivery_note'
    }
    // Check for Invoice patterns
    if (lower.includes('invoice') || lower.includes('inv-') || lower.startsWith('inv')) {
      return 'invoice'
    }
    // Default to selected type if can't detect
    return documentType
  }

  const handleUpload = async () => {
    if (selectedFiles.length === 0) return

    setUploading(true)
    try {
      for (const file of selectedFiles) {
        // Always auto-detect document type from filename
        const detectedType = detectDocumentType(file.name)
        const typeToUse = detectedType
        
        console.log(`Uploading ${file.name} as ${typeToUse} (detected from filename)`)
        await documentsApi.upload(workspaceId, typeToUse, file)
      }
      setSelectedFiles([])
      onUploadComplete()
      // Refresh after a delay to see processing status
      setTimeout(() => {
        onUploadComplete()
      }, 3000)
    } catch (error: any) {
      console.error("Upload failed:", error)
      const errorMsg = error.response?.data?.detail || error.message || "Upload failed. Please try again."
      alert(`Upload failed: ${errorMsg}`)
    } finally {
      setUploading(false)
    }
  }

  const removeFile = (index: number) => {
    setSelectedFiles(selectedFiles.filter((_, i) => i !== index))
  }

  const handleSelectFilesClick = () => {
    fileInputRef.current?.click()
  }

  return (
    <Card className="border border-[#E5E5E5] bg-white">
      <div className="p-6">
        <div className="mb-4">
          <label className="mb-2 block text-sm font-medium text-black">Document Type</label>
          <select
            value={documentType}
            onChange={(e) => setDocumentType(e.target.value as any)}
            className="w-full rounded-md border border-[#E5E5E5] bg-white px-3 py-2 text-sm text-black focus:outline-none focus:ring-2 focus:ring-black focus:border-black"
          >
            <option value="purchase_order">Purchase Order</option>
            <option value="invoice">Invoice</option>
            <option value="delivery_note">Delivery Note</option>
          </select>
        </div>

        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`rounded-md border-2 border-dashed p-12 text-center transition-colors ${
            isDragging
              ? "border-black bg-[#FAFAFA]"
              : "border-[#E5E5E5] bg-white"
          }`}
        >
          <Upload className="mx-auto h-10 w-10 text-[#404040]" />
          <p className="mt-4 text-sm font-medium text-black">
            Drop files here or click to browse
          </p>
          <p className="mt-1.5 text-xs text-[#404040]">
            Supports: PDF, DOCX (Max 100 pages)
          </p>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf,.docx"
            onChange={handleFileSelect}
            className="hidden"
            id="file-upload"
          />
          <Button
            variant="outline"
            className="mt-4 h-9"
            onClick={handleSelectFilesClick}
            type="button"
          >
            <span className="text-sm">Select Files</span>
          </Button>
        </div>
      </div>

      {selectedFiles.length > 0 && (
        <div className="border-t border-[#E5E5E5] p-6 pt-4">
          <p className="mb-3 text-sm font-medium text-black">Selected Files:</p>
          <div className="space-y-2">
            {selectedFiles.map((file, index) => {
              const detectedType = detectDocumentType(file.name)
              const typeLabels = {
                purchase_order: 'PO',
                invoice: 'Invoice',
                delivery_note: 'Delivery Note'
              }
              return (
              <div
                key={index}
                className="flex items-center justify-between rounded-md border border-[#E5E5E5] bg-white p-3"
              >
                <div className="flex items-center gap-2.5">
                  <File className="h-4 w-4 text-[#404040]" />
                  <div className="flex flex-col">
                    <span className="text-sm text-black">{file.name}</span>
                    <span className="text-xs text-[#404040]">
                      Detected as: {typeLabels[detectedType]} • ({(file.size / 1024 / 1024).toFixed(2)} MB)
                    </span>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => removeFile(index)}
                  className="h-7 w-7"
                >
                  <X className="h-3.5 w-3.5" />
                </Button>
              </div>
            )})}
          </div>
          <Button
            onClick={handleUpload}
            disabled={uploading}
            className="mt-4 w-full h-9"
          >
            {uploading ? "Uploading..." : `Upload ${selectedFiles.length} File(s)`}
          </Button>
        </div>
      )}
    </Card>
  )
}

